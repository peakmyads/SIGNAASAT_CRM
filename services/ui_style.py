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
    st.markdown("""
    <style>

    /* Hide top header (Fork / GitHub / menu) */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Hide "Hosted with Streamlit" badge */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Hide footer */
    footer {
        display: none !important;
    }

    /* Hide hamburger menu */
    #MainMenu {
        visibility: hidden;
    }

    /* Remove top spacing after header removal */
    .block-container {
        padding-top: 1rem !important;
    }

    /* Extra safety (covers newer UI changes) */
    div[data-testid="stToolbar"] {
        display: none !important;
    }

    </style>
    """, unsafe_allow_html=True)


    
