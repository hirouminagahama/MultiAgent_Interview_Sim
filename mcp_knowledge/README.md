

---

# 🧠 mcp_knowledge — MCPサーバー群（Dify / Strands 連携対応）

---

## 🗂 概要

本フォルダは、
**FastMCP（v2.13系）** を用いて構築した
「面接シミュレーション用ナレッジサーバー群」です。

すべてのツールは独立した **MCPサーバー（`stdio`モード）** として起動し、
`remote.py` によって集約され、
**1つのHTTPエンドポイント（例：`http://localhost:8081/mcp/`）** として
Dify や Strands Agents から利用可能です。

---

## 🏗 ディレクトリ構成

```
mcp_knowledge/
├── remote.json                   # MCPサーバー登録設定
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

| 層                     | 役割                     | 通信方式            |
| --------------------- | ---------------------- | --------------- |
| 各 `server.py`         | 独立したナレッジMCPサーバー（stdio） | stdio           |
| `remote.py`           | 複数MCPの統合プロキシ化          | HTTP (as_proxy) |
| Dify / Strands Agents | クライアント（ツール呼び出し元）       | HTTP経由          |

---

## 🚀 セットアップと起動

```bash
cd mcp_knowledge
uv sync
uv run remote.py
```

起動後、以下のようにログが表示されれば正常です：

```
INFO:fastmcp.proxy:Starting MCP Proxy "MCP Proxy" on http://127.0.0.1:8081/mcp
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

### 共通構造（全サーバー共通パターン）

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ServerName")

def _load_data():
    """data.jsonを安全に読み込む（型チェック付き）"""
    path = Path(__file__).parent / "data.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"error": "JSON形式が辞書ではありません。"}
        return data
    except Exception as e:
        return {"error": f"データ読み込みに失敗しました: {e}"}

@mcp.tool()
def tool_name(param: str = "default") -> str:
    """MCPツールの主機能を定義"""
    data = _load_data()
    return data.get(param, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()
```

---

### ① Applicant Profile — 応募者の深層的な動機・行動様式

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
      - motivation      : 業務を行う動機
      - teamwork        : チームワークや協調性
      - problem_solving : 問題解決スタイル
    """
    data = _load_data()
    return data.get(topic, "該当情報が見つかりません。")

if __name__ == "__main__":
    mcp.run()
```

---

### ② Resume — 履歴書・職務経歴書サーバー（構造化出力対応）

#### 📄 `server.py`（安全キャスト＋Markdown整形対応）

```python
from pathlib import Path
import json
from fastmcp import FastMCP

mcp = FastMCP("ResumeServer")

def _load_data():
    path = Path(__file__).parent / "data.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"error": "JSON形式が辞書ではありません。"}
        return data
    except Exception as e:
        return {"error": f"データ読み込みに失敗しました: {e}"}

@mcp.tool()
def resume(section: str = "summary") -> str:
    """
    志願者の履歴書・職務経歴書情報を返す。
    section:
      - summary        : 概要
      - education      : 学歴
      - experience     : 職務経歴の要約
      - skills         : スキル一覧
      - career_history : 職務詳細（Markdown整形）
    """
    data = _load_data()
    if not isinstance(data, dict):
        return "データ形式が不正です。"

    if section == "career_history":
        history = data.get("career_history")
        if not isinstance(history, list):
            return "職務経歴情報が見つかりません。"
        formatted = []
        for entry in history:
            dept = entry.get("department", "")
            position = entry.get("position", "")
            period = entry.get("period", "")
            formatted.append(f"### {dept}（{position}・{period}）")
            for field in ("main_projects", "details"):
                if entry.get(field):
                    formatted.append(f"**{field}:**")
                    for item in entry[field]:
                        formatted.append(f"- {item}")
        return "\n".join(formatted)

    result = data.get(section)
    if isinstance(result, str):
        return result
    elif isinstance(result, list):
        return "\n".join(result)
    else:
        return f"該当情報（{section}）が見つかりません。"

if __name__ == "__main__":
    mcp.run()
```

---

### ③ Company Mission — 企業理念・ビジョン

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

---

### ④ HR Questions — 人事質問テンプレート

```python
from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("HRQuestionsServer")

def _load_data():
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def hr_questions(mode: str = "first", applicant_answer: str = "") -> str:
    """
    mode:
      - first    : 初回質問
      - followup : 応募者回答への深掘り質問
    """
    data = _load_data()
    if isinstance(data, list):
        return random.choice(data)
    elif isinstance(data, dict):
        if mode == "first":
            return f"ありがとうございます。まずは最初の質問をさせていただきます。\n\n**{data.get('first_question', '')}**"
        templates = data.get("followup_templates", [])
        base = random.choice(templates) if templates else "もう少し詳しく教えてください。"
        return base
    return "質問データの形式が不正です。"

if __name__ == "__main__":
    mcp.run()
```

---

### ⑤ Dept Questions — 技術面接質問テンプレート

```python
from pathlib import Path
import json
import random
from fastmcp import FastMCP

mcp = FastMCP("DeptQuestionsServer")

def _load_data():
    path = Path(__file__).parent / "data.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
def dept_questions(context_summary: str = "") -> str:
    """技術面接用の質問を返す"""
    data = _load_data()
    if isinstance(data, list):
        q = random.choice(data)
    else:
        q = "技術的な課題をどのように解決しましたか？"
    return f"これまでのやり取りを踏まえて質問します。\n{context_summary}\n\n{q}" if context_summary else q

if __name__ == "__main__":
    mcp.run()
```

---

## ✅ Dify / Strands連携設定

Difyの **MCP設定画面** に以下を登録：

```
http://localhost:8081/mcp/
```

または Docker 実行環境では：

```
http://host.docker.internal:8081/mcp
```

➡ 「Fetch MCP Tools」をクリックすると、
上記5ツールが自動検出されます。



✅ **本READMEは v2.13.0.2 + 安全キャスト実装版に完全対応**
（`data.get()` の型安全化・例外補足・構造化Markdown整形対応済み）
