
import streamlit as st
import pandas as pd
import os

st.title("Client Recovery Triage Tool (County & State Based)")

@st.cache_data
def load_resources():
    dfs = []
    for file in os.listdir():
        if file.endswith("resource.csv"):
            df = pd.read_csv(file, dtype=str)
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Name","Category","Description","Address","Phone","Website","County","State"])

services_df = load_resources()

def triage_client(housing, substance, mental, support):
    if housing == 'Unstable':
        if substance > 7 or mental > 7:
            return 'Housing'
    if mental > 6:
        return 'Mental Health'
    return 'Peer Support'

def find_matches(df, category, county, state):
    return df[
        (df['Category'].str.strip().str.lower() == category.strip().lower()) &
        (df['County'].str.strip().str.lower() == county.strip().lower()) &
        (df['State'].str.strip().str.lower() == state.strip().lower())
    ]

menu = st.sidebar.selectbox("Choose Access Mode", ["Free Individual Search", "Organization Login"])

if menu == "Free Individual Search":
    st.header("Self-Help Screening Tool")
    county = st.text_input("County of Residence").strip()
    state = st.text_input("State of Residence").strip()
    housing_status = st.selectbox("Housing Stability", ['Stable', 'Unstable'])
    substance_use = st.selectbox("Substance Use Severity", ['Mild (1-3)', 'Moderate (4-7)', 'Severe (8-10)'])
    mental_health = st.selectbox("Mental Health Concern Level", ['Low (1-3)', 'Moderate (4-7)', 'High (8-10)'])
    support_system = st.selectbox("Do You Have a Support System?", ['Yes', 'No'])

    if st.button("Find Support Resources"):
        substance_score = {'Mild (1-3)': 2, 'Moderate (4-7)': 5, 'Severe (8-10)': 9}[substance_use]
        mental_score = {'Low (1-3)': 2, 'Moderate (4-7)': 5, 'High (8-10)': 9}[mental_health]
        support = 1 if support_system == 'Yes' else 0
        recommended = triage_client(housing_status, substance_score, mental_score, support)
        st.success(f"Recommended Support Type: {recommended}")

        matched = find_matches(services_df, recommended, county, state)
        if not matched.empty:
            st.write("### Recommended Local Resources:")
            for _, row in matched.iterrows():
                info = (
                    f"**{row['Name']}**  
"
                    f"{row['Description']}  
"
                    f"_Address: {row['Address']}_  
"
                    f"_Phone: {row['Phone']}_  
"
                    f"[Website]({row['Website']})"
                )
                st.markdown(info)
                st.markdown("---")
        else:
            st.warning("No matching services found in your area.")
