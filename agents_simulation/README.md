# agents_simulation の MVP

---

# プロジェクト全体構成

## ディレクトリツリー（全体）

```text
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
│   ├── main_sync.py                # ★ 同期進行のメイン（固定フローMVP）
│   ├── main_autonomous.py          # HR→Applicant→Dept の自律型フロー
│   ├── main_mixed_random.py        # HR/Dept がランダムに質問する混合フロー
│   ├── model_provider.py           # モデル提供・切り替え用（将来拡張）
│   ├── pyproject.toml              # uv 用依存定義（Strands など）
│   ├── README.md
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

* **ルート (`MultiAgent_Interview_Sim/`)**

  * Git リポジトリのルート
  * ワークスペース定義（`.code-workspace`）と全体起動スクリプト（`run_all.sh`）など
  * サブプロジェクトを1つのモノレポとしてまとめる

* **`agents_simulation/`**

  * Strands Agents v1.14 を使った「面接シミュレーション」の中核
  * 3つのエージェント（応募者・人事・部門責任者）を定義し、

    * `main_sync.py` … 「HR→Applicant→HR→Applicant→Dept→Applicant」の**固定フロー**
    * `main_autonomous.py` … HRフェーズとDeptフェーズを**LLMに任せて自律終了**
    * `main_mixed_random.py` … HRとDeptが**ランダムに質問する実際の面接に近いフロー**
  * 今は単体で CLI 実行する MVP（将来 MCP / Streamlit から呼ばれる）

* **`mcp_knowledge/`**

  * FastMCP サーバー群を置く場所
  * `applicant_profile` や `hr_questions` などの「ナレッジ」を JSON で持ち、
    将来、Strands の `@tool` や HTTP 経由で参照する予定

* **`ui_streamlit/`**

  * Streamlit による Web UI
  * `main_sync.py` / `main_autonomous.py` / `main_mixed_random.py` を呼び出して、
    エージェントの発話をチャット風に表示するのがゴール

---

# agents_simulation – 面接シミュレーション MVP

このフォルダは、**Strands Agents v1.14.0** を使って
「応募者 / 人事 / 部門責任者」の3エージェントで面接をシミュレーションする MVP 実装です。

## 1. フォルダ構成（agents_simulation 配下）

```text
agents_simulation/
├── agents/
│   ├── __init__.py
│   ├── applicant_agent.py
│   ├── hr_agent.py
│   ├── dept_agent.py
│   └── util.py
├── main_sync.py
├── main_autonomous.py
├── main_mixed_random.py
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

# 面接シミュレーション（固定フロー版）
uv run python main_sync.py

# 自律型フロー版（HRフェーズ→Deptフェーズ）
uv run python main_autonomous.py

# ランダム混合フロー版（HR / Dept がランダムに質問）
uv run python main_mixed_random.py
```

実行すると、ターミナルに以下のような流れで会話が出力されます（例：`main_sync.py`）：

```text
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

## 3. 実装詳細（エージェント定義）

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

> ✅ 注意: `@tool` の引数名は `query: str` のように **`_` で始めない**（Pydantic 制約）。

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
        "あなたは企業の人事担当者です。応募者との面接を行います。\n"
        "開発部門の責任者（Dept）と一緒に面接を行っており、交互またはランダムに質問します。\n\n"
        "・あなたの役割は、応募者の人物像・志望動機・これまでの実績を理解することです。\n"
        "・直前までの会話ログ（HR, Dept, Applicant の発話）を読んで、"
        "必要に応じて質問またはコメントを1つだけ返してください。\n"
        "・面接全体を終了してよいと判断した場合は、あなたの最後のメッセージの末尾に "
        "`<INTERVIEW_DONE>` を付けてください。\n\n"
        "出力は常に日本語で、自然な面接としてふるまってください。"
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
        "これまでのやり取りを踏まえて、技術的な観点から応募者の実務スキルを確認してください。"
    )

