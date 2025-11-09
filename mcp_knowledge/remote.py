import logging
import json
import asyncio
from fastmcp import FastMCP, settings

logging.basicConfig(level=logging.INFO)
logging.info("Remote MCP settings: %s", settings.model_dump_json(indent=2))

with open("remote.json", "r", encoding="utf-8") as fp:
    mcp_config = json.load(fp)

mcp = FastMCP.as_proxy(mcp_config, name="MCP Proxy")


async def main():
    # 最新版 FastMCP は keepalive_timeout をサポートしない
    await mcp.run_async(transport="http", port=8081)


if __name__ == "__main__":
    asyncio.run(main())
