# ランダムな会話
# main_mixed_random.py
import asyncio
import random
from typing import Any, Dict, List

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

Message = Dict[str, str]  # {"role": "HR" | "Applicant" | "Dept", "content": "..."}


def print_turn(role: str, text: str) -> None:
    print(f"[{role}] {text}\n")


def format_history(history: List[Message]) -> str:
    """
    会話履歴を各エージェントに渡しやすい文字列形式にする。
    """
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)


def choose_interviewer(round_index: int) -> str:
    """
    次に質問する面接官を選ぶ。
    - 最初のラウンドは必ず HR
    - 2ラウンド目以降は、ある程度ランダムに HR / Dept を選ぶ
      （序盤はHR寄り、後半はDept寄りにするなどの重み付けも可能）
    """
    if round_index == 0:
        return "HR"

    # 例: ラウンドが進むほど Dept が出やすくなる重み付け
    # round_index が大きいほど p_dept が増えるイメージ
    base_p_dept = 0.3 + min(round_index * 0.05, 0.4)  # 0.3〜0.7の範囲
    r = random.random()
    return "Dept" if r < base_p_dept else "HR"


async def run_interview_mixed_random(max_rounds: int = 15) -> None:
    """
    HR と Dept がランダムに質問し、Applicant が毎回答える面接シミュレーション。

    ・1ラウンド = 「面接官の発話」→「Applicant の回答」
    ・どの面接官が話すかは choose_interviewer() で決定
    ・どちらかの面接官が <INTERVIEW_DONE> を付けたら終了
    ・max_rounds は保険（無限ループ防止）
    """

    history: List[Message] = []
    print("=== ランダム混合 面接シミュレーション開始 ===\n")

    for round_index in range(max_rounds):
        # 1. 次に話す面接官を決める
        interviewer_role = choose_interviewer(round_index)
        agent = hr_agent if interviewer_role == "HR" else dept_agent

        # 2. 面接官の発話
        interviewer_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            "あなたは "
            + (
                "人事担当（HR）"
                if interviewer_role == "HR"
                else "開発部門責任者（Dept）"
            )
            + " として、次の発話（質問またはコメント）を1つだけ返してください。\n"
            "面接全体を終了してよいと判断した場合は、最後の文の末尾に <INTERVIEW_DONE> を付けてください。"
        )

        interviewer_result: Any = await agent.invoke_async(
            interviewer_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1200},
        )
        interviewer_text = extract_text(interviewer_result)

        done = False
        if "<INTERVIEW_DONE>" in interviewer_text:
            done = True
            interviewer_text = interviewer_text.replace("<INTERVIEW_DONE>", "").strip()

        history.append({"role": interviewer_role, "content": interviewer_text})
        print_turn(interviewer_role, interviewer_text)

        # 3. Applicant の回答
        applicant_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            "あなたは応募者として、直前の面接官の質問・コメントに回答してください。"
        )
        applicant_result: Any = await applicant_agent.invoke_async(
            applicant_prompt,
            model_kwargs={"temperature": 0.2, "max_tokens": 1500},
        )
        applicant_text = extract_text(applicant_result)
        history.append({"role": "Applicant", "content": applicant_text})
        print_turn("Applicant", applicant_text)

        if done:
            break

    print("=== ランダム混合 面接シミュレーション終了 ===")


if __name__ == "__main__":
    asyncio.run(run_interview_mixed_random())
