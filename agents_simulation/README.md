

---

# 🤖 agents_simulation — 面接シミュレーション MVP（MCP連携対応）

---

## 🧩 概要

このフォルダは **Strands Agents v1.14.0** を利用し、
「応募者 / 人事 / 部門責任者」の 3 エージェントによる **面接シミュレーション** を実現します。

従来のローカル固定テキスト実装を超え、
**FastMCP（v2.13系）で提供されるナレッジサーバー群**
（`mcp_knowledge/` 配下）と **非同期に連携** する構成に進化しました。

---

## 🏗 ディレクトリ構成

```bash
agents_simulation/
├── agents/
│   ├── __init__.py
│   ├── applicant_agent.py      # 応募者エージェント（resume / applicant_profile 参照）
│   ├── hr_agent.py             # 人事エージェント（hr_questions / company_mission 参照）
│   ├── dept_agent.py           # 開発部門エージェント（dept_questions / company_mission 参照）
│   ├── mcp_tool_client.py      # ✅ MCPツール共通クライアント（非同期対応）
│   └── util.py                 # Strands AgentResult からのテキスト抽出ユーティリティ
│
├── main_sync.py                # 固定フロー面接（HR→Applicant→Dept）
├── main_autonomous.py          # 自律フロー（HRフェーズ→Deptフェーズ）
├── main_mixed_random.py        # ✅ ランダム混合面接（最新推奨）
├── model_provider.py           # 将来のモデル切替ロジック用（未使用）
├── pyproject.toml
├── uv.lock
├── .gitignore
└── .python-version
```

---

## ⚙️ 環境準備

```bash
cd MultiAgent_Interview_Sim/agents_simulation
uv sync
```

ルートにある `.env` で Bedrock モデルなどを指定します：

```bash
# .env
BEDROCK_MODEL_ID=bedrock.claude-3-sonnet
```

---

## 🚀 実行方法

```bash
# HR→Applicant→Dept の固定フロー
uv run python main_sync.py

# HRフェーズ→Deptフェーズの自律進行
uv run python main_autonomous.py

# ✅ HR/Dept がランダムに質問する混合面接（MCP連携）
uv run python main_mixed_random.py
```

実行例：

```
=== 面接シミュレーション（MCP連携ランダム制御）開始 ===
[HR] あなたのPython経験と業務での活かし方を教えてください。
[Applicant] はい、私は製造現場の品質データをPythonで自動分析するシステムを構築しました...
[Dept] AWSを用いた実装の工夫を教えてください。
[Applicant] LambdaとS3を組み合わせたバッチ設計を行い...
=== 面接シミュレーション終了 ===
```

---

## 🧠 各エージェントの実装概要（MCP連携版）

---

### ① 応募者エージェント — `applicant_agent.py`

```python
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")

@tool
async def resume(section: str = "summary") -> str:
    """📄 履歴書情報を取得"""
    return await call_mcp_tool("resume", "resume", {"section": section})

@tool
async def applicant_profile(topic: str = "motivation") -> str:
    """🧭 応募者の人格・動機情報を取得"""
    return await call_mcp_tool("applicant_profile", "applicant_profile", {"topic": topic})

applicant_agent = Agent(
    name="ApplicantAgent",
    description="応募者。自分の経歴やスキルを説明する。",
    system_prompt=(
        "あなたは面接の応募者です。"
        "resume（職務経歴）と applicant_profile（動機・思考）を参照し、"
        "具体的かつ誠実に回答してください。"
    ),
    tools=[resume, applicant_profile],
    model=MODEL_ID,
)
```

---

### ② 人事エージェント — `hr_agent.py`

```python
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")

@tool
async def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """💬 人事質問テンプレートを取得"""
    return await call_mcp_tool(
        "hr_questions",
        "hr_questions",
        {"mode": mode, "applicant_answer": applicant_answer},
    )

@tool
async def company_mission(section: str = "summary") -> str:
    """🏢 企業理念・ビジョンを取得"""
    return await call_mcp_tool("company_mission", "company_mission", {"section": section})

hr_agent = Agent(
    name="HRAgent",
    description="人事担当。応募者の人物像や志望動機・成果を深掘りする。",
    system_prompt=(
        "あなたは企業の人事担当者です。"
        "応募者の性格・志望動機・スキル・成果を理解するため、"
        "company_mission と hr_questions を参照しながら質問を生成してください。"
    ),
    tools=[company_mission, hr_questions],
    model=MODEL_ID,
)
```

---

### ③ 部門責任者エージェント — `dept_agent.py`

```python
import os
from dotenv import load_dotenv
from strands import Agent, tool
from agents.mcp_tool_client import call_mcp_tool

load_dotenv()
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "bedrock.claude-3-sonnet")

@tool
async def dept_questions(context_summary: str = "") -> str:
    """🧑‍💻 技術面接質問を取得"""
    return await call_mcp_tool(
        "dept_questions",
        "dept_questions",
        {"context_summary": context_summary},
    )

@tool
async def company_mission(section: str = "summary") -> str:
    """🏢 企業理念を取得"""
    return await call_mcp_tool("company_mission", "company_mission", {"section": section})

dept_agent = Agent(
    name="DeptAgent",
    description="開発部門責任者。実務スキルや技術的な問題解決能力を評価する。",
    system_prompt=(
        "あなたは開発部門のマネージャーです。"
        "応募者の技術スキルや業務遂行能力を確認するために、"
        "company_mission と dept_questions を活用して質問してください。"
    ),
    tools=[company_mission, dept_questions],
    model=MODEL_ID,
)
```

---

