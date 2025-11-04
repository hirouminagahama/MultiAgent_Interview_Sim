# agents/util.py
from typing import Any


def extract_text(result: Any) -> str:
    """
    Strands AgentResult 互換オブジェクトから最終テキストを安全に取り出す。
    Pylance 型エラーを避けるため、引数は Any で受け、多段フォールバックで抽出する。
    """
    # 1) よくある名前の属性を直接参照（文字列なら即返す）
    for attr in ("final_output", "output_text", "text", "response"):
        try:
            val = getattr(result, attr, None)
            if isinstance(val, str) and val.strip():
                return val
        except Exception:
            pass

    # 2) message.content[0].text 形式（Message -> ContentBlock[] -> text）
    try:
        msg = getattr(result, "message", None)
        if msg is not None:
            content = getattr(msg, "content", None)
            if isinstance(content, list) and content:
                block = content[0]
                # dict型 or オブジェクト型の両対応
                if isinstance(block, dict):
                    txt = block.get("text")
                else:
                    txt = getattr(block, "text", None)
                if isinstance(txt, str) and txt.strip():
                    return txt
            # message.text がある実装にも対応
            msg_text = getattr(msg, "text", None)
            if isinstance(msg_text, str) and msg_text.strip():
                return msg_text
    except Exception:
        pass

    # 3) dict で来る実装の保険
    if isinstance(result, dict):
        for k in ("final_output", "output_text", "text", "response"):
            v = result.get(k)
            if isinstance(v, str) and v.strip():
                return v
        # message → content → text 形式
        msg = result.get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list) and content:
                block = content[0]
                if isinstance(block, dict):
                    v = block.get("text")
                    if isinstance(v, str) and v.strip():
                        return v

    # 4) 最後の砦：__str__ に頼る
    try:
        s = str(result)
        if isinstance(s, str) and s.strip():
            return s
    except Exception:
        pass

    return ""  # どうしても取れない場合
