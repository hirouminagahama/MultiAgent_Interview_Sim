from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("HRQuestionsServer")


def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """
    人事が使う質問テンプレート。
    mode:
      - first     : オープニング質問
      - followup  : 応募者回答に基づく深掘り質問
    """
    data = _load_data()

    if mode == "first":
        return (
            "ありがとうございます。まずは最初の質問をさせていただきます。\n\n"
            f"**{data.get('first_question', '')}**"
        )

    templates = data.get("followup_templates", [])
    base = random.choice(templates) if templates else "もう少し詳しく教えてください。"

    if applicant_answer:
        return (
            f"先ほどの回答内容を踏まえて、深掘りさせてください。\n\n"
            f"応募者回答要約: {applicant_answer[:500]}\n\n{base}"
        )
    return base


if __name__ == "__main__":
    mcp.run()
