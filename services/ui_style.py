import streamlit as st

def apply_sidebar_style():

    # ===== SIDEBAR TOP (LOGO + TITLE) =====
    with st.sidebar:

        # ✅ ADD LOGO HERE
        import base64

        with open("assets/logo.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <div style="text-align:center; padding:10px 0;">
                <img src="data:image/png;base64,{encoded}" width="180">
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<h2 style='text-align:center; color:#60A5FA;'>Signaasat CRM Tool</h2>",
            unsafe_allow_html=True
        )

        st.markdown("---")
          
    # ===== CSS =====
    st.markdown("""
    <style>
    
    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1E3D 0%, #08142B 100%);
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Sidebar links */
    [data-testid="stSidebarNav"] a {
        color: #E5E7EB !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 15px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
        display: block !important;
    }
    
    /* Remove first item */
    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }
    
    /* Hover */
    [data-testid="stSidebarNav"] a:hover {
        background-color: #FFDE21 !important;
    }
    
    /* Active */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #2563EB !important;
        font-weight: 700 !important;
    }
    
    /* Sub-items */
    [data-testid="stSidebarNav"] ul li a[href*="."] {
        padding-left: 30px !important;
        font-size: 14px !important;
        color: #CBD5F5 !important;
    }
    
    /* ===== REMOVE STREAMLIT BRANDING ===== */
    
    /* Top header (Fork / GitHub / menu) */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* "Hosted with Streamlit" badge */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Footer */
    footer {
        display: none !important;
    }
    
    /* Hamburger menu */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Toolbar (extra safety) */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* Remove extra space after header */
    .block-container {
        padding-top: 1rem !important;
    }
    
    </style>
    """, unsafe_allow_html=True)
