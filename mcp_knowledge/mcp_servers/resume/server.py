from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ResumeServer")


def _load_data():
    """data.jsonを安全に読み込む。常にdictを返す"""
    path = Path(__file__).parent / "data.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # 文字列やリストであっても辞書化して返す
        if not isinstance(data, dict):
            return {"error": "JSON形式が辞書ではありません。"}
        return data
    except Exception as e:
        return {"error": f"データ読み込みに失敗しました: {e}"}


@mcp.tool()
def resume(section: str = "summary") -> str:
    """
    志願者の履歴書・職務経歴書情報を返す。
    section:
      - summary        : 全体概要
      - education      : 学歴
      - experience     : 職務経歴の要約
      - skills         : スキル一覧
      - career_history : 詳細な職務経歴（Markdown形式）
    """
    data = _load_data()

    # 万一辞書でない場合のフォールバック
    if not isinstance(data, dict):
        return "データ形式が不正です。"

    # career_historyだけ構造化処理
    if section == "career_history":
        history = data.get("career_history")
        if not isinstance(history, list):
            return "職務経歴情報が見つかりません。"

        formatted = []
        for entry in history:
            dept = entry.get("department", "")
            position = entry.get("position", "")
            period = entry.get("period", "")
            formatted.append(f"### {dept}（{position}・{period}）")

            # 主なプロジェクト
            projects = entry.get("main_projects", [])
            if projects:
                formatted.append("**主なプロジェクト:**")
                for p in projects:
                    formatted.append(f"- {p}")

            # 詳細
            details = entry.get("details", [])
            if details:
                formatted.append("**詳細:**")
                for d in details:
                    formatted.append(f"- {d}")

        return "\n".join(formatted)

    # 通常項目
    result = data.get(section)
    if isinstance(result, str):
        return result
    elif isinstance(result, list):
        return "\n".join(result)
    else:
        return f"該当情報（{section}）が見つかりません。"


if __name__ == "__main__":
    mcp.run()
