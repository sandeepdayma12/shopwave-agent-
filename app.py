import json
import os

import httpx
import streamlit as st

from config.settings import settings

st.set_page_config(page_title="ShopWave Agentic AI", layout="wide")
st.title("🤖 ShopWave Agentic Support Resolution")
st.markdown("Processing mock tickets **concurrently** via FastAPI + LangGraph.")

if st.button("🚀 Process all 20 mock tickets (concurrent)"):
    with st.spinner("FastAPI Backend is running agents… (may take several minutes)"):
        try:
            _t = float(os.getenv("PROCESS_ALL_HTTP_TIMEOUT", "900"))
            response = httpx.post(f"{settings.fastapi_url}/process_all", timeout=_t)
            data = response.json()

            st.success("Processing Complete!")

            c1, c2, c3 = st.columns(3)
            c1.metric("Tickets Processed", data["total_processed"])
            c2.metric("Actions Logged", len(data["audit_logs"]))
            c3.metric("Dead Letter Queue", len(data["dlq"]))

            with open("audit_log.json", "w", encoding="utf-8") as f:
                json.dump(data["audit_logs"], f, indent=2)
            st.info("💾 Saved execution trail to `audit_log.json` locally.")

            st.subheader("Audit Log & Actions Taken")
            for log in data["audit_logs"]:
                with st.expander(f"🎫 {log['ticket_id']} - {log['action']}"):
                    st.write(f"**Details:** {log['details']}")
                    st.write(f"**Timestamp:** {log['timestamp']}")

            st.subheader("Deep Dive: Agent Reasoning Chains")
            for res in data["results"]:
                with st.expander(f"Trace: {res['ticket_id']} | Confidence: {res.get('confidence', 'N/A')}"):
                    if res["status"] == "Failed":
                        st.error(f"Failed: {res.get('error')}")
                    else:
                        for step in res["trace"]:
                            if step["type"] == "tool_call":
                                for call in step["calls"]:
                                    st.info(
                                        f"🛠️ **Called Tool:** `{call['name']}` | Args: `{call['args']}`"
                                    )
                            elif step["type"] == "thought":
                                st.write(f"🧠 **Thought:** {step['content']}")
                            elif step["type"] == "tool_result":
                                st.success(f"📥 **Result ({step['name']}):** {step['result']}")

        except Exception as e:
            st.error(f"Failed to connect to FastAPI Backend: {e}")
