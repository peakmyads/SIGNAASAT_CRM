# path: pages/10_social_analytics.py

import streamlit as st
import pandas as pd
from datetime import date
from services.db_service import append_row
from services.data_loader import load_data

from services.ui_style import apply_sidebar_style
apply_sidebar_style()

st.set_page_config(layout="wide")

st.title("📊 Social Media Analytics")

st.markdown("""
<style>

/* Save Button Styling */
div.stButton > button {
    background: linear-gradient(90deg,#6a5cff,#8f7bff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 16px;
    transition: 0.3s ease;
}

div.stButton > button:hover {
    background: linear-gradient(90deg,#5948ff,#7b68ff);
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Add Data", "Analytics Dashboard"])


# ------------------------
# Add Social Data
# ------------------------

with tab1:

    data = load_data()
    clients_df = data.get("clients", pd.DataFrame())

    if clients_df.empty:
        st.warning("No clients found. Please add clients first.")
        st.stop()

    client_list = ["Select Client"] + list(clients_df["client_name"].unique())

    client = st.selectbox(
        "Select Client",
        client_list,
        index=0
    )

    platform = st.selectbox(
        "Platform",
        ["Instagram", "YouTube"]
    )
    
    tasks_df = data.get("tasks", pd.DataFrame())

    # Platform → Work Type Mapping
    if platform == "Instagram":
        work_types = ["Reel", "Story Creative"]
    elif platform == "YouTube":
        work_types = ["YouTube Video"]
    else:
        work_types = []

    # Filter completed tasks based on client + platform mapping
    completed_tasks = tasks_df[
        (tasks_df["status"].astype(str).str.strip() == "Completed") &
        (tasks_df["client_name"].astype(str).str.strip() == client) &
        (tasks_df["work_type"].astype(str).str.strip().isin(work_types)) &
        (tasks_df["video_url"].astype(str).str.strip() != "")
    ]

    if completed_tasks.empty:
        st.warning("No completed videos found for selected client & platform")
        video_url = ""
    else:
        # Create label for better UX
        completed_tasks["label"] = (
            completed_tasks["month"] + " | " +
            completed_tasks["work_type"] + " | " +
            completed_tasks["video_url"]
        )

        url_map = dict(zip(completed_tasks["label"], completed_tasks["video_url"]))

        selected_label = st.selectbox(
            "Select Video",
            ["Select Video"] + list(url_map.keys())
        )

        video_url = url_map.get(selected_label, "")
        
        # 🎬 Video Preview
        if video_url:

            st.markdown("### 🎬 Video Preview")

            # YouTube Preview
            if "youtube.com" in video_url or "youtu.be" in video_url:
                st.video(video_url)

            # Instagram Preview (limited support)
            elif "instagram.com" in video_url:
                st.markdown(
                    f"""
                    <a href="{video_url}" target="_blank">
                        🔗 Click to view Instagram video
                    </a>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.info("Preview not available for this URL type")

        if selected_label == "Select Video":
            video_url = ""

    views = st.number_input("Views", min_value=0)
    likes = st.number_input("Likes", min_value=0)
    comments = st.number_input("Comments", min_value=0)

    followers = st.number_input("Followers Gained", min_value=0)

    if st.button("Save Analytics"):

        social_df = data.get("social", pd.DataFrame())

        # Normalize URL (avoid whitespace issues)
        video_url_clean = video_url.strip().lower()

        if not social_df.empty:
            existing_urls = (
                social_df["video_url"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            if video_url_clean in existing_urls.values:
                st.error("⚠️ This Video URL already exists!")
                st.stop()

        data_insert = {
            "client_name": client,
            "platform": platform,
            "video_url": video_url,
            "views": views,
            "likes": likes,
            "comments": comments,
            "followers_gained": followers,
            "date": str(date.today())
        }

        append_row("Social_Insights", data_insert)

        st.cache_data.clear()
        st.session_state.pop("app_data", None)

        st.success("Analytics saved")
        st.rerun()


# ------------------------
# Analytics Dashboard
# ------------------------

with tab2:

    data = load_data()
    df = data.get("social", pd.DataFrame())

    if df.empty:
        st.info("No analytics data yet")
        st.stop()

    # Drop unwanted columns if needed
    df_display = df.copy()

    # Format date
    df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%d-%b-%Y")

    # Column formatting
    df_display.columns = [col.replace("_", " ").title() for col in df_display.columns]

    # Table CSS
    table_html = """
    <style>
    .analytics-table {
        border-collapse: collapse;
        width: 100%;
        font-family: sans-serif;
    }

    .analytics-table th {
        background-color: #1E4E9E;
        color: white;
        font-weight: bold;
        padding: 10px;
        text-align: left;
    }

    .analytics-table td {
        padding: 8px;
    }

    .analytics-table tr:nth-child(even) {
        background-color: #E8F0FE;
    }

    .analytics-table tr:nth-child(odd) {
        background-color: white;
    }
    </style>
    """

    # Build table
    table_html += "<table class='analytics-table'>"

    # Header
    table_html += "<tr>"
    for col in df_display.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr>"

    # Rows
    for _, row in df_display.iterrows():
        table_html += "<tr>"
        for val in row:
            table_html += f"<td>{val}</td>"
        table_html += "</tr>"

    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("### Total Views")

    st.metric("Views", df["views"].sum())

    st.markdown("### Platform Performance")

    chart = df.groupby("platform")["views"].sum()

    st.bar_chart(chart)
