# coding=utf-8

from mcp.server import FastMCP
from mcp_demo.common.MCPCommon import MCPClientBase
from mcp_demo.server_sse.server_sse_multi_part_1_a import MCPServer1A
from mcp_demo.server_sse.server_sse_multi_part_1_b import MCPServer1B

mcp = FastMCP(name="high_speed_railQuerySystem",
                host="0.0.0.0",
                port=8000,
                sse_path="/sse",
                message_path="/messages/")

mcpServer1A: MCPServer1A = MCPServer1A(mcp)
mcpServer1A.initialize()
mcpServer1B: MCPServer1B = MCPServer1B(mcp)
mcpServer1B.initialize()

if __name__ == "__main__":
    MCPClientBase.init_logger(__file__)
    MCPClientBase.set_sse_server_log_level()
    mcp.run(transport="sse")