dept_agent = Agent(
    name="DeptAgent",
    description="部門責任者。実務スキルや技術的な問題解決能力を評価する。",
    system_prompt=(
        "あなたは開発部門のマネージャーです。応募者との技術面接を担当します。\n"
        "人事担当（HR）と一緒に面接を行っており、交互またはランダムに質問します。\n\n"
        "・あなたの役割は、応募者の技術スキル・問題解決力・設計思考を確認することです。\n"
        "・直前までの会話ログ（HR, Dept, Applicant の発話）を読んで、"
        "必要に応じて質問またはコメントを1つだけ返してください。\n"
        "・面接全体を終了してよいと判断した場合は、あなたの最後のメッセージの末尾に "
        "`<INTERVIEW_DONE>` を付けてください。\n\n"
        "出力は常に日本語で、自然な面接としてふるまってください。"
    ),
    tools=[dept_questions],
    model="bedrock.claude-3-sonnet",
)
```

---

### 3-5. メインフロー `main_sync.py`（固定フローMVP）

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

**ポイント**

* `Agent()` のコンストラクタに `temperature` や `model_config` は渡さず、
  `invoke_async(..., model_kwargs={...})` で制御する（Strands v1.14 の仕様）。
* `await agent.invoke_async()` を**逐次的**に呼んでいるので、
  出力順が安定し、固定シナリオの動作確認に向いている。

---

## 4. 拡張フロー：自律型 / ランダム混合面接

固定フローの `main_sync.py` に加えて、より「実際の面接」に近い挙動を持つ
2つのメインフローを用意している。

### 4-1. 3つの実行モード比較

| スクリプト                  | 質問の流れ                                              | 終了条件                                    | 用途               |
| ---------------------- | -------------------------------------------------- | --------------------------------------- | ---------------- |
| `main_sync.py`         | HR → Applicant → HR → Applicant → Dept → Applicant | 固定ステップで終了                               | 最小MVP / デバッグ用    |
| `main_autonomous.py`   | HRフェーズとDeptフェーズをLLMに委ねる                            | `<HR_DONE>` / `<INTERVIEW_DONE>` トークン   | 自律的な「段階的面接」      |
| `main_mixed_random.py` | HR / Dept がラウンドごとにランダムに質問                          | `<INTERVIEW_DONE>` トークン or max round 到達 | 実際の面接に近い混合質問シナリオ |

---

### 4-2. 自律型フロー `main_autonomous.py` の考え方

**コンセプト**

* 面接を以下の2フェーズに分ける：

  1. HR が主体となって応募者の人物像・経験を深掘りする「HRフェーズ」
  2. Dept が主体となって技術スキルを深掘りする「Deptフェーズ」
* 各フェーズ内で **何問・何往復するかは LLM に任せる**：

  * HR が「もう十分」と判断したら `<HR_DONE>` を出す
  * Dept が「面接全体を終えてよい」と判断したら `<INTERVIEW_DONE>` を出す
* Python 側では「誰が話すか」だけ制御し、終了トリガーはトークンで検知する。

※ 以下は構造がわかるように簡略化した例（実コードとほぼ同じ構造）：

```python
# main_autonomous.py（イメージ）
import asyncio
from typing import Any, List, Dict

from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

Message = Dict[str, str]  # {"role": "HR" | "Applicant" | "Dept", "content": "..."}

def format_history_for_agent(history: List[Message]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)

