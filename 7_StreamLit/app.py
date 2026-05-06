import streamlit as st
import pandas as pd

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Digital Twin TF Perturbation Explorer",
    layout="wide"
)

st.title("Digital Twin TF Perturbation Explorer")
st.markdown(
    "Explore precomputed transcription factor knockout perturbation scores "
    "across pancreatic progenitor, exocrine, and endocrine progenitor states."
)

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_ps_table():
    file_path = "Notebooks/7_StreamLit/TableS14_PS_Exo_Endo.xlsx"

    # Header is on row 2 of your Excel file
    df = pd.read_excel(file_path, sheet_name="Table S14", header=1)

    # Remove empty first column if present
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Make sure TF column is string
    df["TF_KO"] = df["TF_KO"].astype(str)

    return df


df = load_ps_table()

cell_state_cols = [col for col in df.columns if col != "TF_KO"]

# Long format for easier filtering
df_long = df.melt(
    id_vars="TF_KO",
    value_vars=cell_state_cols,
    var_name="Cell state",
    value_name="Perturbation score"
)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")

selected_tf = st.sidebar.selectbox(
    "Select TF knockout",
    sorted(df["TF_KO"].unique())
)

selected_state = st.sidebar.selectbox(
    "Select target cell state",
    cell_state_cols
)

top_n = st.sidebar.slider(
    "Number of top TFs to show",
    min_value=5,
    max_value=30,
    value=10
)

# -----------------------------
# TF-level view
# -----------------------------
st.header(f"Perturbation profile for {selected_tf} KO")

tf_data = df_long[df_long["TF_KO"] == selected_tf].copy()
tf_data = tf_data.sort_values("Perturbation score", ascending=False)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Perturbation scores across cell states")
    st.bar_chart(
        tf_data,
        x="Cell state",
        y="Perturbation score"
    )

with col2:
    st.subheader("Table")
    st.dataframe(tf_data, use_container_width=True)

# -----------------------------
# Cell-state-level ranking
# -----------------------------
st.header(f"Top predicted regulators for {selected_state}")

state_data = df[["TF_KO", selected_state]].copy()
state_data = state_data.rename(columns={selected_state: "Perturbation score"})

top_positive = state_data.sort_values(
    "Perturbation score",
    ascending=False
).head(top_n)

top_negative = state_data.sort_values(
    "Perturbation score",
    ascending=True
).head(top_n)

col3, col4 = st.columns(2)

with col3:
    st.subheader(f"Top positive perturbation scores for {selected_state}")
    st.bar_chart(
        top_positive,
        x="TF_KO",
        y="Perturbation score"
    )
    st.dataframe(top_positive, use_container_width=True)

with col4:
    st.subheader(f"Top negative perturbation scores for {selected_state}")
    st.bar_chart(
        top_negative,
        x="TF_KO",
        y="Perturbation score"
    )
    st.dataframe(top_negative, use_container_width=True)

# -----------------------------
# Full searchable table
# -----------------------------
st.header("Full perturbation score table")

search_term = st.text_input("Search TF")

if search_term:
    filtered_df = df[df["TF_KO"].str.contains(search_term, case=False, na=False)]
else:
    filtered_df = df

st.dataframe(filtered_df, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered table as CSV",
    data=csv,
    file_name="filtered_perturbation_scores.csv",
    mime="text/csv"
)