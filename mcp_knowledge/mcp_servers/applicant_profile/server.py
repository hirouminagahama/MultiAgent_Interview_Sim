from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ApplicantProfileServer")


def _load_data():
    """data.jsonを安全に読み込む"""
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # career_details配列の最後にmeta_backgroundがある想定
    if isinstance(data, dict) and "career_details" in data:
        career_details = data["career_details"]
        if isinstance(career_details, list) and career_details:
            last = career_details[-1]
            if "meta_background" in last:
                return last["meta_background"]

    # フォールバック：meta_backgroundが存在しない場合
    return {
        "motivation": "該当情報が見つかりません。",
        "philosophy": "該当情報が見つかりません。",
        "career_vision": "該当情報が見つかりません。",
        "personal_notes": "該当情報が見つかりません。",
    }


@mcp.tool()
def applicant_profile(topic: str = "motivation") -> str:
    """
    応募者の深層的な動機・思考・行動特性を返す。
    topic:
      - motivation      : 業務を行う動機
      - philosophy      : 仕事観・価値観
      - career_vision   : 将来のキャリア展望
      - personal_notes  : 自己分析コメント
    """
    data = _load_data()
    result = data.get(topic)
    if not result:
        return f"該当情報（{topic}）が見つかりません。"
    return result


if __name__ == "__main__":
    mcp.run()
