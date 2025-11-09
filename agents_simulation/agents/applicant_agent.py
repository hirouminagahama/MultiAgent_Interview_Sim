# agents/applicant_agent.py
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

# === .env読み込み ===
load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")


@tool
async def resume(section: str = "summary") -> str:
    """
    ✅ MCPサーバーの resume ツールを非同期で呼び出す。
    - params={"section": section} をMCPサーバーに渡す。
    """
    return await call_mcp_tool("resume", "resume", {"section": section})


@tool
async def applicant_profile(topic: str = "motivation") -> str:
    """
    ✅ MCPサーバーの applicant_profile ツールを非同期で呼び出す。
    - params={"topic": topic} をMCPサーバーに渡す。
    """
    return await call_mcp_tool(
        "applicant_profile", "applicant_profile", {"topic": topic}
    )


applicant_agent = Agent(
    name="ApplicantAgent",
    description="応募者。自分の経歴やスキルを説明する。",
    system_prompt=(
        "あなたは面接の応募者です。質問に答える際、履歴書や職務経歴書情報（resume）や"
        "人格・動機の詳細情報（applicant_profile）を確認しながら、具体的かつ誠実に回答してください。"
    ),
    tools=[resume, applicant_profile],
    model=MODEL_ID,
)
