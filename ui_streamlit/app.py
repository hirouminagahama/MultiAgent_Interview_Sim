import streamlit as st
import asyncio
from agents_simulation.main import main as run_simulation

st.title("🎯 面接シミュレーション (Strands Agents + FastMCP)")
st.caption("応募者・人事・部門責任者の自律的対話を再現")

if st.button("シミュレーションを開始"):
    with st.spinner("エージェントが会話中..."):
        asyncio.run(run_simulation())
