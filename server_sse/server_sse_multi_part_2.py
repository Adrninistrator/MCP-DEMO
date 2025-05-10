# coding=utf-8
from typing import Dict

from pydantic import Field

from mcp.server import FastMCP
from mcp_demo.example import railway_data


class MCPServer2:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp

    def init(self):
        self.mcp.add_tool(self.query_city_station, description="查询城市中的高铁站点名称")

    def query_city_station(self, city_name: str = Field(..., description="城市名称")) -> Dict:
        return railway_data.query_city_station(city_name)
