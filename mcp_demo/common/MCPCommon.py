# coding=utf-8
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
from dotenv import load_dotenv
from fastapi import WebSocket
from mcp.types import TextContent, ImageContent, EmbeddedResource
from openai import OpenAI
from pydantic import BaseModel, Field
from starlette.websockets import WebSocketDisconnect

from mcp_demo.common.HttpLogger import HttpLogger

load_dotenv()
sse_server_url = os.getenv("MCP_DEMO_SSE_SERVER_URL")
sse_server_1_url = sse_server_url if sse_server_url is not None else "http://127.0.0.1:8000/sse"
sse_server_2_url = "http://127.0.0.1:8001/sse"


def get_logger(file):
    logger = logging.getLogger(Path(file).stem)
    logger.setLevel(logging.INFO)
    return logger


def replace_special_chars(input_str: str):
    return input_str.strip().replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def html_format(input_str: str):
    return input_str.replace("\\n", "<br>").replace("\n", "<br>")


class QuestionRequest(BaseModel):
    question: str
    parallel: bool


class LineNameRequest1(BaseModel):
    line_name: str = Field(..., description="高铁线路编号如G1/G2")


class LineNameRequest2(BaseModel):
    line_name: str = Field(..., description="高铁线路编号如G1/G2")
    not_used: str = Field("", description="暂未使用的参数")


class ToolExecutionData:
    def __init__(self, seq: int, tool_seq: int, tool_name: str, use_tool_reason: str, function_args: dict,
                 tool_exec_result: None | list[TextContent | ImageContent | EmbeddedResource]):
        self.seq = seq
        self.tool_seq = tool_seq
        self.tool_name = tool_name
        self.use_tool_reason = use_tool_reason
        self.function_args = function_args
        self.tool_exec_result = tool_exec_result

    def to_dict(self, for_html: bool = False) -> dict:
        results = []
        if self.tool_exec_result is not None:
            for result in self.tool_exec_result:
                result_str = result.model_dump_json()
                if for_html:
                    result_str = html_format(result_str)
                results.append(result_str)
        else:
            results.append("调用工具返回失败")
        return {
            "seq": self.seq,
            "tool_seq": self.tool_seq,
            "tool_name": self.tool_name,
            "use_tool_reason": self.use_tool_reason,
            "function_args": self.function_args,
            "tool_exec_result": results
        }

    def generate_log(self) -> str:
        used_use_tool_reason = replace_special_chars(self.use_tool_reason)
        used_tool_exec_result = replace_special_chars(str(self.tool_exec_result))
        return f"### seq {self.seq} tool_seq {self.tool_seq} 执行工具 {self.tool_name} 选择工具原因 {used_use_tool_reason} 参数 {self.function_args} 工具返回 {used_tool_exec_result}"

    def __str__(self) -> str:
        """字符串表示形式"""
        return self.generate_log()


class MCPClientBase:
    load_dotenv()
    # 初始化日志记录器
    http_client = httpx.Client(event_hooks={
        'request': [HttpLogger.log_request],
        'response': [HttpLogger.log_response]}
    )

    client = OpenAI(
        api_key=os.getenv("MCP_DEMO_API_KEY"),
        base_url=os.getenv("MCP_DEMO_BASE_URL"),
        http_client=http_client,
        default_headers={"Content-Type": "application/json; charset=utf-8"}
    )

    model = os.getenv("MCP_DEMO_MODEL_NAME")

    @classmethod
    def init_logger(cls, file):
        # 获取当前脚本名称
        script_name = Path(file).stem  # 例如：当前脚本是 test.py -> "test"
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_script_path = Path(file).resolve()

        # 创建日志目录
        log_dir = Path(current_script_path.parent.parent / "log")
        log_dir.mkdir(exist_ok=True, parents=True)

        # 日志文件路径（格式：脚本名_当前时间.log）
        log_file = log_dir / f"{script_name}_{current_time}.log"

        # 创建格式化器
        formatter = logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        # 文件处理器（自动创建日志文件）
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # 配置根日志记录器
        root_logger = logging.getLogger()  # 根记录器
        # 添加处理器到根记录器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    @classmethod
    def set_sse_client_log_level(cls):
        # 设置 sse_client 方法所在模块的日志级别
        logging.getLogger("mcp.client.sse").setLevel(logging.DEBUG)
        logging.getLogger("HttpLogger").setLevel(logging.INFO)

    @classmethod
    def set_sse_server_log_level(cls):
        logging.getLogger("mcp.server.sse").setLevel(logging.DEBUG)
        logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.DEBUG)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def websocket_endpoint(self, websocket: WebSocket):
        await self.connect(websocket)
        try:
            while True:
                # 保持连接打开
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)

    async def send_ws_message(self, message):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message, ensure_ascii=False))
