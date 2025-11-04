# agents_simulationのMVP

---

# プロジェクト全体構成

## ディレクトリツリー（全体）

```
MultiAgent_Interview_Sim/
├── .git/                           # Git リポジトリ（ルートに1つだけ）
├── .gitignore                      # 共通の ignore 設定
├── .env                            # ルート用環境変数（任意・Git管理しない）
├── multi_agent_workspace.code-workspace
├── run_all.sh                      # 将来、全コンポーネント起動用スクリプト
│
├── agents_simulation/              # ★ Strands Agents による面接シミュレーション（MVPの中心）
│   ├── .venv/                      # uv が作る仮想環境（Git ignore）
│   ├── agents/
│   │   ├── __init__.py             # パッケージ化用（空でOK）
│   │   ├── applicant_agent.py      # 応募者エージェント
│   │   ├── hr_agent.py             # 人事エージェント
│   │   ├── dept_agent.py           # 部門責任者エージェント
│   │   └── util.py                 # AgentResult からテキストを抜き出すユーティリティ
│   ├── .gitignore
│   ├── .python-version
│   ├── main.py                     # 非同期版サンプル（順序が前後し得る）
│   ├── main_sync.py                # ★ 同期進行のメイン（MVPで使用）
│   ├── model_provider.py           # モデル提供・切り替え用（将来拡張）
│   ├── pyproject.toml              # uv 用依存定義（Strands など）
│   ├── README.md                   # ← これを今から書く
│   └── uv.lock
│
├── mcp_knowledge/                  # FastMCP ベースのナレッジ層
│   ├── .venv/
│   ├── mcp_servers/                # 各 MCP サーバ（applicant_profile etc.）を置く場所
│   ├── .gitignore
│   ├── .python-version
│   ├── main.py                     # MCP テスト・起動用
│   ├── pyproject.toml
│   ├── README.md
│   ├── remote.json                 # MCP Remote 定義
│   ├── remote.py                   # FastMCP Proxy など
│   └── uv.lock
│
└── ui_streamlit/                   # Streamlit UI 層
    ├── .venv/
    ├── .vscode/                    # UI プロジェクト専用 VSCode 設定
    ├── .env                        # APIキー等（Git管理しない）
    ├── .gitignore
    ├── .python-version
    ├── app.py                      # Streamlit アプリ本体
    ├── pyproject.toml
    ├── README.md
    └── uv.lock

```

## 各フォルダの機能概要

- **ルート (`MultiAgent_Interview_Sim/`)**
    - Git リポジトリのルート
    - ワークスペース定義（`.code-workspace`）と全体起動スクリプト（`run_all.sh`）など
    - サブプロジェクトを1つのモノレポとしてまとめる
- **`agents_simulation/`**
    - Strands Agents v1.14 を使った「面接シミュレーション」の中核
    - 3つのエージェント（応募者・人事・部門責任者）を定義し、
        
        `main_sync.py` で **HR → Applicant → HR → Applicant → Dept → Applicant** のフローを実行
        
    - 今は単体で CLI 実行する MVP（将来 MCP / Streamlit から呼ばれる）
- **`mcp_knowledge/`**
    - FastMCP サーバー群を置く場所
    - `applicant_profile` や `hr_questions` などの「ナレッジ」を JSON で持ち、
        
        将来、Strands の `@tool` や HTTP 経由で参照する予定
        
- **`ui_streamlit/`**
    - Streamlit による Web UI
    - `main_sync.py` を呼び出して、エージェントの発話をチャット風に表示するのが最初のゴール

---

# agents_simulation – 面接シミュレーション MVP

このフォルダは、**Strands Agents v1.14.0** を使って

「応募者 / 人事 / 部門責任者」の3エージェントで面接をシミュレーションする MVP 実装です。

## 1. フォルダ構成（agents_simulation 配下）

```
agents_simulation/
├── agents/
│   ├── __init__.py
│   ├── applicant_agent.py
│   ├── hr_agent.py
│   ├── dept_agent.py
│   └── util.py
├── main_sync.py
├── main.py               # 非同期実験版（必要なら）
├── model_provider.py     # 将来のモデル切替ロジック用
├── pyproject.toml
├── uv.lock
├── .gitignore
└── .python-version

```

---

## 2. 準備と実行方法

```bash
cd MultiAgent_Interview_Sim/agents_simulation

# 依存インストール（Strands など）
uv sync

# 面接シミュレーション（同期版）を実行
uv run python main_sync.py

```

実行すると、ターミナルに以下のような流れで会話が出力されます：

