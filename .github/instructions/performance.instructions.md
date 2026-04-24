\---

applyTo: "app.py,components/\*\*/\*.py"

\---



Focus on Streamlit performance:

\- identify rerun-heavy functions

\- identify repeated database queries

\- suggest st.cache\_data or st.cache\_resource only when safe

\- do not modify code before giving a plan

\- no broad refactors

