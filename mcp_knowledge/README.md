---

# 🧠 mcp_knowledge — MCPサーバー群（Dify連携対応）

---

## 🗂 概要

本フォルダは、
**FastMCP（v2.13系）** を利用して構築した
「面接シミュレーション用ナレッジツール群」です。

すべてのツールは独立した **MCPサーバー（`stdio`モード）** として実行され、
`remote.py` により集約されて **1つのHTTPエンドポイント**（例：`http://localhost:8081/mcp/`）
として Dify や Strands Agents から利用可能です。

---

## 🏗 ディレクトリ構成

```
mcp_knowledge/
├── remote.json                   # MCPツール登録設定
├── remote.py                     # FastMCP.as_proxy によるHTTP統合プロキシ
│
└── mcp_servers/
    ├── applicant_profile/
    │   ├── data.json
    │   └── server.py
    │
    ├── resume/
    │   ├── data.json
    │   └── server.py
    │
    ├── company_mission/
    │   ├── data.json
    │   └── server.py
    │
    ├── hr_questions/
    │   ├── data.json
    │   └── server.py
    │
    └── dept_questions/
        ├── data.json
        └── server.py
```

---

## ⚙️ MCPアーキテクチャ概要

| 層                     | 役割                    | 通信方式            |
| --------------------- | --------------------- | --------------- |
| 各 `server.py`         | 独立したナレッジツール（stdioモード） | stdio           |
| `remote.py`           | 全MCPツールのプロキシ集約        | HTTP (as_proxy) |
| Dify / Strands Agents | クライアント（ツール呼び出し）       | HTTP経由          |

---

## 🚀 セットアップと起動

```bash
cd mcp_knowledge
uv sync
uv run python remote.py
```

起動後のログ例：

```
INFO:fastmcp.proxy:Starting MCP Proxy "MCP Proxy" on http://localhost:8081/mcp/
INFO:fastmcp.proxy:Launched 5 subprocess MCP servers (stdio)
```

---

## 🧩 remote.json

```json
{
  "mcpServers": {
    "applicant_profile": {
      "command": "uv",
      "args": ["run", "mcp_servers/applicant_profile/server.py"]
    },
    "resume": {
      "command": "uv",
      "args": ["run", "mcp_servers/resume/server.py"]
    },
    "company_mission": {
      "command": "uv",
      "args": ["run", "mcp_servers/company_mission/server.py"]
    },
    "hr_questions": {
      "command": "uv",
      "args": ["run", "mcp_servers/hr_questions/server.py"]
    },
    "dept_questions": {
      "command": "uv",
      "args": ["run", "mcp_servers/dept_questions/server.py"]
    }
  }
}
```

---

## 🧠 各MCPサーバーの構成と実装例

---

## 🧩 各サーバーの共通構成
すべての server.py は同一パターンで構成されています。

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ServerName")