### ④ MCPクライアント共通関数 — `mcp_tool_client.py`

```python
from typing import Any
from fastmcp import Client

MCP_BASE_URL = "http://127.0.0.1:8081/mcp"

async def call_mcp_tool(server: str, tool_name: str, params: dict) -> str:
    """
    ✅ FastMCPツール共通呼び出し関数（非同期版）
    - 実際のツール名は `<server>_<tool>` 形式。
    - FastMCPのHTTPクライアントを非同期で利用。
    """
    try:
        async with Client(MCP_BASE_URL) as client:
            full_name = f"{server}_{tool_name}"
            result: Any = await client.call_tool(name=full_name, arguments=params)
            if isinstance(result, dict):
                return result.get("result", f"[{full_name}] ツール応答なし")
            return str(result)
    except Exception as e:
        return f"[MCP呼び出しエラー @ {server}_{tool_name}] {e}"
```

---

### ⑤ ユーティリティ — `util.py`

```python
from typing import Any

def extract_text(result: Any) -> str:
    """
    Strands AgentResult から最終テキストを安全に抽出。
    多様な構造（text / response / message.content[0].text 等）に対応。
    """
    for attr in ("final_output", "output_text", "text", "response"):
        val = getattr(result, attr, None)
        if isinstance(val, str) and val.strip():
            return val

    try:
        msg = getattr(result, "message", None)
        content = getattr(msg, "content", None)
        if isinstance(content, list) and content:
            block = content[0]
            txt = block.get("text") if isinstance(block, dict) else getattr(block, "text", None)
            if isinstance(txt, str):
                return txt
        msg_text = getattr(msg, "text", None)
        if isinstance(msg_text, str):
            return msg_text
    except Exception:
        pass

    if isinstance(result, dict):
        for k in ("final_output", "output_text", "text", "response"):
            if isinstance(result.get(k), str):
                return result[k]

    return str(result)
```

---

### ⑥ メインスクリプト — `main_mixed_random.py`（最新版）

```python
import os, asyncio, random
from dotenv import load_dotenv
from typing import Any, Dict, List
from agents.applicant_agent import applicant_agent
from agents.hr_agent import hr_agent
from agents.dept_agent import dept_agent
from agents.util import extract_text

load_dotenv()
print(f"[DEBUG] Loaded MODEL_ID = {os.getenv('BEDROCK_MODEL_ID')}")

Message = Dict[str, str]

def print_turn(role: str, text: str): print(f"[{role}] {text}\n")
def format_history(h: List[Message]) -> str: return "\n".join(f"{m['role']}: {m['content']}" for m in h)

def choose_interviewer(i: int) -> str:
    if i == 0: return "HR"
    p = 0.3 + min(i * 0.05, 0.4)
    return "Dept" if random.random() < p else "HR"

async def run_interview_mixed_random(max_rounds: int = 10):
    print("=== 面接シミュレーション（MCP連携ランダム制御）開始 ===\n")
    history: List[Message] = []

    for i in range(max_rounds):
        interviewer_role = choose_interviewer(i)
        agent = hr_agent if interviewer_role == "HR" else dept_agent

        interviewer_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            f"あなたは{'人事担当（HR）' if interviewer_role=='HR' else '開発部門責任者（Dept）'}です。"
            "MCPツール（company_mission, dept_questions, hr_questions）を利用し、"
            "次の質問またはコメントを1つだけ返してください。\n"
            "面接を終了してよい場合は <INTERVIEW_DONE> を末尾に付けてください。"
        )

        interviewer_result = await agent.invoke_async(interviewer_prompt, model_kwargs={"temperature": 0.3})
        interviewer_text = extract_text(interviewer_result)
        done = "<INTERVIEW_DONE>" in interviewer_text
        interviewer_text = interviewer_text.replace("<INTERVIEW_DONE>", "").strip()

        history.append({"role": interviewer_role, "content": interviewer_text})
        print_turn(interviewer_role, interviewer_text)

        applicant_prompt = (
            "以下はこれまでの面接ログです。\n"
            f"{format_history(history)}\n\n"
            "あなたは応募者です。resume と applicant_profile を参照し、"
            "直前の質問に自然に回答してください。"
        )
        applicant_result = await applicant_agent.invoke_async(applicant_prompt, model_kwargs={"temperature": 0.3})
        applicant_text = extract_text(applicant_result)
        history.append({"role": "Applicant", "content": applicant_text})
        print_turn("Applicant", applicant_text)

        if done:
            print("=== 面接シミュレーション終了（<INTERVIEW_DONE> 検出） ===")
            break

if __name__ == "__main__":
    asyncio.run(run_interview_mixed_random())
```

---

## ✅ 特徴まとめ

| 機能                     | 内容                                                                           |
| ---------------------- | ---------------------------------------------------------------------------- |
| **MCP連携**              | FastMCP Proxy経由で `resume` / `company_mission` / `hr_questions` などをリアルタイム呼び出し |
| **完全非同期化**             | `await call_mcp_tool()` に統一し、レスポンス遅延にも強い                                     |
| **Dify / Strands 両対応** | DifyのMCP連携でも動作確認済み（`http://localhost:8081/mcp/`）                             |
| **Bedrockモデル対応**       | `.env` から `BEDROCK_MODEL_ID` をロードして全エージェントに共通設定                              |
| **ユーティリティ強化**          | `extract_text()` によりStrands結果を柔軟に抽出可能                                        |
| **面接ランダム化**            | HR / Dept の質問順序をランダムにし、より自然な面接を再現                                            |

---

✅ **本READMEは、非同期MCP対応版（2025年11月リビジョン）** に完全準拠しています。
