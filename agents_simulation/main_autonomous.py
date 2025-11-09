# HR,FEPTのフェーズがある構築
# main_autonomous.py
import asyncio
from typing import Any, List, Dict

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

Message = Dict[str, str]  # {"role": "HR" | "Applicant" | "Dept", "content": "..."}


def print_turn(role: str, text: str) -> None:
    print(f"[{role}] {text}\n")


def format_history_for_agent(history: List[Message]) -> str:
    """
    会話履歴を各エージェントに渡しやすい文字列形式にする。
    """
    lines = []
    for msg in history:
        lines.append(f"{msg['role']}: {msg['content']}")
    return "\n".join(lines)


async def run_interview_autonomous(max_turns: int = 30) -> None:
    """
    ・最初の質問以外の回数は固定しない
    ・HRフェーズ: HRとApplicantがやり取りし、HRが <HR_DONE> を出したら終了
    ・Deptフェーズ: DeptとApplicantがやり取りし、Deptが <INTERVIEW_DONE> を出したら終了
    ・max_turns は保険（無限ループ防止）
    """

    history: List[Message] = []
    print("=== 自律型 面接シミュレーション開始 ===\n")

    turn = 0

    # ---------- HRフェーズ ----------
    hr_done = False
    while not hr_done and turn < max_turns:
        # HR の発話
        hr_prompt = (
            "以下はこれまでの面接ログです。\n"
            "これを踏まえて、あなた（人事担当）として次の発話をしてください。\n\n"
            f"{format_history_for_agent(history)}"
        )
        hr_result: Any = await hr_agent.invoke_async(
            hr_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1200},
        )
        hr_text = extract_text(hr_result)

        # <HR_DONE> を検知してフラグを立てる
        if "<HR_DONE>" in hr_text:
            hr_done = True
            hr_text = hr_text.replace("<HR_DONE>", "").strip()

        history.append({"role": "HR", "content": hr_text})
        print_turn("HR", hr_text)
        turn += 1
        if hr_done or turn >= max_turns:
            break

        # Applicant の発話
        app_prompt = (
            "以下はこれまでの面接ログです。\n"
            "あなたは応募者として、直前の人事の質問・コメントに回答してください。\n\n"
            f"{format_history_for_agent(history)}"
        )
        app_result: Any = await applicant_agent.invoke_async(
            app_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1500},
        )
        app_text = extract_text(app_result)
        history.append({"role": "Applicant", "content": app_text})
        print_turn("Applicant", app_text)
        turn += 1

    # ---------- Deptフェーズ ----------
    dept_done = False
    while not dept_done and turn < max_turns:
        # 部門責任者の発話
        dept_prompt = (
            "以下はこれまでの面接ログです。\n"
            "あなたは開発部門の責任者として、技術的な観点から質問・コメントを行ってください。\n"
            "面接を終了してよいと判断した場合は、メッセージの末尾に <INTERVIEW_DONE> を付けてください。\n\n"
            f"{format_history_for_agent(history)}"
        )
        dept_result: Any = await dept_agent.invoke_async(
            dept_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1200},
        )
        dept_text = extract_text(dept_result)

        if "<INTERVIEW_DONE>" in dept_text:
            dept_done = True
            dept_text = dept_text.replace("<INTERVIEW_DONE>", "").strip()

        history.append({"role": "Dept", "content": dept_text})
        print_turn("Dept", dept_text)
        turn += 1
        if dept_done or turn >= max_turns:
            break

        # Applicant の発話
        app_prompt = (
            "以下はこれまでの面接ログです。\n"
            "あなたは応募者として、直前の部門責任者の質問・コメントに回答してください。\n\n"
            f"{format_history_for_agent(history)}"
        )
        app_result: Any = await applicant_agent.invoke_async(
            app_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1500},
        )
        app_text = extract_text(app_result)
        history.append({"role": "Applicant", "content": app_text})
        print_turn("Applicant", app_text)
        turn += 1

    print("=== 自律型 面接シミュレーション終了 ===")


if __name__ == "__main__":
    asyncio.run(run_interview_autonomous())
