# agents/dept_agent.py
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

# === .env読み込み ===
load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")


@tool
async def dept_questions(context_summary: str = "") -> str:
    """
    ✅ MCPサーバーの dept_questions ツールを非同期で呼び出す。
    - params={"context_summary": context_summary} をMCPサーバーに渡す。
    - 🧠 注意：
      dept_questions サーバーの引数も "context_summary" に統一されている。
      クライアント側では値を使わないが、I/F整合性維持のため空文字で送る。
    """
    return await call_mcp_tool(
        "dept_questions", "dept_questions", {"context_summary": context_summary}
    )


@tool
async def company_mission(section: str = "summary") -> str:
    """
    ✅ MCPサーバー上の company_mission ツールを非同期で呼び出す。
    """
    return await call_mcp_tool(
        "company_mission", "company_mission", {"section": section}
    )


dept_agent = Agent(
    name="DeptAgent",
    description="開発部門責任者。実務スキルや技術的な問題解決能力を評価する。",
    system_prompt=(
        "あなたは開発部門のマネージャーです。応募者の技術スキルや業務遂行能力を確認するために、"
        "実務に即した具体的な質問を行います。応募者のこれまでの回答を踏まえ、"
        "必要に応じて company_mission や dept_questions を参照しながら質問を生成してください。"
    ),
    tools=[company_mission, dept_questions],
    model=MODEL_ID,
)
