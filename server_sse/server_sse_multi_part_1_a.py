# coding=utf-8
from typing import Dict

from pydantic import Field

from mcp.server import FastMCP
from mcp_demo.example import railway_data


class MCPServer1A:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp

    def initialize(self):
        self.mcp.add_tool(self.get_all_lines, name="get_all_lines",
                          description="获取所有高铁线路编号，需要首先调用当前接口")
        self.mcp.add_tool(self.query_stations, description="根据高铁线路编号查询起始站点名称，可用于判断指定线路是否能从某个站点到达另一个站点")

    def get_all_lines(self) -> list:
        return railway_data.get_all_lines()

    def query_stations(self, line_name: str = Field(..., description="高铁线路编号如G1/G2")) -> Dict:
        return railway_data.query_stations(line_name)
