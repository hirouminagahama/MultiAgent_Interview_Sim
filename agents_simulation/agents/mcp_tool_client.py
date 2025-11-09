# agents/mcp_tool_client.py
from typing import Any
from fastmcp import Client

MCP_BASE_URL = "http://127.0.0.1:8081/mcp"


async def call_mcp_tool(server: str, tool_name: str, params: dict) -> str:
    """
    ✅ FastMCPツール共通呼び出し関数
    - FastMCPの登録名は `<server>_<tool>` 形式（例: applicant_profile_applicant_profile）。
    - Difyで確認されたツール名にも一致する。
    """
    try:
        async with Client(MCP_BASE_URL) as client:  # type: ignore
            full_name = f"{server}_{tool_name}"  # ← ⚙️ここをアンダースコア結合に変更！
            result: Any = await client.call_tool(name=full_name, arguments=params)
            if isinstance(result, dict):
                return result.get("result", f"[{full_name}] ツール応答なし")
            return str(result)
    except Exception as e:
        return f"[MCP呼び出しエラー @ {server}_{tool_name}] {e}"