```
=== 面接シミュレーション（同期実行） ===

[HR] ...最初の質問...

[Applicant] ...応募者の回答...

[HR Follow-up] ...深掘り質問...

[Applicant] ...再回答...

[Dept] ...技術的な質問...

[Applicant Final] ...最終回答...

=== 面接シミュレーション終了 ===

```

※「`Tool #1: XXX`」などの行は Strands SDK の内部ログです（`print()`ではない）。

---

## 3. 実装詳細

### 3-1. 共通ユーティリティ `agents/util.py`

Strands の `AgentResult` からテキストを抜き出すための関数です。

バージョンや実装差異に影響されないよう、多段フォールバックで取り出します。

```python
# agents/util.py
from typing import Any

def extract_text(result: Any) -> str:
    """
    Strands AgentResult 互換オブジェクトから最終テキストを安全に取り出す。
    Pylance の型エラーを避けるため Any で受け、多段フォールバックする。
    """

    # 1. よくある属性名
    for attr in ("final_output", "output_text", "text", "response"):
        try:
            val = getattr(result, attr, None)
            if isinstance(val, str) and val.strip():
                return val
        except Exception:
            pass

    # 2. message.content[0].text 形式
    try:
        msg = getattr(result, "message", None)
        if msg is not None:
            content = getattr(msg, "content", None)
            if isinstance(content, list) and content:
                block = content[0]
                txt = (
                    block.get("text")
                    if isinstance(block, dict)
                    else getattr(block, "text", None)
                )
                if isinstance(txt, str) and txt.strip():
                    return txt
            msg_text = getattr(msg, "text", None)
            if isinstance(msg_text, str) and msg_text.strip():
                return msg_text
    except Exception:
        pass

    # 3. dict 形式
    if isinstance(result, dict):
        for k in ("final_output", "output_text", "text", "response"):
            v = result.get(k)
            if isinstance(v, str) and v.strip():
                return v
        msg = result.get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list) and content:
                block = content[0]
                if isinstance(block, dict):
                    v = block.get("text")
                    if isinstance(v, str) and v.strip():
                        return v

    # 4. 最後の砦: __str__
    try:
        s = str(result)
        if isinstance(s, str) and s.strip():
            return s
    except Exception:
        pass

    return ""

```

---

### 3-2. 応募者エージェント `agents/applicant_agent.py`

```python
# agents/applicant_agent.py
from strands import Agent, tool

@tool
def applicant_profile(query: str) -> str:
    """
    応募者のプロフィール・職務経歴・Pythonプロジェクト経験を返すツール。

    現状は固定テキストだが、
    将来的には FastMCP 経由で JSON ナレッジから取得する想定。
    """
    return (
        "Python、AWS、SQLを活用したプロジェクト経験があることが確認できました。"
        "特に、データ分析・レポート自動化・API開発の領域でPythonを実務に活用しています。"
    )

applicant_agent = Agent(
    name="ApplicantAgent",
    description="応募者。自分の経歴やスキルを説明する。",
    system_prompt=(
        "あなたは面接の応募者です。質問に答える際、職務経歴やスキルを確認する必要がある場合は、"
        "必ず applicant_profile ツールを使用して応募者情報を確認してから回答してください。"
        "回答は日本語で、具体的なプロジェクト事例や数値も交えて説明してください。"
    ),
    tools=[applicant_profile],
    model="bedrock.claude-3-sonnet",  # 例：Bedrock。環境に応じて変更
)

```

> ✅ 注意: @tool の引数名は query: str のように _ で始めない（Pydantic制約）。
> 

---

### 3-3. 人事エージェント `agents/hr_agent.py`

```python
# agents/hr_agent.py
from strands import Agent, tool

@tool
def hr_questions(query: str) -> str:
    """
    人事がよく使う「応募者への質問」のテンプレートを返すツール。

    将来的にはここも MCP 経由のデータに置き換える。
    """
    return (
        "ありがとうございます。まずは最初の質問をさせていただきます。\n\n"
        "「あなたのPython経験と、それをどのように業務で活かしてきたか教えてください。」\n\n"
        "これまでのプログラミング経験や、具体的にどのようなプロジェクトでPythonを使用されたか、"
        "また業務上でどのような成果を上げることができたかについて、詳しくお聞かせください。"
    )

hr_agent = Agent(
    name="HRAgent",
    description="人事担当。応募者の人物像や志望動機・成果を深掘りする。",
    system_prompt=(
        "あなたは企業の人事担当者です。応募者の性格・志望動機・スキル・成果を理解するための質問を行います。"
        "応募者の回答をよく読み、必要に応じて具体的な事例や数値を求めるフォローアップ質問を生成してください。"
    ),
    tools=[hr_questions],
    model="bedrock.claude-3-sonnet",
)

```

