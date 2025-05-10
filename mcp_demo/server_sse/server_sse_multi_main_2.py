# coding=utf-8

from mcp.server import FastMCP
from mcp_demo.common.MCPCommon import MCPClientBase
from mcp_demo.server_sse.server_sse_multi_part_2 import MCPServer2

mcp = FastMCP(name="high_speed_railQuerySystem",
                host="0.0.0.0",
                port=8001,
                sse_path="/sse",
                message_path="/messages/")

mcpServer2: MCPServer2 = MCPServer2(mcp)
mcpServer2.init()

if __name__ == "__main__":
    MCPClientBase.init_logger(__file__)
    MCPClientBase.set_sse_server_log_level()
    mcp.run(transport="sse")
