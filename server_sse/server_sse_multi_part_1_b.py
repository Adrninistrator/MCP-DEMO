# coding=utf-8
from typing import Dict

from pydantic import Field

from mcp.server import FastMCP
from mcp_demo.common.MCPCommon import LineNameRequest1, LineNameRequest2
from mcp_demo.example import railway_data


class MCPServer1B:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp

    def initialize(self):
        self.mcp.add_tool(self.query_duration, description="根据高铁线路编号查询运行时长")
        self.mcp.add_tool(self.query_ticket_price, description="根据高铁线路编号查询最低票价")

    def query_duration(self, line_name_request: LineNameRequest1 = Field(..., description="高铁线路编号请求类1")) -> Dict:
        return railway_data.query_duration(line_name_request)

    def query_ticket_price(self, line_name_request: LineNameRequest2 = Field(..., description="高铁线路编号请求类2")) -> Dict:
        return railway_data.query_ticket_price(line_name_request)
