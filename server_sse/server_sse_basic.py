# coding=utf-8
from typing import Dict

from pydantic import Field

from mcp.server import FastMCP
from mcp_demo.common.MCPCommon import LineNameRequest1, LineNameRequest2, MCPClientBase
from mcp_demo.example import railway_data

mcp = FastMCP(name="high_speed_railQuerySystem",
                host="0.0.0.0",
                port=8000,
                sse_path="/sse",
                message_path="/messages/")

@mcp.tool(name="get_all_lines", description="获取所有高铁线路编号，需要首先调用当前接口")
async def get_all_lines() -> list:
    """返回当前系统支持查询的所有高铁线路编号"""
    return railway_data.get_all_lines()


@mcp.tool(description="根据高铁线路编号查询起始站点名称，可用于判断指定线路是否能从某个站点到达另一个站点")
async def query_stations(line_name: str = Field(..., description="高铁线路编号如G1/G2")) -> Dict:
    return railway_data.query_stations(line_name)


@mcp.tool(description="根据高铁线路编号查询运行时长")
async def query_duration(line_name_request: LineNameRequest1 = Field(..., description="高铁线路编号请求类1")) -> Dict:
    return railway_data.query_duration(line_name_request)


@mcp.tool(description="根据高铁线路编号查询最低票价")
async def query_ticket_price(line_name_request: LineNameRequest2 = Field(..., description="高铁线路编号请求类2")) -> Dict:
    return railway_data.query_ticket_price(line_name_request)


if __name__ == "__main__":
    MCPClientBase.init_logger(__file__)
    MCPClientBase.set_sse_server_log_level()
    mcp.run(transport="sse")