async def run_interview_autonomous(max_turns: int = 30) -> None:
    history: List[Message] = []
    print("=== 自律型 面接シミュレーション開始 ===")

    turn = 0

    # ------------- HRフェーズ -------------
    hr_done = False
    while not hr_done and turn < max_turns:
        # HR の発話
        hr_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history_for_agent(history)}\n\n"
            "あなたは人事担当として、必要であれば質問やコメントを行ってください。\n"
            "HRフェーズを終えてよい場合は、メッセージ末尾に <HR_DONE> を付けてください。"
        )
        hr_result: Any = await hr_agent.invoke_async(
            hr_prompt, model_kwargs={"temperature": 0.2, "max_tokens": 1200}
        )
        hr_text = extract_text(hr_result)
        if "<HR_DONE>" in hr_text:
            hr_done = True
            hr_text = hr_text.replace("<HR_DONE>", "").strip()

        history.append({"role": "HR", "content": hr_text})
        print(f"[HR] {hr_text}\n")
        turn += 1
        if hr_done or turn >= max_turns:
            break

        # Applicant の回答
        app_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history_for_agent(history)}\n\n"
            "あなたは応募者として、直前の人事の発話に回答してください。"
        )
        app_result: Any = await applicant_agent.invoke_async(
            app_prompt, model_kwargs={"temperature": 0.2, "max_tokens": 1500}
        )
        app_text = extract_text(app_result)
        history.append({"role": "Applicant", "content": app_text})
        print(f"[Applicant] {app_text}\n")
        turn += 1

    # ------------- Deptフェーズ -------------
    dept_done = False
    while not dept_done and turn < max_turns:
        dept_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history_for_agent(history)}\n\n"
            "あなたは開発部門責任者として、技術的な質問やコメントを行ってください。\n"
            "面接全体を終了してよい場合は、メッセージ末尾に <INTERVIEW_DONE> を付けてください。"
        )
        dept_result: Any = await dept_agent.invoke_async(
            dept_prompt, model_kwargs={"temperature": 0.2, "max_tokens": 1200}
        )
        dept_text = extract_text(dept_result)
        if "<INTERVIEW_DONE>" in dept_text:
            dept_done = True
            dept_text = dept_text.replace("<INTERVIEW_DONE>", "").strip()

        history.append({"role": "Dept", "content": dept_text})
        print(f"[Dept] {dept_text}\n")
        turn += 1
        if dept_done or turn >= max_turns:
            break

        # Applicant の回答
        app_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history_for_agent(history)}\n\n"
            "あなたは応募者として、直前の部門責任者の発話に回答してください。"
        )
        app_result: Any = await applicant_agent.invoke_async(
            app_prompt, model_kwargs={"temperature": 0.2, "max_tokens": 1500}
        )
        app_text = extract_text(app_result)
        history.append({"role": "Applicant", "content": app_text})
        print(f"[Applicant] {app_text}\n")
        turn += 1

    print("=== 自律型 面接シミュレーション終了 ===")
```

**ポイント**

* フェーズの切り替えと終了トリガーは **LLMの判断 + 特殊トークン** で行う。
* Python 側は「誰が次に話すか」と「トークン検知」だけ行い、
  何回深掘りするかは完全に LLM に委ねている。

---

### 4-3. ランダム混合フロー `main_mixed_random.py` の考え方

**コンセプト**

* 実際の面接に近づけるため、

  * 「最初の質問は HR」
  * それ以降はラウンドごとに **HR または Dept のどちらかが質問し、必ず Applicant が回答**
* HR / Dept のどちらがいつ質問するかは **ある程度ランダム**：

  * Python 側の `choose_interviewer()` で次の質問者をランダム決定
* 面接の終了は：

  * HR or Dept が `<INTERVIEW_DONE>` を付けて発話する
  * または保険として `max_rounds` に達したら終了

**メイン構造（イメージ）**

```python
# main_mixed_random.py（イメージ）
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
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)

def choose_interviewer(round_index: int) -> str:
    """
    次に質問する面接官を選ぶ。
    - 最初のラウンドは必ず HR
    - 2ラウンド目以降は、ある程度ランダムに HR / Dept を選ぶ
    """
    if round_index == 0:
        return "HR"

    # 例: ラウンドが進むほど Dept が出やすくなる
    base_p_dept = 0.3 + min(round_index * 0.05, 0.4)  # 0.3〜0.7 の範囲
    return "Dept" if random.random() < base_p_dept else "HR"

async def run_interview_mixed_random(max_rounds: int = 10) -> None:
    """
    HR / Dept がランダムに質問し、Applicant が毎回答える面接シミュレーション。

    ・1ラウンド = 「面接官の発話」→「Applicant の回答」
    ・どの面接官が話すかは choose_interviewer() で決定
    ・どちらかの面接官が <INTERVIEW_DONE> を付けたら終了
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
            + ("人事担当（HR）" if interviewer_role == "HR" else "開発部門責任者（Dept）")
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
```

**ポイント**

* 実際の面接に近い「HR と Dept が織り交ざる」挙動を、
  **シンプルなランダムロジック + LLM の自律的な質問生成**で実現している。
* 「誰が次に話すか」は Python 側で制御（`choose_interviewer()`）、
  「何を質問するか／いつ終えるか」は LLM 側に委ねる、という分離になっている。

---

今後は、この3モード（固定 / 自律 / ランダム混合）を
Streamlit UI から選択して実行できるようにしていく想定。
