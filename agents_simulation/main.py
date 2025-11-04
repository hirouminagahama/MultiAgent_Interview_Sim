# main_sync.py
import asyncio
from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text


async def run_interview_sync():
    print("=== 面接シミュレーション（同期実行） ===")

    # HR → Applicant → HR → Applicant → Dept → Applicant の順で逐次 await
    hr_q = await hr_agent.invoke_async(
        "応募者に最初の質問をしてください。",
        model_kwargs={"temperature": 0.0, "max_tokens": 1200},
    )
    hr_q_txt = extract_text(hr_q)
    print(f"\n[HR] {hr_q_txt}")

    app_r = await applicant_agent.invoke_async(
        hr_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_r_txt = extract_text(app_r)
    print(f"[Applicant] {app_r_txt}")

    hr_f = await hr_agent.invoke_async(
        f"応募者の回答:\n{app_r_txt}\nを踏まえてもう1つ質問してください。",
        model_kwargs={"temperature": 0.0},
    )
    hr_f_txt = extract_text(hr_f)
    print(f"[HR Follow-up] {hr_f_txt}")

    app_f = await applicant_agent.invoke_async(
        hr_f_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_f_txt = extract_text(app_f)
    print(f"[Applicant] {app_f_txt}")

    dept_q = await dept_agent.invoke_async(
        f"これまでのやり取り:\n{hr_q_txt}\n{app_r_txt}\n{hr_f_txt}\n{app_f_txt}\n"
        "を踏まえて、実務スキルを確認する質問をしてください。",
        model_kwargs={"temperature": 0.0},
    )
    dept_q_txt = extract_text(dept_q)
    print(f"[Dept] {dept_q_txt}")

    final_a = await applicant_agent.invoke_async(
        dept_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    final_a_txt = extract_text(final_a)
    print(f"[Applicant Final] {final_a_txt}")

    print("\n=== 面接シミュレーション終了 ===")


if __name__ == "__main__":
    asyncio.run(run_interview_sync())
