# coding=utf-8
import json
from datetime import timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import CallToolResult
from openai.types.chat import ChatCompletionToolParam

from mcp_demo.common.MCPCommon import MCPClientBase, QuestionRequest, get_logger, sse_server_1_url, ConnectionManager, ToolExecutionData, html_format

logger = get_logger(__file__)

app = FastAPI()

connection_manager = ConnectionManager()


async def query_mcp_server(question: str, parallel: bool):
    async with sse_client(url=sse_server_1_url, timeout=60, sse_read_timeout=60 * 5) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
            # Initialize the connection
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            logger.info(f"MCP Server Tools {tools}")
            available_tools = []
            for tool in tools.tools:
                tool_param: ChatCompletionToolParam = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                available_tools.append(tool_param)

            messages = [{
                "role": "system",
                "content": "仅使用role=tool相关数据进行分析，不使用模型中的数据"
            }, {
                "role": "user",
                "content": f"要求：每次返回选择工具时，在choices.message.content返回选择工具的原因\n任务：{question}"
            }]

            seq = 0
            while True:
                seq += 1
                response = MCPClientBase.client.chat.completions.create(
                    model=MCPClientBase.model,
                    messages=messages,
                    tools=available_tools,
                    parallel_tool_calls=parallel
                )

                assistant_output = response.choices[0].message
                if assistant_output.content is None:
                    assistant_output.content = ""

                if response.choices[0].finish_reason != "tool_calls" \
                        or assistant_output.tool_calls is None \
                        or len(assistant_output.tool_calls) == 0:
                    logger.info(f"获得结果：{assistant_output.content}")
                    return assistant_output.content

                messages.append(assistant_output)

                tool_seq = 0
                for tool_call in assistant_output.tool_calls:
                    tool_seq += 1
                    function = tool_call.function
                    tool_name = function.name
                    # 调用 MCP server 对应工具
                    mcp_server_result: CallToolResult = await session.call_tool(tool_name, json.loads(function.arguments))
                    if mcp_server_result.isError:
                        toolExecutionData = ToolExecutionData(seq, tool_seq, tool_name, assistant_output.content, function.arguments, None)
                        logger.error(f"{toolExecutionData}")
                        await connection_manager.send_ws_message(toolExecutionData.to_dict(True))
                        raise ValueError(f"调用MCP server tool {tool_name} 返回失败")

                    toolExecutionData = ToolExecutionData(seq, tool_seq, tool_name, assistant_output.content, function.arguments, mcp_server_result.content)
                    logger.info(f"{toolExecutionData}")
                    await connection_manager.send_ws_message(toolExecutionData.to_dict(True))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": mcp_server_result.content
                    })
                    if not parallel:
                        break


@app.post("/chat_mcp")
async def chat_mcp(request: QuestionRequest):
    logger.info(f"执行请求 {request}")
    answer = await query_mcp_server(request.question, request.parallel)
    return {"answer": html_format(answer)}


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await connection_manager.connect(websocket)
#     try:
#         while True:
#             # 保持连接打开
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         connection_manager.active_connections.remove(websocket)

if __name__ == "__main__":
    MCPClientBase.init_logger(__file__)
    MCPClientBase.set_sse_client_log_level()

    # 提供WebSocket服务，等同于以上 @app.websocket("/ws") 对应方法
    app.add_api_websocket_route("/ws", connection_manager.websocket_endpoint)

    current_script_path = Path(__file__).resolve()
    static_dir = current_script_path.parent.parent / "static"
    # 需要在接口定义后执行
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    uvicorn.run(app, host="0.0.0.0", port=9000)
