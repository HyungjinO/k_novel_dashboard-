import streamlit as st
import pandas as pd
import plotly.express as px
from st_keyup import st_keyup
from utils.data_loader import load_data
from utils.style import apply_custom_style
from collections import Counter
from streamlit_extras.stylable_container import stylable_container
import plotly.io as pio

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

# --- 2. CSS 스타일 및 네비게이션 숨김 + 카드/도서 스타일 통합 ---
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
    color: #474747 !important;
    font-size: 18px;
}
.metric-card-value {
    color: #588157 !important;        
    font-size: 40px;
    font-weight: bold;
}
.book-item-compact, .bsr-book-card {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: #f9f9f9;
    border-radius: 14px;
    padding: 14px 16px;
    border: 1px solid #e0e0e0;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.book-image-small img, .bsr-book-image img {
    width: 90px;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.book-text-info, .bsr-book-info { flex: 1; }
.book-title, .bsr-book-title {
    font-size: 1.1rem;
    font-weight: bold;
    margin-bottom: 2px;
    color: #222;
}
.book-author, .book-bsr, .bsr-book-author, .bsr-book-rank {
    font-size: 0.95rem;
    color: #666;
}
.stTabs [data-baseweb="tab-list"] button {
    color: #111 !important;
    font-weight: bold;
    font-size: 1.05rem;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: #D3D3D3 !important;
    color: #fff !important;
}
div[role="radiogroup"] label {
    color: #D3D3D3 !important;
    font-weight: bold;
    font-size: 1.05rem;
}
.stButton > button {
    background-color: #f8f8f8 !important;
    color: #111 !important;
    border: 2px solid #588157 !important;
    border-radius: 8px !important;
}
.bsr-book-card {
    background: #f9f9f9;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 24px 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    gap: 20px;
    border: 1px solid #e0e0e0;
    min-height: 190px;      /* 카드 높이 증가 */
    max-width: 500px;       /* 필요시 카드 너비도 조정 */
}
.bsr-book-image img {
    width: 350px;           /* 이미지 크기 증가 */
    height: auto;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    max-width: 100%;
    max-height: 190px;      /* 카드 높이에 맞게 제한 */
    display: block;
}
</style>
""", unsafe_allow_html=True)

# --- 3. 사이드바 ---
with st.sidebar:
    st.title("K-소설 해외진출 나침반 🧭")
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
if not df_ranked.empty and not df_book_korean.empty:
    avg_salespoint_trans = df_translated['salespoint'].mean()
    hit_isbns = df_ranked['ISBN'].unique()
    df_not_hit = df_book_korean[~df_book_korean['ISBN'].isin(hit_isbns)]
    avg_salespoint_miss = df_not_hit['salespoint'].mean()
    avg_salespoint_all = df_book_korean['salespoint'].mean()
    per_success = 20.92391304348
else:
    avg_salespoint_success, avg_salespoint_miss, avg_salespoint_all = 0, 0, 0, 0

metrics = [
     {
        "label": "한국도서 해외 흥행율",
        "value": f"{per_success:,.2f}%",
        "desc": "판매량과 판매기간을 반영해 산출한 상품의 판매지수입니다.",
        "expander": """
        - **해석:** 해외에서 판매량이 높은 한국도서를 Amazon BSR(베스트셀러 순위) 기준으로 평가한 지수입니다.
        - **참고:** 번역된 한국 도서중 BSR 순위가 상위 10% 이내에 든 도서를 '해외 흥행'으로 간주합니다.
        """
    },
    {   
        "label": "한국도서 평균 판매지수",
        "value": f"{avg_salespoint_all:.2f}pts",
        "desc": "판매량과 판매기간을 반영해 산출한 상품의 판매지수입니다.",
        "expander": """
        - **해석:** 알라딘에서 각 도서의 인기도와 판매 추이를 수치로 나타내는 고유한 판매 지수입니다. 
        - **참고:** 판매지수가 높을수록 시장 반응이 좋음을 의미합니다.
        """
    },
    {
        "label": "번역 도서 평균 판매지수",
        "value": f"{avg_salespoint_trans:.2f}pts",
        "desc": "판매량과 판매기간을 반영해 산출한 상품의 판매지수입니다.",
        "expander": """
        - **해석:** 알라딘에서 각 도서의 인기도와 판매 추이를 수치로 나타내는 고유한 판매 지수입니다. 
        - **참고:** 판매지수가 높을수록 시장 반응이 좋음을 의미합니다.
        """
    },
    {
        "label": "해외 인기도서 유사도",
        "value": f"{0.64} / 1",
        "desc": "국내 흥행도서와 해외 인기도서 간의 평균 유사도 점수입니다.",
        "expander": """
        - **해석:** 도서의 설명에 포함된 장르, 배경, 캐릭터, 분위기, 전개 등 도서 내용 및 의미가 유사한 정도를 수치화한 지수입니다.
        - **참고:** 1에 가까울수록 두 책이 매우 비슷함을, 0에 가까울수록 상이한 특성을 지님을 의미합니다.
        """
    }
]

custom_palette = [
              "#A3C9A8", "#84B1BE", "#F2D388", "#C98474", "#8E7DBE",
              "#F5B7B1", "#AED6F1", "#F9E79F", "#D7BDE2", "#A2D9CE",
              "#FADBD8", "#F5CBA7", "#D2B4DE", "#A9CCE3", "#A3E4D7"
            ]

cols = st.columns(4)
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
        with st.expander("설명 보기"):
            st.markdown(metric["expander"])

# --- 7. 인기 도서 & 분석  ---
col_bsr, col_trend = st.columns([1, 1], gap="large")

with col_bsr:
    with stylable_container(key="bestseller_card", css_styles="""
        .content-card { min-height: 600px; background: #f9f9f9; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 24px; }
    """):
        st.subheader("한국도서 인기순위")
        if "salespoint" in df_book_korean.columns:
            salespoint_df = df_book_korean.sort_values(by="salespoint", ascending=False).head(6)
        else:
            st.warning("'salespoint' 컬럼이 데이터에 없습니다.")
            salespoint_df = df_book_korean.head(6)

        def display_book_item(row):
            return f"""
                <div class="book-item-compact">
                    <div class="book-image-small">
                        <img src="{row.get("image_url", "")}" alt="Book Cover">
                    </div>
                    <div class="book-text-info">
                        <div class="book-title">{row.get('제목', 'N/A')}</div>
                        <div class="book-author">작가: {row.get('저자', 'N/A')}</div>
                        <div class="book-author">출판사: {row.get('출판사', 'N/A')}</div>
                        <div class="book-bsr">판매지수: {row.get('salespoint', 0):,.0f}</div>
                    </div>
                </div>
            """
        for i in range(3):
            if i < len(salespoint_df):
                cols_inner = st.columns(2)
                with cols_inner[0]:
                    st.markdown(display_book_item(salespoint_df.iloc[i]), unsafe_allow_html=True)
                if i + 3 < len(salespoint_df):
                    with cols_inner[1]:
                        st.markdown(display_book_item(salespoint_df.iloc[i+3]), unsafe_allow_html=True)

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

# --- Row 3: 해외 독자 베스트 & 출판연도별 추이 ---
col_bsr2, col_trend2 = st.columns([1, 1], gap="large")
with col_bsr2:
    with stylable_container(key="bestseller_card_2", css_styles="""
        .content-card { min-height:1000px; background: #f9f9f9; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 24px; }
    """):
        st.subheader("해외 독자가 선택한 한국 도서 베스트")
        bsr_df = df_translated.sort_values(by='avg_bsr', ascending=True).head(6)
        book_cols = st.columns(2)
        for i, row in bsr_df.reset_index().iterrows():
            with book_cols[i % 2]:
                st.markdown(f"""
                    <div class="book-item-compact">
                        <div class="book-image-small">
                            <img src="{row.get("book_image", "")}" alt="Book Cover">
                        </div>
                        <div class="bsr-book-info">
                            <div class="bsr-book-title" title="{row.get('Title', 'N/A')}">{row.get('Title', 'N/A')}</div>
                            <div class="bsr-book-author">작가: {row.get('Author', 'N/A')}</div>
                            <div class="book-author">출판사: {row.get('Publisher', 'N/A')}</div>
                            <div class="bsr-book-rank">평균 BSR: {row.get('avg_bsr', 0):,.0f}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with col_trend2:
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
    if kor_map and emoji_map:
        return data_series.map(
            lambda x: f"{emoji_map.get(x, '')} {kor_map.get(x, x)}" if pd.notna(x) else x
        )
    return data_series

# --- 도넛 차트 함수 ---
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
    if kor_map and emoji_map:
        return data_series.map(
            lambda x: f"{emoji_map.get(x, '')} {kor_map.get(x, x)}" if pd.notna(x) else x
        )
    return data_series

# --- 도넛 차트 함수 (테마 분기 없이 간결하게) ---
def create_donut_chart(data_series, title_text, category=None):
    if category:
        data_series = apply_kor_emoji_map(data_series, category)
    if data_series.dropna().empty:
        st.info("분석할 데이터가 없습니다.")
        return
    counts = data_series.value_counts().reset_index()
    counts.columns = ['category', 'count']
    total = counts['count'].sum()
    fig = px.pie(
        counts, values='count', names='category',
        title=f"{title_text} 분포", hole=0.4, color_discrete_sequence=custom_palette
    )
    fig.update_layout(
        template=None,
        width=700,
        height=700,
        paper_bgcolor='#f8f8f8',
        plot_bgcolor='#f8f8f8',
        font_color='black',
        title_font_color='black',
        legend_font_color='black',
        annotations=[dict(
            text=f'전체<br>{total}권',
            x=0.5, y=0.5,
            font_size=30,
            font_color='black',
            showarrow=False
        )],
        showlegend=True,
        legend=dict(title=title_text, yanchor="top", y=1, xanchor="left", x=1.05)
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='horizontal',
        textfont_size=30
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 트리맵 차트 함수 (테마 분기 없이 간결하게) ---
def create_treemap_chart(data_series, title_text, emoji_map, category=None, color_discrete_sequence=custom_palette):
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
        color='label', color_discrete_sequence=color_scale, hover_data={'value': ':,.0f'}
    )
    fig.update_layout(
        template=None,
        paper_bgcolor='#f8f8f8',
        plot_bgcolor='#f8f8f8',
        font_color='black',
        title_font_color='black',
        title=f"{title_text} 분포",
        margin=dict(t=40, l=10, r=10, b=10),
        showlegend=False
    )
    fig.update_traces(
        textposition='middle center',
        textinfo='label+value',
        insidetextfont=dict(size=18, color='black'),
        marker=dict(cornerradius=5, line=dict(width=2, color='white'))
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 버블 차트 함수 (테마 분기 없이 간결하게) ---
def create_bubble_chart(data_series, title_text, emoji_map=None, category=None, color_discrete_sequence=custom_palette):
    if category:
        data_series = apply_kor_emoji_map(data_series, category)
    if data_series.dropna().empty:
        st.info("분석할 데이터가 없습니다.")
        return
    counts = data_series.value_counts().reset_index()
    counts.columns = ['category', 'count']
    fig = px.scatter(
        counts, x='category', y='count', size='count', color='category',
        title=f"{title_text} 분포", size_max=60,
        labels={'category': title_text, 'count': '등장 횟수'}
    )
    fig.update_layout(
        template=None,
        paper_bgcolor='#f8f8f8',
        plot_bgcolor='#f8f8f8',
        font_color='black',
        title_font_color='black'
    )
    fig.update_xaxes(tickfont_color='black', titlefont_color='black', title=title_text)
    fig.update_yaxes(tickfont_color='black', titlefont_color='black', title='등장 횟수')
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

    # 한글+이모지 매핑 적용
    data_series_label = apply_kor_emoji_map(data_series, selected_category)

    tab_donut, tab_treemap, tab_bubble = st.tabs(["도넛 차트", "트리맵", "버블 차트"])
    with tab_donut:
        create_donut_chart(data_series_label, selected_category, st.session_state.theme)
    with tab_treemap:
        create_treemap_chart(data_series_label, selected_category, emoji_map, st.session_state.theme)
    with tab_bubble:
        create_bubble_chart(data_series_label, selected_category, st.session_state.theme)
else:
    st.warning("번역 도서 데이터(`trans_final_with_url.csv`)를 찾을 수 없어 분석을 표시할 수 없습니다.")