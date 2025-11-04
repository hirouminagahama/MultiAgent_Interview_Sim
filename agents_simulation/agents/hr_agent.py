from strands import Agent, tool


@tool
def hr_questions(query: str) -> str:
    """
    人事がよく聞く質問を生成する。
    query（入力）は未使用だが、Pydanticが要求するため残す。
    """
    return "あなたのPython経験と、それをどのように業務で活かしてきたか教えてください。"


hr_agent = Agent(
    name="HRAgent",
    description="人事担当。応募者の人物像や志望動機を深掘りする。",
    system_prompt=(
        "あなたは企業の人事担当者です。応募者の性格・志望動機・スキルを理解するための質問をします。"
        "必要に応じて、具体的な事例を尋ねてください。"
    ),
    tools=[hr_questions],
)
