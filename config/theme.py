"""Theme configuration for Streamlit app."""
import streamlit as st
from config.settings import APP_NAME, APP_ICON, DEFAULT_THEME, LAYOUT

def apply_theme():
    """Apply custom theme to Streamlit app."""
    st.set_page_config(
        page_title=f"{APP_ICON} {APP_NAME}",
        page_icon=APP_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded",
        theme=DEFAULT_THEME
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    /* Main colors */
    :root {
        --primary: #6366F1;
        --secondary: #EC4899;
        --success: #10B981;
        --danger: #EF4444;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    
    /* Button hover effect */
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)
