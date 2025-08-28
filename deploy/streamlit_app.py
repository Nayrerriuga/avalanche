# import packages
import streamlit as st
import pandas as pd
import re
import altair as alt


# --- Helper function to clean text ---
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text


# --- App Title ---
st.set_page_config(page_title="GenAI Data Processor", layout="wide")
st.title("✨ GenAI-Powered Data Processing App")
st.markdown("Upload, clean, and explore customer reviews with interactive visualizations.")


# --- File uploader ---
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])


# --- Action buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Ingest Dataset", use_container_width=True):
        if uploaded_file is not None:
            try:
                st.session_state["df"] = pd.read_csv(uploaded_file)
                st.success("✅ Dataset loaded successfully!")
            except Exception as e:
                st.error(f"⚠️ Error loading file: {e}")
        else:
            st.warning("Please upload a CSV file first.")

with col2:
    if st.button("🧹 Parse Reviews", use_container_width=True):
        if "df" in st.session_state:
            if "SUMMARY" in st.session_state["df"].columns:
                st.session_state["df"]["CLEANED_SUMMARY"] = st.session_state["df"]["SUMMARY"].apply(clean_text)
                st.success("🧼 Reviews parsed and cleaned!")
            else:
                st.error("⚠️ Column 'SUMMARY' not found in dataset.")
        else:
            st.warning("Please ingest the dataset first.")


# --- Main Layout: Split into two panels ---
if "df" in st.session_state:
    st.markdown("---")

    left_col, right_col = st.columns([1.2, 1])  # left panel a bit wider

    with left_col:
        st.subheader("📊 Customer Reviews Table")

        # Product filter dropdown
        if "PRODUCT" in st.session_state["df"].columns:
            product = st.selectbox(
                "🔍 Filter by Product",
                ["All Products"] + list(st.session_state["df"]["PRODUCT"].unique())
            )

            if product != "All Products":
                filtered_df = st.session_state["df"][st.session_state["df"]["PRODUCT"] == product]
            else:
                filtered_df = st.session_state["df"]

            st.dataframe(filtered_df, use_container_width=True, height=500)
        else:
            st.warning("⚠️ Column 'PRODUCT' not found in dataset.")

    with right_col:
        st.subheader("📈 Sentiment Score Distribution")

        if "SENTIMENT_SCORE" in st.session_state["df"].columns:
            interval = alt.selection_interval()
            chart = alt.Chart(filtered_df).mark_bar().add_params(
                interval
            ).encode(
                alt.X("SENTIMENT_SCORE:Q", bin=alt.Bin(maxbins=10), title="Sentiment Score"),
                alt.Y("count():Q", title="Frequency"),
                tooltip=["count():Q"]
            ).properties(
                width=400,
                height=400,
                title=f"Distribution of Sentiment Scores ({product})"
            ).configure_title(
                fontSize=16,
                anchor="start",
                color="gray"
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("⚠️ Column 'SENTIMENT_SCORE' not found in dataset.")
