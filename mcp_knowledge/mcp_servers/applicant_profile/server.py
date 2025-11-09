from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ApplicantProfileServer")


def _load_data():
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@mcp.tool()
def applicant_profile(topic: str = "motivation") -> str:
    """
    応募者の深層的な動機・思考・行動特性を返す。
    topic:
      - motivation      : 業務を行う動機
      - teamwork        : チームワークや協調性
      - problem_solving : 問題解決スタイル
    """
    data = _load_data()
    return data.get(topic, "該当情報が見つかりません。")


if __name__ == "__main__":
    mcp.run()
