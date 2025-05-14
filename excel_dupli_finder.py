
import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="CleanSheet LLM - Excel via LLaMA", layout="wide")
st.title("🧠 CleanSheet LLM - Natural Language Excel Tool (LLaMA)")

st.markdown("""
Upload your Excel file and describe what you want to do.
The app uses a local LLaMA model (via Ollama) to generate and run Python code.
""")

# Upload Excel
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])
df = None

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success(f"Loaded file with {df.shape[0]:,} rows and {df.shape[1]} columns.")
    st.dataframe(df.head(), use_container_width=True)

    user_query = st.text_area("💬 What would you like to do with this Excel data?", placeholder="e.g. Remove duplicates by Email")

    if st.button("🧠 Ask LLaMA (Offline)"):
        if not user_query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Thinking..."):

                # Sample first 20 rows to include in prompt
                sample_data = df.head(20).to_csv(index=False)
                columns = ", ".join(df.columns)

                prompt = f"""
You are a helpful Python data analyst.
The user uploaded an Excel file with the following columns: {columns}.

Here is a sample of the data (CSV format):
{sample_data}

The user asked: "{user_query}"

Please write Python pandas code that performs the user's request. 
Assign the final DataFrame to a variable named `result`.
DO NOT include file reading or printing code.
Only return valid Python code.
"""

                # Send to local LLaMA via Ollama API
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    generated_code = response.json()["response"]
                    st.code(generated_code, language="python")

                    try:
                        # Execute code safely
                        local_vars = {"df": df.copy()}
                        exec(generated_code, {}, local_vars)
                        result_df = local_vars.get("result", None)

                        if result_df is not None and isinstance(result_df, pd.DataFrame):
                            st.success("✅ Code executed successfully.")
                            st.dataframe(result_df.head(50), use_container_width=True)

                            # Download button
                            buffer = BytesIO()
                            result_df.to_excel(buffer, index=False)
                            buffer.seek(0)
                            st.download_button(
                                "📥 Download Result as Excel",
                                data=buffer,
                                file_name="result_llm.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.error("⚠️ Code did not return a DataFrame named `result`.")
                    except Exception as e:
                        st.error(f"❌ Error running generated code: {e}")
                else:
                    st.error("Failed to connect to local LLaMA via Ollama.")
else:
    st.info("Please upload an Excel file to begin.")
