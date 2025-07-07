import streamlit as st

def apply_custom_style(theme="Light"):
    if theme == "Light":
        css_variables = """
            --primary-color: #588157; --background-color: #F4F4F4; --secondary-background-color: #FFFFFF;
            --text-color: #2E2E2E; --secondary-text-color: #666666; --widget-background-color: #F0F2F6;
            --sidebar-background-color: #588157; --sidebar-text-color: #FFFFFF; --sidebar-hover-color: #3A5A40;
        """
    else: # Dark Theme
        css_variables = """
            --primary-color: #A3B18A; --background-color: #0E1117; --secondary-background-color: #161B22;
            --text-color: #FAFAFA; --secondary-text-color: #A0A0A0; --widget-background-color: #262730;
            --sidebar-background-color: #1f3d20; --sidebar-text-color: #E0E0E0; --sidebar-hover-color: #395a3b;
        """

    custom_css = f"""
    <style>
        :root {{ {css_variables} }}
        .stApp, .stApp > header {{ background-color: var(--background-color); }}
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp .stMarkdown, .stApp .stMetricLabel {{ color: var(--text-color); }}
        
        /* FORCE KEYUP INPUT TO WHITE BACKGROUND WITH BLACK TEXT */
        .stTextInput > div > div > input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #588157 !important;
        }}
        .stTextInput label {{
            color: #2E2E2E !important;
        }}
        
        /* FORCE PILLS TO WHITE BACKGROUND WITH BLACK TEXT */
        [data-testid="stPills"] button {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #588157 !important;
        }}
        [data-testid="stPills"] button span {{
            color: #000000 !important;
        }}
        [data-testid="stPills"] button[aria-pressed="true"] {{
            background-color: #588157 !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stPills"] button[aria-pressed="true"] span {{
            color: #FFFFFF !important;
        }}
        
        /* FORCE DATAFRAME TO WHITE BACKGROUND WITH BLACK TEXT */
        .stDataFrame {{
            background-color: #FFFFFF !important;
        }}
        .stDataFrame [data-testid="stDataFrameResizable"] {{
            background-color: #FFFFFF !important;
        }}
        .stDataFrame table {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        .stDataFrame th {{
            background-color: #F0F2F6 !important;
            color: #000000 !important;
        }}
        .stDataFrame td {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        .stDataFrame thead tr th {{
            background-color: #F0F2F6 !important;
            color: #000000 !important;
        }}
        .stDataFrame tbody tr td {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        
        /* FORCE RADIO BUTTONS TO BLACK TEXT */
        .stRadio [role="radiogroup"] label {{
            color: #000000 !important;
        }}
        .stRadio [role="radiogroup"] label span {{
            color: #000000 !important;
        }}
        .stRadio div[role="radiogroup"] div label {{
            color: #000000 !important;
        }}
        .stRadio div[role="radiogroup"] div label span {{
            color: #000000 !important;
        }}
        
        /* FORCE RADIO BUTTON TITLE TO BLACK TEXT */
        .stRadio > label {{
            color: #000000 !important;
        }}
        .stRadio > label span {{
            color: #000000 !important;
        }}
        
        /* FORCE ALL MARKDOWN TEXT TO BLACK */
        [data-testid="stMarkdownContainer"] p {{
            color: #000000 !important;
        }}
        [data-testid="stMarkdownContainer"] span {{
            color: #000000 !important;
        }}
        
        /* FORCE SELECTBOX TO WHITE BACKGROUND WITH BLACK TEXT */
        .stSelectbox > div > div {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        .stSelectbox label {{
            color: #000000 !important;
        }}
        
        /* FORCE TABS TO BLACK TEXT */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: #FFFFFF;
        }}
        .stTabs [data-baseweb="tab-list"] button {{
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }}
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
            color: #588157 !important;
            border-bottom: 2px solid #588157 !important;
        }}
        .stTabs [data-baseweb="tab-list"] button span {{
            color: #000000 !important;
        }}
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] span {{
            color: #588157 !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            width: 260px !important;
            background-color: var(--sidebar-background-color) !important;
        }}
        [data-testid="stSidebar"] * {{
            color: var(--sidebar-text-color) !important;
        }}
        
        /* Cards */
        .content-card {{
            background-color: var(--secondary-background-color);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
            border: 1px solid #e0e0e0;
        }}
        
        .metric-card {{
            background-color: var(--secondary-background-color);
            border: 1px solid var(--primary-color);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .metric-card-label {{
            font-size: 16px;
            color: var(--secondary-text-color);
            line-height: 1.3;
            margin-bottom: 8px;
        }}
        .metric-card-value {{
            font-size: 36px;
            font-weight: bold;
            color: var(--primary-color);
        }}
        
        /* Details card */
        .details-card-window {{
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            padding: 2rem;
            min-height: 600px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .details-card-content {{
            text-align: center;
            width: 100%;
        }}
        .details-card-img-wrap {{
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: center;
        }}
        .details-card-img {{
            max-width: 150px;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .details-card-title {{
            font-size: 1.8em;
            font-weight: 700;
            color: var(--text-color) !important;
            margin-bottom: 1.5rem;
            line-height: 1.3;
        }}
        .details-card-meta {{
            margin-bottom: 0.8rem;
            color: var(--text-color);
            font-size: 1.1em;
        }}
        .details-card-desc {{
            font-size: 1em;
            color: var(--secondary-text-color);
            margin-top: 1.5rem;
            text-align: justify;
            line-height: 1.6;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }}
        
        /* BSR book cards */
        .bsr-book-card {{
            display: flex;
            align-items: center;
            padding: 1rem;
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            height: 120px;
            border: 1px solid #f0f0f0;
            margin-bottom: 1rem;
        }}
        .bsr-book-image {{
            flex-shrink: 0;
            width: 70px;
            margin-right: 1.2rem;
        }}
        .bsr-book-image img {{
            width: 100%;
            height: 95px;
            object-fit: cover;
            border-radius: 4px;
        }}
        .bsr-book-info {{
            flex-grow: 1;
            overflow: hidden;
        }}
        .bsr-book-title {{
            font-weight: bold;
            font-size: 1em;
            color: var(--text-color);
            margin-bottom: 0.3rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .bsr-book-author, .bsr-book-rank {{
            font-size: 0.9em;
            color: var(--secondary-text-color);
        }}

        /* US Market page styles */
        .nyt-book-card {{
            display: flex;
            align-items: center;
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #f0f0f0;
            height: 150px;
            margin-bottom: 1rem;
        }}
        .nyt-book-image {{
            flex-shrink: 0;
            width: 80px;
            margin-right: 1.2rem;
        }}
        .nyt-book-image img {{
            width: 100%;
            height: 120px;
            object-fit: cover;
            border-radius: 4px;
        }}
        .nyt-book-info {{
            flex-grow: 1;
            overflow: hidden;
        }}
        .nyt-book-title {{
            font-weight: bold;
            font-size: 1.1em;
            color: var(--text-color);
            margin-bottom: 0.3rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .nyt-book-author {{
            font-size: 0.9em;
            color: var(--secondary-text-color);
            margin-bottom: 0.3rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .nyt-book-reviews {{
            font-size: 0.9em;
            color: var(--secondary-text-color);
        }}
        .star-rating {{
            color: #FFC700;
            font-size: 1.1em;
            letter-spacing: 2px;
            margin-bottom: 0.4rem;
        }}
        
        /* Persona styles */
        div[data-testid="stImage"] {{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        .persona-name-card {{
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            font-size: 1.3em;
            margin-bottom: 1.5rem;
        }}
        .persona-detail-label {{
            font-weight: bold;
            color: var(--text-color);
            font-size: 1.05em;
            margin-top: 1rem;
        }}
        .persona-detail-text {{
            color: var(--secondary-text-color);
            font-size: 1em;
            margin-left: 0.5rem;
            padding-bottom: 0.5rem;
        }}
        .keyword-tag {{
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 4px;
            display: inline-block;
            font-size: 0.9em;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
