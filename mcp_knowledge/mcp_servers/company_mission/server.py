from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("CompanyMissionServer")


def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def company_mission(section: str = "summary") -> str:
    """
    企業の理念・ビジョン・バリューを返す。
    section:
      - summary : 概要
      - vision  : ビジョン
      - value   : 行動指針・価値観
    """
    data = _load_data()
    return data.get(section, "該当情報が見つかりません。")


if __name__ == "__main__":
    mcp.run()
