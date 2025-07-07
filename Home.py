import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from utils.style import apply_custom_style

# --- 1. Theme & Page Config ---
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

st.set_page_config(
    page_title="대시보드 홈",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_style(st.session_state.theme)

# --- 2. Custom Sidebar Style (color & width) ---
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #588157 !important;
        color: #fff !important;
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    [data-testid="stSidebar"] .css-1d391kg {
        color: #fff !important;
    }
    [data-testid="stSidebar"] .css-1v0mbdj, [data-testid="stSidebar"] .css-1v0mbdj * {
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Sidebar Navigation ---
with st.sidebar:
    st.title("K-소설 해외진출 나침반")
    st.page_link("Home.py", label="대시보드 홈")
    st.page_link("pages/1_translation.py", label="흥행 예측도서 분석")
    st.page_link("pages/2_us_market.py", label="미국 도서시장 분석")
    st.page_link("pages/3_domestic_market.py", label="한국 도서시장 현황")
    st.divider()

# --- 4. Main Title & Intro ---
st.title("대시보드 구성 및 활용 방법 간략 안내")
st.markdown("""
이 페이지는 대시보드의 간략한 개요와 활용 방법을 제공합니다.  
아래 책 이미지를 클릭하여 각 대시보드로 이동하고, 구성 및 활용 방법을 확인하세요.
""")

# --- 5. Bookshelf Image and Overlay Buttons ---
st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
st.image("images/bookshelf.png", use_container_width=True)  # No deprecation warning

# --- 6. Overlay Buttons using Columns ---
# Adjust the column ratios to match the book positions visually
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

# --- 7. Book Button Handler ---
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

def select_book(book):
    st.session_state.selected_book = book

with col2:
    st.button("🔴 빨간 책 (Home)", key="btn_red", help="번역 현황 및 우선순위 대시보드로 이동", on_click=select_book, args=("red",))
with col3:
    st.button("🟡 노란 책 (US Market)", key="btn_yellow", help="미국 도서시장 분석 대시보드로 이동", on_click=select_book, args=("yellow",))
with col4:
    st.button("🟢 초록 책 (Domestic Market)", key="btn_green", help="국내 도서시장 분석 대시보드로 이동", on_click=select_book, args=("green",))

# --- 8. Book Legend (below image) ---
st.markdown("""
<div style="display: flex; justify-content: center; gap: 28px; margin-top: 10px; margin-bottom: 18px;">
    <span style="display: flex; align-items: center; gap: 6px;">
        <span style="width:18px; height:18px; border-radius:50%; background:#ff6f61; display:inline-block;"></span>
        <span style="color:#555;">빨간 책 (Home)</span>
    </span>
    <span style="display: flex; align-items: center; gap: 6px;">
        <span style="width:18px; height:18px; border-radius:50%; background:#ffe066; display:inline-block; border:1px solid #d5c100;"></span>
        <span style="color:#555;">노란 책 (US Market)</span>
    </span>
    <span style="display: flex; align-items: center; gap: 6px;">
        <span style="width:18px; height:18px; border-radius:50%; background:#74c69d; display:inline-block;"></span>
        <span style="color:#555;">초록 책 (Domestic Market)</span>
    </span>
</div>
""", unsafe_allow_html=True)

# --- 9. Dashboard Info Cards ---
content = {
    "red": {
        "대시보드 구성": "Home.py 대시보드는 번역 현황 및 우선순위 데이터를 시각화합니다.",
        "활용 방법": "이 대시보드를 통해 번역 진행 상황과 우선순위를 쉽게 파악할 수 있습니다."
    },
    "yellow": {
        "대시보드 구성": "미국 도서시장 분석 페이지는 미국 시장의 도서 트렌드와 리뷰를 분석합니다.",
        "활용 방법": "미국 시장 진출 전략 수립에 필요한 인사이트를 제공합니다."
    },
    "green": {
        "대시보드 구성": "국내 도서시장 분석 페이지는 국내 시장의 판매지수와 유사도 분석을 포함합니다.",
        "활용 방법": "국내 시장 동향을 이해하고 마케팅 전략 수립에 활용할 수 있습니다."
    }
}

if st.session_state.selected_book:
    st.divider()
    book_label = {
        "red": "빨간",
        "yellow": "노란",
        "green": "초록"
    }
    st.markdown(f"#### <span style='color:#588157; font-weight:700;'>{book_label[st.session_state.selected_book].capitalize()} 책 대시보드 정보</span>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        with stylable_container(
            key="left_card",
            css_styles="""
                border: 1px solid #ccc;
                border-radius: 15px;
                padding: 20px;
                background-color: #f9f9f9;
                margin-bottom: 18px;
            """
        ):
            st.markdown("#### 대시보드 구성")
            st.write(content[st.session_state.selected_book]["대시보드 구성"])

    with col_right:
        with stylable_container(
            key="right_card",
            css_styles="""
                border: 1px solid #ccc;
                border-radius: 15px;
                padding: 20px;
                background-color: #f0f8ff;
                margin-bottom: 18px;
            """
        ):
            st.markdown("#### 활용 방법")
            st.write(content[st.session_state.selected_book]["활용 방법"])
else:
    st.info("위의 책 중 하나를 클릭하여 대시보드 구성 및 활용 방법을 확인하세요.")
