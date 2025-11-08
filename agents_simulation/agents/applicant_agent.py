from strands import Agent, tool


@tool
def applicant_profile(query: str) -> str:
    """Retrieve applicant's work history, skills, and Python project experience.
    Always use this tool when HR asks about the applicant's background or skills."""
    return (
        "Python、AWS、SQLを活用したプロジェクト経験があることが確認できました。"
        "特に、データ分析とAPI開発の両方でPythonを実務に活用しています。"
    )


applicant_agent = Agent(
    name="ApplicantAgent",
    description="応募者。経歴やスキルを説明する。",
    system_prompt=(
        "あなたは応募者です。質問に答える際、職務経歴やスキルを確認する必要がある場合は、"
        "必ず applicant_profile ツールを使用して情報を確認してから回答してください。"
    ),
    tools=[applicant_profile],
)
