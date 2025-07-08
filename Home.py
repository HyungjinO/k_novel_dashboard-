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


# --- 3. Sidebar Navigation ---
hide_pages_nav = """
<style>
    div[data-testid="stSidebarNav"] {
        display: none;
    }
</style>
"""
st.markdown(hide_pages_nav, unsafe_allow_html=True)

with st.sidebar:
    st.title("K-소설 해외진출 나침반 🧭")
    # Add new homepage link at the top
    st.page_link("Home.py", label="대시보드 홈")
    st.page_link("pages/1_translation.py", label="흥행 예측도서 분석")
    st.page_link("pages/2_us_market.py", label="미국 도서시장 분석")
    st.page_link("pages/3_domestic_market.py", label="한국 도서시장 현황")
    st.divider()

# --- 4. Main Title & Intro ---
st.title("한국소설 번역 시장 인텔리전스 플랫폼")
st.markdown("""
- 데이터 기반으로 한국소설의 번역 가능성과 해외 시장 적합도를 정량적으로 분석합니다.
- 잠재력 있는 작품을 선제적으로 발굴하고, 전략적 해외 진출을 지원하는 통합 대시보드를 만나보세요.
""")

# --- 5. Bookshelf Image and Overlay Buttons ---
st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
st.image("images/bookshelf.png", use_container_width=True, width=900)  

# --- 6. Overlay Buttons using Columns ---
# Adjust the column ratios to match the book positions visually
col0, col1, col2, col3 = st.columns([0.45, 1, 1, 1])

# --- 7. Book Button Handler ---
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

def select_book(book):
    st.session_state.selected_book = book

# Center the buttons in each column using markdown
with col1:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("🔴 흥행 예측도서 분석", key="btn_red", help="흥행 예측도서 분석 대시보드 정보 확인하기"):
        select_book("red")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("🟡 미국 도서시장 분석", key="btn_yellow", help="미국 도서시장 분석 대시보드 정보 확인하기"):
        select_book("yellow")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("🟢 한국 도서시장 현황", key="btn_green", help="한국 도서시장 현황 대시보드 정보 확인하기"):
        select_book("green")
    st.markdown('</div>', unsafe_allow_html=True)


# --- 8. Dashboard Info Cards ---
content = {
    "red": {
        "📊 대시보드 구성": """- 흥행 예측도서의 비율 및 흥행예측 지수 시각화
- 주요 장르 필터링 기능 및 순위 기반 흥행 예측도서 리스트 제공
- 흥행 예측도서 순위 지표 설명: 판매지수, 뉴욕타임즈 베스트셀러와의 유사도, K-콘텐츠 적합도 등""",
        "💡 활용 방법": """- 흥행 예측도서 중 번역 및 수출 우선순위 도서를 객관적 수치로 선별
- 특정 장르/작가군의 해외 반응 가능성 예측
- 출판사별 번역 성과 비교 및 전략 수립 참고
"""
    },
    "yellow": {
        "📊 대시보드 구성": """- 미국 베스트셀러 장르 분석 및 평점 비교
- 현지 독자 감정 분석 및 리뷰 키워드 추출
- 마케팅 문구 스타일 및 빈도 비교""",
        "💡 활용 방법": """- 미국 시장에서 유망한 장르 및 독자 취향 파악
- 현지 리뷰 감정을 기반으로 번역/출간 전략 설계
- 미국 도서시장 동향 분석에 따른 K-소설 전략 도출"""
    },
    "green": {
        "📊 대시보드 구성": """- 국내 흥행도서 순위 및 판매지수 분석
- 인기 K-콘텐츠 장르 분포 시각화
- 주요 출판사별 흥행 도서 출간 비율 제공""",
        "💡 활용 방법": """- 국내 흥행 도서를 기반으로 해외 진출 후보 도서 선정
- K-콘텐츠 인기 흐름과 문학 트렌드 파악
- 출판사 포트폴리오 진단 및 수출 전략 보완"""
    }
}

if st.session_state.selected_book:
    st.divider()
    book_label = {
        "red": "흥행 예측도서 분석",
        "yellow": "미국 도서시장 분석",
        "green": "한국 도서시장 현황"
    }
    st.markdown(f"#### <span style='color:#588157; font-weight:700;'>{book_label[st.session_state.selected_book].capitalize()} 대시보드 정보</span>", unsafe_allow_html=True)
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
            st.markdown("#### 📊 대시보드 구성")
            st.write(content[st.session_state.selected_book]["📊 대시보드 구성"])


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
            st.markdown("#### 💡 활용 방법")
            st.write(content[st.session_state.selected_book]["💡 활용 방법"])

else:
    st.info("위의 버튼 중 하나를 클릭하여 대시보드 구성 및 활용 방법을 확인하세요.")