# main_sync.py
import asyncio
from typing import Any

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text


async def run_interview_sync():
    print("=== 面接シミュレーション（同期実行） ===")

    # 1. HRが最初の質問
    hr_q: Any = await hr_agent.invoke_async(
        "応募者に、Python経験と業務での活かし方について質問してください。",
        model_kwargs={"temperature": 0.0, "max_tokens": 1200},
    )
    hr_q_txt = extract_text(hr_q)
    print(f"\n[HR] {hr_q_txt}")

    # 2. Applicantが回答
    app_r: Any = await applicant_agent.invoke_async(
        hr_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_r_txt = extract_text(app_r)
    print(f"[Applicant] {app_r_txt}")

    # 3. HRのフォロー質問
    hr_f: Any = await hr_agent.invoke_async(
        f"応募者の回答:\n{app_r_txt}\nを踏まえて、もう1つ深掘り質問をしてください。",
        model_kwargs={"temperature": 0.0},
    )
    hr_f_txt = extract_text(hr_f)
    print(f"[HR Follow-up] {hr_f_txt}")

    # 4. Applicantが再回答
    app_f: Any = await applicant_agent.invoke_async(
        hr_f_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_f_txt = extract_text(app_f)
    print(f"[Applicant] {app_f_txt}")

    # 5. 部門責任者の最終質問
    dept_q: Any = await dept_agent.invoke_async(
        "これまでのやり取りを踏まえて、実務スキルを確認する技術的な質問を1つだけしてください。\n"
        f"- 最初のHR質問: {hr_q_txt}\n"
        f"- 応募者の回答: {app_r_txt}\n"
        f"- HRの深掘り: {hr_f_txt}\n"
        f"- 応募者の再回答: {app_f_txt}\n",
        model_kwargs={"temperature": 0.0},
    )
    dept_q_txt = extract_text(dept_q)
    print(f"[Dept] {dept_q_txt}")

    # 6. Applicantの最終回答
    final_a: Any = await applicant_agent.invoke_async(
        dept_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    final_a_txt = extract_text(final_a)
    print(f"[Applicant Final] {final_a_txt}")

    print("\n=== 面接シミュレーション終了 ===")


if __name__ == "__main__":
    asyncio.run(run_interview_sync())
