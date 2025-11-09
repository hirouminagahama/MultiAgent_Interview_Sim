# main_mixed_random.py
import os
import asyncio
import random
from typing import Any, Dict, List
from dotenv import load_dotenv

# ✅ .env を最初にロードする（全Agent共通のMODEL_IDを読み込むため）
load_dotenv()
print(f"[DEBUG] Loaded MODEL_ID = {os.getenv('BEDROCK_MODEL_ID')}")

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

Message = Dict[str, str]  # {"role": "HR" | "Applicant" | "Dept", "content": "..."}

# ======== Utility ========


def print_turn(role: str, text: str) -> None:
    print(f"[{role}] {text}\n")


def format_history(history: List[Message]) -> str:
    """会話履歴を各エージェントに渡しやすい文字列形式にする。"""
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)


def choose_interviewer(round_index: int) -> str:
    """
    次に質問する面接官を選ぶ。
    - 最初のラウンドは必ず HR
    - 2ラウンド目以降はランダムに HR / Dept を選ぶ
    """
    if round_index == 0:
        return "HR"
    base_p_dept = 0.3 + min(round_index * 0.05, 0.4)  # 0.3〜0.7範囲
    return "Dept" if random.random() < base_p_dept else "HR"


# ======== メイン処理 ========


async def run_interview_mixed_random(max_rounds: int = 1) -> None:
    """
    HR と Dept がランダムに質問し、Applicant が毎回答える面接シミュレーション。
    各質問エージェントは MCP 連携ツールを利用して発話内容を生成。
    """
    history: List[Message] = []
    print("=== 面接シミュレーション（MCP連携ランダム制御）開始 ===\n")

    for round_index in range(max_rounds):
        interviewer_role = choose_interviewer(round_index)
        agent = hr_agent if interviewer_role == "HR" else dept_agent

        # --- 質問生成 ---
        interviewer_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            f"あなたは{('人事担当（HR）' if interviewer_role == 'HR' else '開発部門責任者（Dept）')}です。"
            "MCPツール（company_mission, dept_questions, hr_questions）を活用し、"
            "次の質問またはコメントを1つだけ返してください。\n"
            "面接を終了してよい場合は、最後の文に <INTERVIEW_DONE> を付けてください。"
        )

        interviewer_result: Any = await agent.invoke_async(
            interviewer_prompt,
            model_kwargs={"temperature": 0.3, "max_tokens": 1500},
        )
        interviewer_text = extract_text(interviewer_result)

        done = False
        if "<INTERVIEW_DONE>" in interviewer_text:
            done = True
            interviewer_text = interviewer_text.replace("<INTERVIEW_DONE>", "").strip()

        history.append({"role": interviewer_role, "content": interviewer_text})
        print_turn(interviewer_role, interviewer_text)

        # --- 応募者の回答 ---
        applicant_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            "あなたは応募者です。履歴書（resume）とプロフィール（applicant_profile）を参照し、"
            "直前の質問に対して自然に回答してください。"
        )
        applicant_result: Any = await applicant_agent.invoke_async(
            applicant_prompt,
            model_kwargs={"temperature": 0.3, "max_tokens": 1500},
        )
        applicant_text = extract_text(applicant_result)
        history.append({"role": "Applicant", "content": applicant_text})
        print_turn("Applicant", applicant_text)

        if done:
            print("=== 面接シミュレーション終了（<INTERVIEW_DONE> 検出） ===")
            break

    print("=== 面接シミュレーション終了 ===")


if __name__ == "__main__":
    asyncio.run(run_interview_mixed_random())
