from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("DeptQuestionsServer")


def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def dept_questions(context_summary: str = "") -> str:
    """
    技術面接用の質問テンプレートを返す。
    """
    data = _load_data()
    questions = data.get("technical_focus", [])
    q = (
        random.choice(questions)
        if questions
        else "技術的な課題をどのように解決してきましたか？"
    )
    if context_summary:
        return f"これまでの経緯を踏まえて質問します。\n{context_summary}\n\n{q}"
    return q


if __name__ == "__main__":
    mcp.run()