---

### 3-4. 部門責任者エージェント `agents/dept_agent.py`

```python
# agents/dept_agent.py
from strands import Agent, tool

@tool
def dept_questions(query: str) -> str:
    """
    部門責任者が実務スキルや技術的な判断力を確認する質問を生成するツール。
    """
    return (
        "ありがとうございます。大量データ処理や自動化のご経験は非常に興味深いです。\n\n"
        "先ほどのプロジェクトを踏まえてお伺いしますが、"
        "「ボトルネックを特定して改善する際に、どのような指標やログを重視し、"
        "どのような手順で原因切り分けを行いましたか？」\n\n"
        "技術的な調査プロセスや、チームとの協力の仕方も含めて教えてください。"
    )

dept_agent = Agent(
    name="DeptAgent",
    description="部門責任者。実務スキルや技術的な問題解決能力を評価する。",
    system_prompt=(
        "あなたは開発部門のマネージャーです。応募者の技術スキルや業務遂行能力を確認するために、"
        "実務に即した具体的な質問を行います。応募者のこれまでの回答を踏まえ、"
        "深掘りが必要な点を見つけて質問してください。"
    ),
    tools=[dept_questions],
    model="bedrock.claude-3-sonnet",
)

```

---

### 3-5. メインフロー `main_sync.py`（MVPのエントリ）

```python
# main_sync.py
import asyncio
from typing import Any

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

async def run_interview_sync() -> None:
    """
    HR → Applicant → HR → Applicant → Dept → Applicant Final
    という順番で面接シミュレーションを同期的に実行する。
    """
    print("=== 面接シミュレーション（同期実行） ===")

    # 1. HR が最初の質問
    hr_q: Any = await hr_agent.invoke_async(
        "応募者に、Python経験と業務での活かし方について質問してください。",
        model_kwargs={"temperature": 0.0, "max_tokens": 1200},
    )
    hr_q_txt = extract_text(hr_q)
    print(f"\n[HR] {hr_q_txt}")

    # 2. Applicant が回答
    app_r: Any = await applicant_agent.invoke_async(
        hr_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_r_txt = extract_text(app_r)
    print(f"[Applicant] {app_r_txt}")

    # 3. HR がフォローアップ質問
    hr_f: Any = await hr_agent.invoke_async(
        f"応募者の回答:\n{app_r_txt}\n"
        "を踏まえて、もう1つ深掘り質問をしてください。",
        model_kwargs={"temperature": 0.0},
    )
    hr_f_txt = extract_text(hr_f)
    print(f"[HR Follow-up] {hr_f_txt}")

    # 4. Applicant が再回答
    app_f: Any = await applicant_agent.invoke_async(
        hr_f_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    app_f_txt = extract_text(app_f)
    print(f"[Applicant] {app_f_txt}")

    # 5. 部門責任者が技術的な質問
    dept_q: Any = await dept_agent.invoke_async(
        "これまでのやり取りを踏まえて、実務スキルを確認する技術的な質問を1つだけしてください。\n"
        f"- 最初のHR質問: {hr_q_txt}\n"
        f"- 応募者の回答: {app_r_txt}\n"
        f"- HRのフォローアップ: {hr_f_txt}\n"
        f"- 応募者の再回答: {app_f_txt}\n",
        model_kwargs={"temperature": 0.0},
    )
    dept_q_txt = extract_text(dept_q)
    print(f"[Dept] {dept_q_txt}")

    # 6. Applicant が最終回答
    final_a: Any = await applicant_agent.invoke_async(
        dept_q_txt,
        model_kwargs={"temperature": 0.0, "max_tokens": 1500},
    )
    final_a_txt = extract_text(final_a)
    print(f"[Applicant Final] {final_a_txt}")

    print("\n=== 面接シミュレーション終了 ===")

if __name__ == "__main__":
    asyncio.run(run_interview_sync())

```

### 重要なポイント

- Strands v1.14 では、
    
    **`Agent()` のコンストラクタに `temperature` や `model_config` を渡さず**、
    
    `invoke_async(..., model_kwargs={...})` で制御する。
    
- `await agent.invoke_async()` を **逐次的に** 呼んでいるので、
    
    出力順が安定し、面接の流れが分かりやすい。
    
- `Tool #X: ...` のログは Strands 自身のログ。
    
    UI（Streamlit）に出す際は、`print` の結果だけを使えば良い。
    

---

こんな感じで、このまま `agents_simulation/README.md` にコピペしてもらえば、

プロジェクト全体と MVP の仕様がきれいに共有できると思います 👍