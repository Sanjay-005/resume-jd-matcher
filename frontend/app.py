import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8001"

st.set_page_config(page_title="Resume-JD Matcher", layout="wide")
st.title("📄 Resume-JD Matcher")

tab1, tab2 = st.tabs(["Analyze", "Batch Rank"])

with tab1:
    st.subheader("Upload Resume & Job Description")
    resume_file = st.file_uploader("Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_text = st.text_area("Job Description", height=150)

    if st.button("Analyze", type="primary"):
        if resume_file and jd_text:
            with st.spinner("Submitting..."):
                files = {"resume": (resume_file.name, resume_file.getvalue())}
                data = {"jd_text": jd_text}
                resp = requests.post(f"{API_URL}/analyze", files=files, data=data)
                task_id = resp.json()["task_id"]

            with st.spinner("Analyzing (this can take 10-20s)..."):
                result = None
                for _ in range(30):
                    r = requests.get(f"{API_URL}/result/{task_id}").json()
                    if r["status"] == "completed":
                        result = r["result"]
                        break
                    elif r["status"] == "failed":
                        st.error(f"Task failed: {r.get('error')}")
                        break
                    time.sleep(2)

            if result:
                scores = result["scores"]
                col1, col2, col3 = st.columns(3)
                col1.metric("Semantic Score", f"{scores['semantic_score']*100:.1f}%")
                col2.metric("Skill Match", f"{scores['skill_score']*100:.1f}%")
                col3.metric("Composite Score", f"{scores['composite_score']*100:.1f}%")

                st.subheader("🔍 Gap Analysis")
                gaps = result["gap_analysis"]
                if gaps.get("missing_skills"):
                    st.write("**Missing Skills:**", ", ".join(gaps["missing_skills"]))
                for s in gaps.get("suggestions", []):
                    st.info(s)

                st.subheader("⚠️ Bias Check")
                bias = result["bias_check"]
                for flag in bias.get("flags", []):
                    st.warning(f"**{flag['phrase']}** — {flag['issue']}")

                with st.expander("Extracted Skills"):
                    st.write("**Resume Skills:**", ", ".join(result["resume_skills"]))
                    st.write("**JD Skills:**", ", ".join(result["jd_skills"]))
        else:
            st.warning("Please upload a resume and enter a job description.")

with tab2:
    st.subheader("Rank Resumes Against a Job Description")
    batch_jd = st.text_area("Job Description", height=150, key="batch_jd")
    top_k = st.slider("Number of results", 1, 20, 10)

    if st.button("Rank Resumes", type="primary"):
        if batch_jd:
            with st.spinner("Ranking..."):
                resp = requests.post(f"{API_URL}/batch-rank", data={"jd_text": batch_jd, "top_k": top_k})
                ranked = resp.json()["ranked_resumes"]

            if ranked:
                for i, r in enumerate(ranked, 1):
                    with st.container(border=True):
                        st.write(f"**#{i} — {r['payload'].get('filename', 'Unknown')}**")
                        st.write(f"Similarity: {r['score']*100:.1f}%")
                        st.caption(r['payload'].get('resume_snippet', '')[:200] + "...")
            else:
                st.info("No resumes found. Analyze some resumes first.")
        else:
            st.warning("Please enter a job description.")