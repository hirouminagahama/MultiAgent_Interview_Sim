from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("HRQuestionsServer")


def _load_data():
    """data.json を安全に読み込む。"""
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        data = json.load(f)
    # 配列で定義されていた場合も自動的に辞書に変換
    if isinstance(data, list):
        return {"question_pool": data}
    return data


@mcp.tool()
def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """
    人事が使う質問テンプレート。
    mode:
      - first     : オープニング質問
      - followup  : 応募者回答に基づく深掘り質問
    """
    data = _load_data()

    # --- オープニング質問 ---
    if mode == "first":
        q = data.get("first_question")
        if not q and "question_pool" in data:
            q = random.choice(data["question_pool"])
        return (
            f"ありがとうございます。まずは最初の質問をさせていただきます。\n\n**{q}**"
        )

    # --- フォローアップ質問 ---
    templates = data.get("followup_templates", [])
    base = random.choice(templates) if templates else "もう少し詳しく教えてください。"

    if applicant_answer:
        return (
            f"先ほどの回答内容を踏まえて、さらに深掘りさせてください。\n\n"
            f"応募者回答要約: {applicant_answer[:500]}\n\n{base}"
        )

    # --- 汎用質問プールから選択 ---
    pool = data.get("question_pool", [])
    if pool:
        return random.choice(pool)

    return "質問データが定義されていません。"


if __name__ == "__main__":
    mcp.run()
