from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("CompanyMissionServer")


def _load_data():
    """data.jsonを安全に読み込む。辞書以外の形式は自動変換"""
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # 万が一リスト形式で定義された場合のフォールバック
    if isinstance(data, list):
        # 1行目→summary, 2行目→vision, 3行目→value として解釈
        data = {
            "summary": data[0] if len(data) > 0 else "",
            "vision": data[1] if len(data) > 1 else "",
            "value": data[2] if len(data) > 2 else "",
        }
    return data


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
    result = data.get(section)
    if not result:
        return f"該当情報（{section}）が見つかりません。"
    return result


if __name__ == "__main__":
    mcp.run()
