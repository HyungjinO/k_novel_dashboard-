# 국내 도서시장 분석 페이지
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
from collections import Counter

# 데이터 로딩 및 스타일 함수는 프로젝트 환경에 맞게 import
from utils.data_loader import load_data
from utils.style import apply_custom_style

# --- 1. 테마 상태 및 스타일 적용 ---
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

st.set_page_config(
    page_title="K-소설 해외진출 나침반",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_style(st.session_state.theme)

# --- 2. CSS 스타일 및 네비게이션 숨김 ---
st.markdown("""
<style>
div[data-testid="stSidebarNav"] { display: none; }
.metric-card {
    background: #F8F8F8;
    border: 2px solid #588157;
    color: #588157;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 5px;
    position: relative;
    min-height: 90px;
}
.metric-card-label {
    font-size: 18px;
}
.metric-card-value {
    font-size: 28px;
    font-weight: bold;
}
.metric-tooltip {
    visibility: hidden;
    opacity: 0;
    width: 400px;
    background: #222;
    color: #fff;
    text-align: left;
    border-radius: 8px;
    padding: 8px 12px;
    position: absolute;
    z-index: 10;
    left: 50%;
    top: 110%;
    transform: translateX(-50%);
    transition: opacity 0.2s;
    font-size: 0.95em;
    pointer-events: none;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.metric-card:hover .metric-tooltip {
    visibility: visible;
    opacity: 1;
    pointer-events: auto;
}
.book-item-compact {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: #f9f9f9;
    border-radius: 14px;
    padding: 14px 16px;
    border: 1px solid #e0e0e0;
    margin-bottom: 12px;
}
.book-image-small img {
    width: 90px; height: auto; border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.book-text-info { flex: 1; }
.book-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 2px; }
.book-author, .book-bsr { font-size: 0.95rem; color: #666; }
</style>
""", unsafe_allow_html=True)


#사이드바 숨기기
hide_pages_nav = """
<style>
    div[data-testid="stSidebarNav"] {
        display: none;
    }
</style>
"""
st.markdown(hide_pages_nav, unsafe_allow_html=True)

# --- 3. 사이드바 ---
with st.sidebar:
    st.title("K-소설 해외진출 나침반 🧭")
    # Add new homepage link at the top
    st.page_link("Home.py", label="대시보드 홈")
    st.page_link("pages/1_translation.py", label="흥행 예측도서 분석")
    st.page_link("pages/2_us_market.py", label="미국 도서시장 분석")
    st.page_link("pages/3_domestic_market.py", label="한국 도서시장 현황")
    st.divider()


# --- 4. 데이터 로딩 ---
df_ranked = load_data('흥행예측도서_ranked.csv')
df_translated = load_data('trans_final_with_url.csv')
df_book_korean = load_data('book_korean.csv')
df_nyb = load_data('nyt_bestseller_with_keyword.csv')
df_imdb = load_data('imdb_llm_filtered_final.csv')

if 'selected_book_isbn' not in st.session_state:
    st.session_state.selected_book_isbn = None

# --- 5. 페이지 타이틀 ---
st.title("한국 도서시장 현황")
st.divider()

# --- 6. 메트릭 카드 (툴팁 포함) ---
st.subheader("국내시장 핵심 지표")

# --- NEW: Add a button to toggle all expanders ---
if 'expand_all_metrics' not in st.session_state:
    st.session_state.expand_all_metrics = False

if st.button("지표 설명 모두 보기/접기", key="domestic_expand"):
    st.session_state.expand_all_metrics = not st.session_state.expand_all_metrics

# --- REVISED: Add expander content to the metrics list ---
if not df_ranked.empty and not df_book_korean.empty:
    avg_salespoint_success = df_ranked['salespoint'].mean()
    hit_isbns = df_ranked['ISBN'].unique()
    df_not_hit = df_book_korean[~df_book_korean['ISBN'].isin(hit_isbns)]
    avg_salespoint_miss = df_not_hit['salespoint'].mean()
    avg_salespoint_all = df_book_korean['salespoint'].mean()
else:
    avg_salespoint_success, avg_salespoint_miss, avg_salespoint_all = 0, 0, 0

if not df_ranked.empty and not df_translated.empty and not df_book_korean.empty:
    translated_count = df_translated['ISBN_K'].nunique()
    untranslated_count = df_book_korean['ISBN'].nunique()
    total_books = translated_count + untranslated_count
    translation_percentage = (translated_count / total_books) * 100 if total_books > 0 else 0
    avg_final_score = df_ranked['fuzzy_topsis_score'].mean()
    avg_salespoint = df_translated['salespoint'].mean()
    book_kor_salespoint = df_book_korean['salespoint'].mean()
    translated_salespoint = df_translated['salespoint'].mean()
    avg_similarity = df_translated['top_1_similarity'].mean()
    trans_success = df_translated[df_translated['success'] == 1]['ISBN'].nunique()
    trans_fail = df_translated[df_translated['success'] == 0]['ISBN'].nunique()
    trans_success_percentage = (trans_success / (trans_success + trans_fail)) * 100
    book_korean_imdb_maxs = df_book_korean['max_imdb_similarity'].mean()
else:
    translation_percentage, avg_final_score, avg_salespoint, avg_similarity = 0, 0, 0, 0

per_success = 20.92391304348 
metrics = [
    {
        "label": "번역도서 해외 흥행률",
        "value": f"{per_success:.2f}%",
        "expander": """
        - **설명:** 해외에서 인기도서로 선정된 한국도서를 Amazon BSR(아마존 베스트셀러 순위) 기준으로 평가한 지수입니다.
        - **의미:** 번역된 한국 도서 중 BSR 순위가 상위 10% 이내인 도서를 ‘해외 흥행’으로 간주합니다.
        """
    },
    {
        "label": "한국도서 평균 판매지수",
        "value": f"{book_kor_salespoint:,.0f} pts",
        "expander": """
        - **설명:** 알라딘에서 각 도서의 인기도와 판매 추이를 수치로 나타내는 고유한 판매 지수입니다.
        - **의미:** 판매지수가 높을수록 시장 반응이 좋음을 의미합니다.
        """
    },
    {
        "label": "번역도서 평균 판매지수",
        "value": f"{translated_salespoint:,.0f} pts",
        "expander": """
        - **설명:** 알라딘에서 번역된 도서들의 인기도와 판매 추이를 수치로 나타내는 고유한 판매 지수입니다.
        - **의미:** 판매지수가 높을수록 시장 반응이 좋음을 의미합니다.
        """
    },
    {
        "label": "해외 인기도서 평균 유사도",   #**여기 변경 
        "value": "0.64 / 1",
        "expander": """
        - **설명:** 해외 인기 도서의 설명에 포함된 장르, 배경, 캐릭터, 분위기, 전개 등 도서 내용 및 의미와 국내 도서의 유사한 정도를 수치화한 지수입니다.
        - **의미:** 값이 1에 가까울수록 두 책이 매우 비슷함을, 0에 가까울수록 상이한 특성을 지님을 의미합니다.
        """
    }
]
cols = st.columns(len(metrics))
for i, metric in enumerate(metrics):
    with cols[i]:
        st.markdown(
            f'''
            <div class="metric-card">
                <div class="metric-card-label">{metric["label"]}</div>
                <div class="metric-card-value">{metric["value"]}</div>
            </div>
            ''', unsafe_allow_html=True
        )
        # --- NEW: Add the expander for each metric ---
        with st.expander("설명 보기", expanded=st.session_state.get('expand_all_metrics', False)):
            st.markdown(metric["expander"])


# --- 7. 인기 도서 & 분석 ---

# --- Step 1: Define the required CSS styles locally ---
st.markdown("""
<style>
.bsr-book-card {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    height: 168px; /* Increased height for more content */
    border: 1px solid #f0f0f0;
    margin-bottom: 1rem;
}
.bsr-book-image {
    flex-shrink: 0;
    width: 70px;
    margin-right: 1.2rem;
}
.bsr-book-image img {
    width: 100%;
    height: 95px;
    object-fit: cover;
    border-radius: 4px;
}
.bsr-book-info {
    flex-grow: 1;
    overflow: hidden;
}
.bsr-book-title {
    font-weight: bold;
    font-size: 1em;
    color: #2E2E2E;
    margin-bottom: 0.3rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bsr-book-author, .bsr-book-rank {
    font-size: 0.9em;
    color: #666666;
}
</style>
""", unsafe_allow_html=True)


col_bsr, col_trend = st.columns([1.4, 1], gap="large")

with col_bsr:
    with stylable_container(key="bestseller_card", css_styles=".content-card { min-height: 600px; }"):
        st.subheader("한국도서 인기순위")
        if "salespoint" in df_book_korean.columns:
            salespoint_df = df_book_korean.sort_values(by="salespoint", ascending=False).head(6)
        else:
            st.warning("'salespoint' 컬럼이 데이터에 없습니다.")
            salespoint_df = df_book_korean.head(6)

        # --- Step 2: Update the function to use the correct classes ---
        def display_book_item(row):
            # Format similarity score to 2 decimal places
            imdb_sim = row.get('max_imdb_similarity', 'N/A')
            if isinstance(imdb_sim, (int, float)):
                imdb_sim = f"{imdb_sim:.2f}"

            return f"""
                <div class="bsr-book-card">
                    <div class="bsr-book-image">
                        <img src="{row.get("image_url", "")}" alt="Book Cover">
                    </div>
                    <div class="bsr-book-info">
                        <div class="bsr-book-title" title="{row.get('제목', 'N/A')}">{row.get('제목', 'N/A')}</div>
                        <div class="bsr-book-author">작가: {row.get('저자', 'N/A')}</div>
                        <div class="bsr-book-author">출판사: {row.get('출판사', 'N/A')}</div>
                        <div class="bsr-book-rank">판매지수: {row.get('salespoint', 0):,.0f}</div>
                    </div>
                </div>
            """

        # --- Step 3: Use a cleaner loop to display the items ---
        book_cols = st.columns(2)
        for i, row in salespoint_df.reset_index().iterrows():
            with book_cols[i % 2]:
                st.markdown(display_book_item(row), unsafe_allow_html=True)

with col_trend:
    with stylable_container(key="trend_card_1", css_styles="""
        .content-card { min-height: 600px; background: #f9f9f9; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 24px; }
    """):
        st.subheader("국내 인기 작가")
        author_col = '저자'
        if author_col in df_book_korean.columns and 'salespoint' in df_book_korean.columns:
            author_sales = (
                df_book_korean
                .groupby(author_col)['salespoint']
                .sum()
                .reset_index()
                .sort_values(by='salespoint', ascending=False)
            )
            author_sales.columns = ['저자', '총 판매지수']
            top_authors = author_sales.head(15)
            
            fig = px.bar(
                top_authors.sort_values('총 판매지수', ascending=True),
                x='총 판매지수',
                y='저자',
                orientation='h',
                text='총 판매지수',
                color='총 판매지수',  # 값에 따라 색상 그라데이션
                color_continuous_scale = ["#e0f2e9","#a3c9a8", "#7fb77e", "#568955", "#355c36"],
                labels={'총 판매지수': '총 판매지수', '저자': '저자'},
            )
            fig.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside',
                textfont=dict(color='#222', size=16)
            )
            fig.update_layout(
                title_text='',
                yaxis={'categoryorder':'total ascending'},
                showlegend=False,
                height=600,
                plot_bgcolor='#f9f9f9',
                paper_bgcolor='#f9f9f9',
                font=dict(color='#222', size=18),
                title_font=dict(color='#222', size=22),
                coloraxis_showscale=False  # 컬러바(색상축) 숨기기
            )
            fig.update_yaxes(tickfont=dict(color='#222', size=16))
            fig.update_xaxes(tickfont=dict(color='#222', size=16))
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "scrollZoom": True,
                    "displayModeBar": True,
                    "displaylogo": False
                }
            )
        else:
            st.warning("'저자' 또는 'salespoint' 컬럼을 찾을 수 없습니다.")

