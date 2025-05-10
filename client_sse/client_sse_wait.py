# coding=utf-8
import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client

from mcp_demo.common.MCPCommon import MCPClientBase, get_logger, sse_server_1_url

logger = get_logger(__file__)


async def sse_connect():
    async with sse_client(url=sse_server_1_url) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            while True:
                await asyncio.sleep(1)


if __name__ == "__main__":
    MCPClientBase.init_logger(__file__)
    MCPClientBase.set_sse_client_log_level()
    asyncio.run(sse_connect())
