from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ResumeServer")


def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def resume(section: str = "summary") -> str:
    """
    志願者の履歴書・職務経歴書情報を返す。
    section:
      - summary    : 全体概要
      - education  : 学歴
      - experience : 職務経歴
      - skills     : スキル一覧
    """
    data = _load_data()
    return data.get(section, "該当情報が見つかりません。")


if __name__ == "__main__":
    mcp.run()
