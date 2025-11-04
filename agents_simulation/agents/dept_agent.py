from strands import Agent, tool


@tool
def dept_questions(query: str) -> str:
    """
    部門責任者が業務スキルを確認する質問を生成する。
    """
    return "Pythonを業務で活かす上で、どのような課題や改善提案をした経験がありますか？"


dept_agent = Agent(
    name="DeptAgent",
    description="部門責任者。実務スキルや問題解決力を評価する。",
    system_prompt=(
        "あなたは部門責任者です。応募者の技術スキルや課題解決力を確認するために質問します。"
        "応募者の回答内容を踏まえて、より深い実務的な質問を行ってください。"
    ),
    tools=[dept_questions],
)
