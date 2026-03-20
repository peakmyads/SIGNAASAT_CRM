import streamlit as st

def apply_sidebar_style():

    # ===== SIDEBAR TOP (LOGO + TITLE) =====
    with st.sidebar:
        
        st.markdown(
            "<h2 style='text-align:left; color:#60A5FA;'>Signaasat CRM</h2>",
            unsafe_allow_html=True
        )

        st.markdown("---")
    
    # ===== CSS =====
    st.markdown("""
    <style>

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1E3D 0%, #08142B 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebarNav"] a {
        color: #E5E7EB !important;
        font-size: 15px !important;
        font-weight: 600 !important;   /* 👈 ADD THIS */
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        display: block !important;
    }
    
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background-color: #FFDE21 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #2563EB !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebarNav"] ul li a {
        padding-left: 15px !important;
    }

    /* Sub-items (with dot numbering like 1.1, 2.1) */
    [data-testid="stSidebarNav"] ul li a[href*="."] {
        padding-left: 30px !important;
        font-size: 14px !important;
        color: #CBD5F5 !important;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
