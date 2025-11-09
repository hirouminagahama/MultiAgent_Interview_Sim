from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("DeptQuestionsServer")


def _load_data():
    """data.jsonを安全に読み込む"""
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        data = json.load(f)
    # 万一リストで定義されていた場合も自動変換
    if isinstance(data, list):
        return {"technical_focus": data}
    return data


@mcp.tool()
def dept_questions(context_summary: str = "") -> str:
    """
    技術面接用の質問テンプレートを返す。
    context_summary: 応募者の回答や経歴要約（オプション）
    """
    data = _load_data()

    # 技術フォーカス質問群を取得
    questions = data.get("technical_focus", [])
    q = (
        random.choice(questions)
        if questions
        else "技術的な課題をどのように解決してきましたか？"
    )

    # 最初の質問を context_summary の有無で出し分け
    if context_summary:
        return f"これまでの経緯を踏まえて質問します。\n{context_summary}\n\n{q}"
    return q


if __name__ == "__main__":
    mcp.run()
