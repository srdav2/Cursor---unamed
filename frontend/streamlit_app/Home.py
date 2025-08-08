import streamlit as st

st.set_page_config(page_title="Bank Comparator", layout="wide")

st.title("Bank Financials Comparator (MVP)")
st.write(
    "Upload FY24 PDFs for NAB and Commonwealth Bank. The dashboard and QC tools will appear here as they are implemented."
)

with st.expander("Project status"):
    st.markdown(
        "- Backend API scaffolded with health endpoint.\n"
        "- Next: upload, extraction, QC, and dashboards."
    )