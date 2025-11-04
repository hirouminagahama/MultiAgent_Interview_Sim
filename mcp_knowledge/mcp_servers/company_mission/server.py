from fastmcp import FastMCP
import json, os

mcp = FastMCP(name="Knowledge MCP")


@mcp.tool
def get_knowledge():
    """登録済みのJSONナレッジを返す"""
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {"data": data}


if __name__ == "__main__":
    mcp.run(transport="stdio")
