# agents/hr_agent.py
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

# === .env読み込み ===
load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")


@tool
async def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """
    ✅ MCPサーバーの hr_questions ツールを非同期で呼び出す。
    - params={"mode": mode, "applicant_answer": applicant_answer} を送信。
    - 🧠 MCP側がこの2引数を定義しているため、完全一致させる。
    """
    return await call_mcp_tool(
        "hr_questions",
        "hr_questions",
        {"mode": mode, "applicant_answer": applicant_answer},
    )


@tool
async def company_mission(section: str = "summary") -> str:
    """
    ✅ 企業理念・ビジョンを取得。
    """
    return await call_mcp_tool(
        "company_mission", "company_mission", {"section": section}
    )


hr_agent = Agent(
    name="HRAgent",
    description="人事担当。応募者の人物像や志望動機・成果を深掘りする。",
    system_prompt=(
        "あなたは企業の人事担当者です。応募者の性格・志望動機・スキル・成果を理解するための質問を行います。"
        "必要に応じて company_mission や hr_questions ツールを利用して、"
        "企業理念に沿った質問を生成してください。"
    ),
    tools=[company_mission, hr_questions],
    model=MODEL_ID,
)