st.divider()


st.title("한국소설 해외 동향")
st.divider()

#Row 3 추가 (page 1에 있는 부분 추가)
col_bsr, col_trend = st.columns([1, 1], gap="large")
with col_bsr:
    st.subheader("해외 독자가 선택한 한국 도서 베스트")
    bsr_df = df_translated.sort_values(by='avg_bsr', ascending=True).head(6)
    
    # FIXED: Remove stylable_container wrapper to avoid double cards
    book_cols = st.columns(2)
    for i, row in bsr_df.reset_index().iterrows():
        with book_cols[i % 2]:
            st.markdown(f"""
                <div class="bsr-book-card">
                    <div class="bsr-book-image"><img src="{row.get("book_image", "")}" alt="Book Cover"></div>
                    <div class="bsr-book-info">
                        <div class="bsr-book-title" title="{row.get('Title', 'N/A')}">{row.get('Title', 'N/A')}</div>
                        <div class="bsr-book-author">작가: {row.get('Author', 'N/A')}</div>
                        <div class="bsr-book-rank">평균 BSR: {row.get('avg_bsr', 0):,.0f}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            
with col_trend:
    with stylable_container(key="trend_card_2", css_styles="""
        .content-card { min-height: 600px; background: #f9f9f9; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 24px; }
    """):
        st.subheader("출판연도별 해외 흥행 추이")
        if 'success' in df_translated.columns and 'Published Year' in df_translated.columns:
            trend_data = df_translated[df_translated['success'] == 1]['Published Year'].value_counts().sort_index()
            fig_trend = px.bar(
                x=trend_data.index,
                y=trend_data.values,
                labels={'x': '출판 연도', 'y': '흥행한 도서의 총합'},
                color_discrete_sequence=["#568955"],
                title=""
            )
            fig_trend.update_layout(
                title_text='',
                coloraxis_showscale=False,
                template=None,
                paper_bgcolor='#f9f9f9',
                plot_bgcolor='#f9f9f9',
                font_color='#222',
                title_font_color='#222',
                height=530
            )
            fig_trend.update_xaxes(tickfont_color='#222', titlefont_color='#222')
            fig_trend.update_yaxes(tickfont_color='#222', titlefont_color='#222')
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("'success' 또는 'Published Year' 컬럼을 찾을 수 없습니다.")

# 장르 분석 파트 생성
genre_kor_map = {
    'Thriller': '스릴러', 'Mystery': '미스터리', 'Crime Fiction': '범죄소설', 'Suspense': '서스펜스', 'Romance': '로맨스',
    'Fantasy': '판타지', 'Magical Realism': '마술적 사실주의', 'Mythic Fiction': '신화소설', 'Adventure': '모험',
    'Historical Fiction': '역사소설', 'Historical & Political Fiction': '역사/정치소설', 'Science Fiction': 'SF',
    'Philosophical Fiction': '철학소설', 'Contemporary Fiction': '현대소설', 'Literary Fiction': '문학소설',
    'Family_Saga': '가족서사', 'Coming-of-Age': '성장소설' 
}
plot_kor_map = {
    'survival': '생존', 'identity_crisis': '정체성의 혼란', 'transformation': '변화', 'coming_of_age': '성장', 'revenge': '복수',
    'rebellion': '반란', 'family_secrets': '가족의 비밀', 'forgiveness': '용서', 'curse': '저주', 'mystery_solving': '미스터리 해결',
    'love_story': '사랑 이야기', 'war': '전쟁', 'discovery': '발견', 'sacrifice': '희생', 'hero_journey': '영웅의 여정',
    'political_intrigue': '정치적 음모', 'betrayal': '배신', 'forbidden_love': '금지된 사랑', 'quest': '임무', 'exploration': '탐험',
    'redemption': '속죄', 'fish_out_of_water': '낯선 환경에서의 갈등', 'second_chance': '두 번째 기회', 'rags_to_riches': '신분 상승 이야기'
}

character_kor_map = { 
        "survivor": "생존자", "ordinary_person": "평범한 인물", "outsider": "국외자", "artist": "예술가", "student": "학생", 
        "anti_hero": "반(反)영웅", "reluctant_hero": "마지못해 영웅이 된 인물", "magic_user": "마법사", "detective": "탐정", "royalty": "왕족", 
        "spy": "스파이", "love_interest": "사랑의 대상", "teacher": "교사", "soldier": "군인", "leader": "리더", "complex_antagonist": "입체적 악역",
          "hero": "영웅", "mentor_figure": "멘토", "doctor": "의사", "journalist": "기자", "criminal": "범죄자", "scientist": "과학자", "writer": "작가" 
}

setting_kor_map = {
     "contemporary": "현대", "foreign_country": "외국", "rural": "시골", "dystopian_society": "디스토피아 사회", "magical_realm": "마법 세계", 
     "big_city": "대도시", "historical_medieval": "중세 시대", "fantasy_world": "판타지 세계", "historical_victorian": "빅토리아 시대", "historical_1920s": "1920년대", 
     "historical": "역사적 배경", "near_future": "가까운 미래", "historical_wwii": "2차 세계대전", "far_future": "먼 미래", "small_town": "소도시", "historical_1970s": "1970년대", 
     "prison": "감옥", "school_setting": "학교", "workplace": "직장", "post_apocalyptic": "포스트 아포칼립스", "historical_1950s": "1950년대", "historical_1980s": "1980년대", 
     "upper_class": "상류층", "military": "군대", "other_planet": "다른 행성", "working_class": "노동자 계급", "historical_1930s": "1930년대", "island": "섬" 
}

tone_kor_map = {
     "intense": "강렬한", "serious": "진지한", "emotional": "감정적인", "haunting": "잊혀지지 않는", "dark": "어두운", "suspenseful": "긴장감 있는", "poetic": "시적인", 
     "dramatic": "극적인", "hopeful": "희망적인", "whimsical": "기발한", "action_packed": "액션이 풍부한", "humorous": "유머러스한", "melancholic": "우울한", "uplifting": "격려하는", 
     "fast_paced": "빠른 전개", "philosophical": "철학적인", "eerie": "으스스한", "mysterious": "신비로운", "gentle": "부드러운", "nostalgic": "향수를 불러일으키는", "pessimistic": "비관적인" 
}

theme_kor_map = { 
    "survival_instinct": "생존 본능", "social_justice": "사회 정의", "personal_growth": "개인적 성장", "truth_seeking": "진실 추구", "justice": "정의", "family_bonds": "가족 유대", 
    "power_corruption": "권력의 부패", "identity_search": "정체성 탐색", "freedom": "자유", "environmental_issues": "환경 문제", "good_vs_evil": "선과 악", "belonging": "소속감",
      "cultural_clash": "문화 충돌", "technology_impact": "기술의 영향", "love_story": "사랑 이야기", "moral_dilemma": "도덕적 딜레마", "sacrifice_for_others": "타인을 위한 희생", 
      "tradition_vs_change": "전통과 변화의 갈등", "forgiveness": "용서", "love": "사랑", "legacy": "유산", "responsibility": "책임"
}

# --- 기타 이모지 매핑 ---
plot_emoji_map = {
    'survival':'🏕️', 'identity_crisis':'🎭', 'transformation':'🦋', 'coming_of_age':'🌱', 'revenge':'😠', 'rebellion':'✊', 
    'family_secrets':'🗝️', 'forgiveness':'🤝', 'curse':'🧙‍♂️', 'mystery_solving':'🕵️', 'love_story':'❤️', 'war':'⚔️', 'discovery':'💡', 
    'sacrifice':'🕊️', 'hero_journey':'🦸', 'political_intrigue':'🕴️', 'betrayal':'💔', 'forbidden_love':'🚫❤️', 'quest':'🗺️', 'exploration':'🧭',
    'redemption':'🙏', 'fish_out_of_water':'😰', 'second_chance':'🔄', 'rags_to_riches':'📈'
}

character_emoji_map = {
    'ordinary_person': '🧑', 'survivor': '💪', 'outsider': '🚶', 'reluctant_hero': '🦸', 'love_interest': '💕',
    'anti_hero': '😈', 'mentor_figure': '🧑‍🏫', 'artist': '🎨', 'student': '🎒', 'magic_user': '🧙',
    'detective': '🕵️', 'royalty': '👑', 'spy': '🕶️', 'teacher': '👩‍🏫', 'soldier': '🪖', 'leader': '🧑‍💼',
    'complex_antagonist': '🦹', 'hero': '🦸', 'doctor': '👩‍⚕️', 'journalist': '📰', 'criminal': '🚓',
    'scientist': '🔬', 'writer': '✍️'
}
theme_emoji_map = {
    'personal_growth':'🌱', 'social_justice':'⚖️', 'identity_search':'❓', 'family_bonds':'👨‍👩‍👧‍👦', 'moral_dilemma':'🤔', 
    'cultural_clash':'🌍', 'survival_instinct':'🧠', 'truth_seeking':'🔎', 'justice':'🧑‍⚖️', 'power_corruption':'🤫', 'freedom':'🕊️', 
    'environmental_issues':'🌳', 'good_vs_evil':'⚔️', 'belonging':'🫂', 'technology_impact':'🤖', 'love_story':'❤️', 'sacrifice_for_others':'🕊️', 
    'tradition_vs_change':'🔄', 'forgiveness':'🤝', 'love':'💖', 'legacy':'🏛️', 'responsibility':'👩‍⚖️'
}

setting_emoji_map = {
    'contemporary': '🌇', 'foreign_country': '✈️', 'rural': '🌾', 'dystopian_society': '🏭', 'magical_realm': '🪄',
    'big_city': '🚕', 'historical_medieval': '🏰', 'fantasy_world': '🐉', 'historical_victorian': '🎩', 'historical_1920s': '🎷',
    'historical': '📜', 'near_future': '🤖', 'historical_wwii': '💣', 'far_future': '🚀', 'small_town': '🏘️',
    'historical_1970s': '🕺', 'prison': '🚔', 'school_setting': '🏫', 'workplace': '💼', 'post_apocalyptic': '☢️',
    'historical_1950s': '🎙️', 'historical_1980s': '📼', 'upper_class': '💎', 'military': '🎖️', 'other_planet': '🪐',
    'working_class': '🔧', 'historical_1930s': '🎞️', 'island': '🏝️'
}

tone_emoji_map = {
    'intense':'🔥', 'serious':'🧐', 'emotional':'😭', 'haunting':'👻', 'dark':'🌑', 'suspenseful':'😱', 'poetic':'🖋️',
    'dramatic':'🎭', 'hopeful':'🌅', 'whimsical':'🦄', 'action_packed':'💥', 'humorous':'🤣', 'melancholic':'😔', 
    'uplifting':'🌈', 'fast_paced':'⚡', 'philosophical':'🤔', 'eerie':'🕸️', 'mysterious':'🕵️‍♂️', 'gentle':'🕊️', 'nostalgic':'📻', 'pessimistic':'🙄'}

genre_emoji_map = {
    'Thriller': '🔪', 'Mystery': '🔍', 'Crime Fiction': '⚖️', 'Suspense': '⏳', 'Romance': '❤️',
    'Fantasy': '✨', 'Magical Realism': '🧙‍♂️', 'Mythic Fiction': '🧚‍♀️', 'Adventure': '🗺️',
    'Historical Fiction': '🏛️', 'Historical & Political Fiction': '🏛️', 'Science Fiction': '🚀',
    'Philosophical Fiction': '🤔', 'Contemporary Fiction': '🏙️', 'Literary Fiction': '📖',
    'Family_Saga': '👨‍👩‍👧‍👦', 'Coming-of-Age': '🌱'
}

# --- 분석 카테고리 매핑 ---
analysis_map = {
    "장르": {"col": "primary_genre", "emoji": genre_kor_map},
    "전개": {"col": "primary_plot", "emoji": plot_emoji_map},
    "등장인물": {"col": "primary_character", "emoji": character_emoji_map},
    "주제": {"col": "primary_theme", "emoji": theme_emoji_map},
    "배경": {"col": "primary_setting", "emoji": setting_emoji_map},
    "분위기": {"col": "primary_tone", "emoji": tone_emoji_map}
}

custom_palette = [
              "#A3C9A8", "#84B1BE", "#F2D388", "#C98474", "#8E7DBE",
              "#F5B7B1", "#AED6F1", "#F9E79F", "#D7BDE2", "#A2D9CE",
              "#FADBD8", "#F5CBA7", "#D2B4DE", "#A9CCE3", "#A3E4D7"
            ]

# 카테고리별 한국어 mapping 
# --- 한글+이모지 매핑 함수 ---
def apply_kor_emoji_map(data_series, category):
    kor_map_dict = {
        "장르": genre_kor_map,
        "전개": plot_kor_map,
        "등장인물": character_kor_map,
        "주제": theme_kor_map,
        "배경": setting_kor_map,
        "분위기": tone_kor_map
    }
    emoji_map_dict = {
        "장르": genre_emoji_map,
        "전개": plot_emoji_map,
        "등장인물": character_emoji_map,
        "주제": theme_emoji_map,
        "배경": setting_emoji_map,
        "분위기": tone_emoji_map
    }
    kor_map = kor_map_dict.get(category)
    emoji_map = emoji_map_dict.get(category)
    if kor_map is not None and emoji_map is not None:
        return data_series.map(
            lambda x: f"{emoji_map.get(x, '')} {kor_map.get(x, x)}" if pd.notna(x) else x
        )
    return data_series

# --- 도넛 차트 함수 ---
def create_donut_chart(data_series, title_text, theme, category=None):
    # 한글+이모지 매핑 적용
    if category:
        data_series = apply_kor_emoji_map(data_series, category)
    if data_series.dropna().empty:
        st.info("분석할 데이터가 없습니다.")
        return
    counts = data_series.value_counts().reset_index()
    counts.columns = ['category', 'count']
    total = counts['count'].sum()
    fig = px.pie(counts, values='count', names='category', title=f"{title_text} 분포", hole=0.4, color_discrete_sequence=custom_palette)
    if theme == "Light":
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            font_color='black',
            title_font_color='black',
            legend_font_color='black',
            annotations=[dict(text=f'전체<br>{total}권', x=0.5, y=0.5, font_size=20, font_color='black', showarrow=False)]
        )
    else:
        fig.update_layout(
            width = 700,
            height= 700,
            template="plotly_dark",
            paper_bgcolor='#262730',
            plot_bgcolor='#262730',
            font_color='white',
            title_font_color='white',
            legend_font_color='white',
            annotations=[dict(text=f'전체<br>{total}권', x=0.5, y=0.5, font_size=20, font_color='white', showarrow=False)]
        )
    fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='radial')
    fig.update_layout(
        showlegend=True, legend=dict(title=title_text, yanchor="top", y=1, xanchor="left", x=1.05)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 트리맵 차트 함수 ---
def create_treemap_chart(data_series, title_text, emoji_map, theme, category=None):
    if category:
        data_series = apply_kor_emoji_map(data_series, category)
    if data_series.dropna().empty:
        st.info("분석할 데이터가 없습니다.")
        return
    counts = Counter(data_series.dropna().astype(str))
    df_treemap = pd.DataFrame(counts.items(), columns=['label', 'value'])
    df_treemap['formatted_label'] = df_treemap['label']
    color_scale = px.colors.qualitative.Pastel
    fig = px.treemap(
        df_treemap, path=[px.Constant("전체"), 'formatted_label'], values='value',
        color='label', color_discrete_sequence=custom_palette, hover_data={'value': ':,.0f'}
    )
    if theme == "Light":
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            font_color='black',
            title_font_color='black'
        )
        fig.update_traces(
            textposition='middle center', textinfo='label+value',
            insidetextfont=dict(size=18, color='black'),
            marker=dict(cornerradius=5, line=dict(width=2, color='white'))
        )
    else:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='#262730',
            plot_bgcolor='#262730',
            font_color='white',
            title_font_color='white'
        )
        fig.update_traces(
            textposition='middle center', textinfo='label+value',
            insidetextfont=dict(size=18, color='white'),
            marker=dict(cornerradius=5, line=dict(width=2, color='white'))
        )
    fig.update_layout(
        title=f"{title_text} 분포", margin=dict(t=40, l=10, r=10, b=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 버블 차트 함수 ---
def create_bubble_chart(data_series, title_text, theme, emoji_map=None, category=None):
    if category:
        data_series = apply_kor_emoji_map(data_series, category)
    if data_series.dropna().empty:
        st.info("분석할 데이터가 없습니다.")
        return
    counts = data_series.value_counts().reset_index()
    counts.columns = ['category', 'count']
    fig = px.scatter(
        counts, x='category', y='count', size='count', color='category',
        title=f"{title_text} 분포", size_max=60, color_discrete_sequence=custom_palette,
        labels={'category': title_text, 'count': '등장 횟수'}
    )
    if theme == "Light":
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor='white',
            plot_bgcolor='white',
            font_color='black',
            title_font_color='black'
        )
        fig.update_xaxes(tickfont_color='black', titlefont_color='black', title=title_text)
        fig.update_yaxes(tickfont_color='black', titlefont_color='black', title='등장 횟수')
    else:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='#262730',
            plot_bgcolor='#262730',
            font_color='white',
            title_font_color='white'
        )
        fig.update_xaxes(tickfont_color='white', titlefont_color='white', title=title_text)
        fig.update_yaxes(tickfont_color='white', titlefont_color='white', title='등장 횟수')
    st.plotly_chart(fig, use_container_width=True)

# --- UI Layout for the new section ---
if not df_translated.empty:
    st.subheader("번역된 한국도서 특성 분석")
    selected_category = st.radio(
        "분석 카테고리 선택",
        options=analysis_map.keys(),
        horizontal=True
    )
    config = analysis_map[selected_category]
    column_to_analyze = config["col"]
    emoji_map = config["emoji"]
    data_series = df_translated.get(column_to_analyze)

    tab_donut, tab_treemap, tab_bubble = st.tabs(["도넛 차트", "트리맵", "버블 차트"])
    with tab_donut:
        create_donut_chart(data_series, selected_category, st.session_state.theme, category=selected_category)
    with tab_treemap:
        create_treemap_chart(data_series, selected_category, emoji_map, st.session_state.theme, category=selected_category)
    with tab_bubble:
        create_bubble_chart(data_series, selected_category, st.session_state.theme, category=selected_category)
else:
    st.warning("번역 도서 데이터(`trans_final_with_url.csv`)를 찾을 수 없어 분석을 표시할 수 없습니다.")