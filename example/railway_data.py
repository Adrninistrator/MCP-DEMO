# coding=utf-8
from typing import Dict

from mcp_demo.common.MCPCommon import LineNameRequest1, LineNameRequest2

RAILWAY_DATA = {
    "G1": {
        "stations": ["bjx", "zzd"],
        "duration": 150,
        "price": 300
    },
    "G2": {
        "stations": ["cqx", "gyb"],
        "duration": 120,
        "price": 130
    },
    "G3": {
        "stations": ["cdd", "xab"],
        "duration": 210,
        "price": 263
    }
}

CITY_STATION_DATA = {
    "cq": ["cqx"],
    "gy": ["gyb"]
}


def get_all_lines() -> list:
    """返回当前系统支持查询的所有高铁线路编号"""
    return list(RAILWAY_DATA.keys())


def query_stations(line_name: str) -> Dict:
    """根据线路编号返回起点站和终点站"""
    if line_name not in RAILWAY_DATA:
        return {"error": "线路不存在"}
    stations = RAILWAY_DATA[line_name]["stations"]
    return {
        "line": line_name,
        "start": stations[0],
        "end": stations[1]
    }


def query_duration(line_name_request: LineNameRequest1) -> Dict:
    """返回指定线路的运行总时长（分钟）"""
    line_name = line_name_request.line_name
    if line_name not in RAILWAY_DATA:
        return {"error": "线路不存在"}
    return {
        "line": line_name,
        "duration": RAILWAY_DATA[line_name]["duration"],
        "unit": "分钟"
    }


def query_ticket_price(line_name_request: LineNameRequest2) -> Dict:
    """返回指定线路的最低票价"""
    line_name = line_name_request.line_name
    if line_name not in RAILWAY_DATA:
        return {"error": "线路不存在"}
    return {
        "line": line_name,
        "price": RAILWAY_DATA[line_name]["price"],
        "currency": "CNY"
    }


def query_city_station(city_name: str) -> Dict:
    if city_name not in CITY_STATION_DATA:
        return {"error": "城市不存在"}
    return CITY_STATION_DATA[city_name]
