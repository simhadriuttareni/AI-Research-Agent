import streamlit as st
import requests
import time
import json

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {margin-top: -50px;}
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
        }
        .report-container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>🔬 AI Research Agent</h1>
        <p>Autonomous multi-agent research system powered by Groq AI</p>
    </div>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/api/v1"

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    depth = st.selectbox("Research Depth", ["quick", "standard", "deep"], index=1)
    max_sources = st.slider("Max Sources", min_value=5, max_value=20, value=10)
    st.markdown("---")
    st.markdown("### 📊 Stats")
    try:
        response = requests.get(f"{API_URL}/research")
        if response.status_code == 200:
            data = response.json()
            st.metric("Total Research Reports", data.get("count", 0))
    except:
        pass
    st.markdown("---")
    st.markdown("### 🤖 Agents")
    st.markdown("""
    - 🎯 Planner - Creates strategy
    - 🔍 Researcher - Gathers info
    - 📊 Analyst - Extracts insights
    - ✍️ Editor - Writes report
    - ✅ Reviewer - Quality check
    """)

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("🔍 Enter your research topic", placeholder="e.g., Quantum Computing, Climate Change, AI Ethics...", label_visibility="collapsed")
with col2:
    st.write("")
    st.write("")
    start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

if start_button and topic:
    with st.spinner("Starting research..."):
        try:
            response = requests.post(f"{API_URL}/research", json={"topic": topic, "depth": depth, "max_sources": max_sources}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                report_id = data.get("report_id")
                st.success(f"✅ Research started! Tracking ID: #{report_id}")
                
                status_container = st.container()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status = "pending"
                progress = 0
                status_messages = {"pending": "⏳ Queued...", "researching": "🔍 Gathering information...", "analyzing": "📊 Analyzing data...", "editing": "✍️ Writing report...", "completed": "✅ Complete!", "failed": "❌ Failed"}
                
                while status not in ["completed", "failed"]:
                    time.sleep(2)
                    status_response = requests.get(f"{API_URL}/research/{report_id}")
                    if status_response.status_code == 200:
                        report_data = status_response.json()
                        status = report_data.get("status", "pending")
                        progress_map = {"pending": 10, "researching": 40, "analyzing": 70, "editing": 90, "completed": 100, "failed": 100}
                        progress = progress_map.get(status, 0)
                        progress_bar.progress(progress)
                        status_text.info(f"**Status:** {status_messages.get(status, status.upper())}")
                        
                        if status == "completed":
                            st.balloons()
                            st.success("🎉 Research completed successfully!")
                            report_text = report_data.get("report", "")
                            citations = report_data.get("citations", [])
                            score = report_data.get("quality_score", 0)
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1: st.metric("Quality Score", f"{score}%")
                            with col2: st.metric("Sources", len(citations))
                            with col3: st.metric("Words", len(report_text.split()))
                            with col4: st.metric("Status", "✅ Complete")
                            
                            with st.expander("📄 View Full Report", expanded=True):
                                st.markdown(report_text)
                            
                            if citations:
                                with st.expander("📚 References", expanded=True):
                                    for c in citations:
                                        st.markdown(f"- **{c.get('title', 'Unknown')}**")
                                        if c.get('url'):
                                            st.markdown(f"  🔗 {c.get('url')}")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.download_button("📥 Download Report (TXT)", data=report_text, file_name=f"research_{topic.replace(' ', '_')}_{report_id}.txt", mime="text/plain", use_container_width=True)
                            with col2:
                                st.download_button("📥 Download Report (MD)", data=f"# Research Report: {topic}\n\n{report_text}", file_name=f"research_{topic.replace(' ', '_')}_{report_id}.md", mime="text/markdown", use_container_width=True)
                            with col3:
                                st.download_button("📥 Download Citations", data=json.dumps(citations, indent=2), file_name=f"citations_{report_id}.json", mime="application/json", use_container_width=True)
                            break
                        elif status == "failed":
                            st.error(f"❌ Research failed: {report_data.get('error', 'Unknown error')}")
                            break
                    else:
                        st.error(f"API Error: {status_response.status_code}")
                        break
            else:
                st.error(f"API Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the server is running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("### 📋 Recent Research Reports")

try:
    response = requests.get(f"{API_URL}/research", params={"limit": 10})
    if response.status_code == 200:
        data = response.json()
        reports = data.get("reports", [])
        if reports:
            cols = st.columns(2)
            for idx, report in enumerate(reports):
                with cols[idx % 2]:
                    status_icon = "✅" if report['status'] == "completed" else "🔄" if report['status'] == "researching" else "❌"
                    with st.container():
                        st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                                <h4>{status_icon} {report['topic'][:50]}</h4>
                                <p style="color: #666; font-size: 0.9rem;">
                                    Status: {report['status'].upper()} | 
                                    Score: {report.get('quality_score', 'N/A')}% | 
                                    {report['created_at'][:10]}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View #{report['id']}", key=f"view_{report['id']}"):
                            st.session_state['selected_report'] = report['id']
                            st.rerun()
        else:
            st.info("No research reports found. Start your first research!")
    else:
        st.error("Failed to fetch recent research")
except Exception as e:
    st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔬 AI Research Agent v1.0 | Built with LangChain, Groq, and Streamlit</p>
        <p style="font-size: 0.8rem;">© 2026 All Rights Reserved</p>
    </div>
""", unsafe_allow_html=True)