def _load_data():
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def tool_name(param: str = "default") -> str:
    """目的に応じた説明文"""
    data = _load_data()
    return data.get(param, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()  # stdioモードで起動

```

## 各フォルダ内server.py, data.jsonの記載内容
### ① applicant_profile — 応募者の深層的な動機・行動様式

#### 📄 `server.py`

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ApplicantProfileServer")

def _load_data():
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def applicant_profile(topic: str = "motivation") -> str:
    """
    応募者の深層的な動機・思考・行動特性を返す。
    topic:
      - motivation      : 業務への動機
      - teamwork        : チームワークに対する姿勢
      - problem_solving : 問題解決の考え方
    """
    data = _load_data()
    return data.get(topic, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()
```

#### 📘 `data.json`

```json
{
  "motivation": "常に現場課題の解決に関心を持ち、データ活用と自動化で業務改善を推進してきた。",
  "teamwork": "チーム全体で成果を出すことを重視し、後輩育成やレビュー文化の改善にも貢献した。",
  "problem_solving": "課題を構造的に分析し、仮説検証と迅速な試行を繰り返して成果を導いた。"
}
```

---

### ② resume — 志願者の履歴書・職務経歴情報

#### 📄 `server.py`

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ResumeServer")

def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def resume(section: str = "summary") -> str:
    """
    志願者の履歴書・職務経歴書情報を返す。
    section:
      - summary    : 全体概要
      - education  : 学歴
      - experience : 職務経歴
      - skills     : スキル一覧
    """
    data = _load_data()
    return data.get(section, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()
```

#### 📘 `data.json`

```json
{
  "summary": "製造業で品質保証・AIシステム構築に従事。Python, AWS, SQLを活用した改善経験多数。",
  "education": "工業化学専攻（修士課程修了）",
  "experience": "凸版印刷にて品質保証6年、システム開発部門でAI導入を担当。",
  "skills": "Python, SQL, AWS SageMaker, Streamlit, FastAPI, Tableau"
}
```

---

### ③ company_mission — 企業ミッション・理念

#### 📄 `server.py`

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("CompanyMissionServer")

def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def company_mission(section: str = "summary") -> str:
    """
    企業の理念・ビジョン・バリューを返す。
    section:
      - summary : 概要
      - vision  : ビジョン
      - value   : 行動指針
    """
    data = _load_data()
    return data.get(section, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()
```

#### 📘 `data.json`

```json
{
  "summary": "テクノロジーを通じて社会課題を解決し、持続可能な価値を創出する。",
  "vision": "人とデータが調和する未来社会の実現。",
  "value": "挑戦・誠実・共創を軸に、信頼されるパートナーを目指す。"
}
```

---

### ④ hr_questions — 人事用質問テンプレート

#### 📄 `server.py`

```python
from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("HRQuestionsServer")

def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """
    人事の質問テンプレートを返す。
    mode:
      - first     : 初回質問
      - followup  : 応募者回答への深掘り質問
    """
    data = _load_data()

    if mode == "first":
        return (
            "ありがとうございます。まずは最初の質問をさせていただきます。\n\n"
            f"**{data.get('first_question', '')}**"
        )

    templates = data.get("followup_templates", [])
    base = random.choice(templates) if templates else "もう少し詳しく教えてください。"

    if applicant_answer:
        return (
            f"応募者の回答を踏まえて、以下を伺います。\n"
            f"要約: {applicant_answer[:200]}...\n\n{base}"
        )

    return base

if __name__ == "__main__":
    mcp.run()
```

#### 📘 `data.json`

```json
{
  "first_question": "あなたのPython経験と、それをどのように業務で活かしてきたか教えてください。",
  "followup_templates": [
    "具体的にどのようなプロジェクトで成果を上げましたか？",
    "チームで困難な課題を乗り越えた経験はありますか？",
    "改善提案を行った事例を教えてください。"
  ]
}
```

---

### ⑤ dept_questions — 技術面接用質問テンプレート

#### 📄 `server.py`

```python
from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("DeptQuestionsServer")

def _load_data():
    with (Path(__file__).parent / "data.json").open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def dept_questions(context_summary: str = "") -> str:
    """
    技術的な質問を生成するツール。
    """
    data = _load_data()
    questions = data.get("technical_focus", [])
    q = random.choice(questions) if questions else "技術的な課題をどのように解決しましたか？"
    if context_summary:
        return f"これまでのやり取りを踏まえて質問します。\n{context_summary}\n\n{q}"
    return q

if __name__ == "__main__":
    mcp.run()
```

#### 📘 `data.json`

```json
{
  "technical_focus": [
    "ボトルネックを特定する際、どのようなメトリクスを重視しましたか？",
    "AWSを活用したシステム構築での工夫を教えてください。",
    "異常検知や自動化システムにおけるエラー分析の手順を説明してください。"
  ]
}
```

---

## ✅ Dify 連携設定

Difyの **MCP設定画面** に以下を登録：

```
http://localhost:8081/mcp/
```

➡ 「Fetch MCP Tools」をクリックすると、
上記5ツールが自動検出されます。

---

## 🔮 今後の拡張

| 項目                     | 内容                                   |
| ---------------------- | ------------------------------------ |
| **MCP Inspector**      | 各ツールの入出力をCLIで確認                      |
| **FastMCP + Qdrant統合** | ベクトルRAG対応                            |
| **Strands連携**          | `agents_simulation` 側からHTTP経由で自動呼び出し |
| **Dify Workflow統合**    | 各ツールをAgentツールノードとして活用                |

---

---
### メモ（Difyと連携する際の注意事項）
---
difyにつなぎ込む場合は、以下のようなURLで登録する必要がある。
http://host.docker.internal:8081/mcp  

---