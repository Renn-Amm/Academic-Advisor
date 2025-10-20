"""
Modern UI Styles for AI Academic Advisor
Clean, professional design without emojis
"""

MODERN_CSS = """
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    /* Cards */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .course-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 3px solid #4facfe;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e0e7ff;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Success/Info/Warning/Error Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left-width: 4px;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Chat Messages */
    .chat-message {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 3px solid #4facfe;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: none;
        border-right: 3px solid #764ba2;
        text-align: right;
    }
    
    /* Badge Styles */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-enrolled {
        background: #10b981;
        color: white;
    }
    
    .badge-audit {
        background: #6b7280;
        color: white;
    }
    
    .badge-beginner {
        background: #3b82f6;
        color: white;
    }
    
    .badge-intermediate {
        background: #f59e0b;
        color: white;
    }
    
    .badge-advanced {
        background: #ef4444;
        color: white;
    }
    
    /* Stats Display */
    .stat-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid #667eea;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
"""

def apply_modern_styles():
    """Apply modern CSS styles"""
    import streamlit as st
    st.markdown(MODERN_CSS, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = ""):
    """Render modern header"""
    import streamlit as st
    html = f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_section_header(text: str):
    """Render section header"""
    import streamlit as st
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

def render_stat_box(value: str, label: str):
    """Render stat box"""
    import streamlit as st
    html = f"""
    <div class="stat-box">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "default"):
    """Render badge"""
    return f'<span class="badge badge-{badge_type}">{text}</span>'
