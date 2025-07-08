import streamlit as st
import pandas as pd
import plotly.express as px
from st_keyup import st_keyup
from utils.data_loader import load_data
from utils.style import apply_custom_style
from collections import Counter
from streamlit_extras.stylable_container import stylable_container
import plotly.io as pio

# --- 1. PAGE CONFIGURATION & THEME SETUP ---
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

st.set_page_config(
    page_title="K-소설 해외진출 나침반",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. APPLY CUSTOM STYLES ---
apply_custom_style(st.session_state.theme)

# Set global plotly template based on theme
if st.session_state.theme == "Light":
    pio.templates.default = "plotly_white"
else:
    pio.templates.default = "plotly_dark"

# --- 3. DATA LOADING ---
df_ranked = load_data('흥행예측도서_ranked.csv')
df_translated = load_data('trans_final_with_url.csv')
df_book_korean = load_data('book_korean.csv')
df_nyb = load_data('nyt_bestseller_with_keyword.csv')
df_imdb = load_data("imdb_llm_filtered_final.csv")

# --- 4. SESSION STATE INITIALIZATION ---
if 'selected_book_isbn' not in st.session_state:
    st.session_state.selected_book_isbn = None




# --- 5. SIDEBAR / NAVIGATOR ---
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

# --- 6. MAIN PAGE TITLE ---
st.title("📚 K-소설 해외진출 대시보드")
st.divider()

# --- 7. ROW 1: DYNAMIC METRIC CARDS ---
st.subheader("흥행 예측 핵심 지표")

# --- NEW: Add a button to toggle all expanders ---
if 'expand_all_metrics' not in st.session_state:
    st.session_state.expand_all_metrics = False

if st.button("지표 설명 모두 보기/접기", key="trans_expand"):
    st.session_state.expand_all_metrics = not st.session_state.expand_all_metrics

# --- REVISED: Create a structured list of metrics ---
if not df_ranked.empty and not df_translated.empty and not df_book_korean.empty:
    translated_count = df_translated['ISBN_K'].nunique()
    untranslated_count = df_book_korean['ISBN'].nunique()
    total_books = translated_count + untranslated_count
    translation_percentage = (translated_count / total_books) * 100 if total_books > 0 else 0
    success_count = df_ranked['ISBN'].nunique()
    success_percentage = (success_count/(success_count + untranslated_count)) * 100
    avg_final_score = df_ranked['fuzzy_topsis_score'].mean()
    avg_salespoint = df_translated['salespoint'].mean()
    success_salespoint = df_ranked['salespoint'].mean()
    avg_similarity = df_translated['top_1_similarity'].mean()
    success_nyb_max_s = df_ranked['nyb_max_s'].mean()
else:
    translation_percentage, avg_final_score, avg_salespoint, avg_similarity = 0, 0, 0, 0

metrics = [
    {
        "label": "흥행 예측도서 비율",
        "value": f"{success_percentage:.2f}%",
        "expander": """
        - **설명:** 번역되지 않은 전체 한국소설 중, 해외 흥행이 예측된 도서의 비율입니다.
        - **의미:** 이 비율이 높을수록 해외 흥행이 예측된 K-소설의 비중이 크다는 것을 의미합니다.
        """
    },
    {
        "label": "흥행 예측지수 평균",
        "value": f"{avg_final_score:.2f} / 1",
        "expander": """
        - **설명:** 다양한 지표(판매량, 평점, 유사도 등)를 종합하여 산출한 흥행 예측 점수입니다.
        - **의미:** 점수가 1에 가까울수록 해외 시장에서의 흥행 가능성이 높음을 시사합니다.
        """
    },
    {
        "label": "흥행 예측도서 판매지수 평균",
        "value": f"{success_salespoint:,.0f} pts",
        "expander": """
        - **설명:** 흥행 성공이 예측된 도서들의 평균 판매지수로, 알라딘에서 각 도서의 인기도와 판매 추이를 수치로 나타내는 고유한 판매 지수입니다.
        - **의미:** 판매지수가 높을수록 시장 반응이 좋음을 의미합니다.
        """
    },
    {
        "label": "흥행 예측도서 vs NYT 베스트셀러 유사도",
        "value": f"{success_nyb_max_s:.2f} / 1",
        "expander": """
        - **설명:** 흥행 예측도서와 뉴욕타임즈 베스트셀러 간의 내용적 유사도를 나타냅니다. **유사도**란 도서의 설명에 포함된 장르, 배경, 캐릭터, 분위기, 전개 등 도서 내용 및 의미가 유사한 정도를 수치화한 지수입니다.
        - **의미:** 수치가 높을수록 미국 주류 시장의 독자 취향과 부합할 가능성이 큽니다.
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


# --- 8. ROW 2: INTERACTIVE RANKING LIST AND DETAILS PANEL ---
st.subheader("흥행예측도서 순위")

# --- STEP 1: Define all mappings first for easy management ---
genre_emoji_map = {
    'Thriller': '🔪', 'Mystery': '🔍', 'Crime Fiction': '⚖️', 'Suspense': '⏳', 'Romance': '❤️',
    'Fantasy': '✨', 'Magical Realism': '🧙‍♂️', 'Mythic Fiction': '🧚‍♀️', 'Adventure': '🗺️',
    'Historical Fiction': '🏛️', 'Historical & Political Fiction': '🏛️', 'Science Fiction': '🚀',
    'Philosophical Fiction': '🤔', 'Contemporary Fiction': '🏙️', 'Literary Fiction': '📖',
    'Family_Saga': '👨‍👩‍👧‍👦', 'Coming-of-Age': '🌱'
}

genre_kor_map = {
    'Thriller': '스릴러', 'Mystery': '미스터리', 'Crime Fiction': '범죄소설', 'Suspense': '서스펜스', 'Romance': '로맨스',
    'Fantasy': '판타지', 'Magical Realism': '마술적 사실주의', 'Mythic Fiction': '신화소설', 'Adventure': '모험',
    'Historical Fiction': '역사소설', 'Historical & Political Fiction': '역사/정치소설', 'Science Fiction': 'SF',
    'Philosophical Fiction': '철학소설', 'Contemporary Fiction': '현대소설', 'Literary Fiction': '문학소설',
    'Family_Saga': '가족서사', 'Coming-of-Age': '성장소설'
}

# Labels for dataframe columns and sorting options
display_labels = {
    'fuzzy_rank': '순위',
    '제목': '제목',
    '저자': '저자',
    'primary_genre': '장르',
    'salespoint': '판매지수',
    'nyb_max_s': '해외 인기도서 유사도',
    'nyt_genre_score' : '해외 인기도서 장르 유사도',
    'imdb_genre_score' :'K-컨텐츠 장르 유사도',
    'fuzzy_topsis_score': '종합 평가 점수',
    'ISBN': 'ISBN'
}

sort_cols = ['fuzzy_rank', 'salespoint', 'nyb_max_s', 'nyt_genre_score','imdb_genre_score', 'fuzzy_topsis_score']

col_rank, col_detail = st.columns([2, 1])

with col_rank:
    search_query = st_keyup("🔍 도서 검색 (제목, 저자, ISBN)", debounce=500, key="book_search")
    if search_query:
        search_filtered_df = df_ranked[
            df_ranked['제목'].str.contains(search_query, case=False, na=False) |
            df_ranked['저자'].str.contains(search_query, case=False, na=False) |
            df_ranked['ISBN'].astype(str).str.contains(search_query, case=False, na=False)
        ]
    else:
        search_filtered_df = df_ranked

    col_sort_1, col_sort_2 = st.columns([2, 1])
    with col_sort_1:
        # --- STEP 2: Modify the selectbox to show Korean labels ---
        # The user sees Korean, but `sort_by` variable will hold the English key for sorting
        sort_by = st.selectbox(
            "정렬 기준 (Sort by)",
            options=sort_cols,
            format_func=lambda x: display_labels.get(x, x),  # Show Korean label
            index=0
        )
    with col_sort_2:
        order = st.radio("정렬 순서", ["오름차순", "내림차순"], horizontal=True)
        is_ascending = "오름차순" in order

    # --- STEP 3: Modify pills to show Korean genre names ---
    if 'primary_genre' in df_ranked.columns:
        unique_genres = sorted(df_ranked['primary_genre'].dropna().unique().tolist())
        selected_genres = st.pills(
            "장르 필터 (Filter by Genre)",
            options=unique_genres,
            format_func=lambda x: f"{genre_emoji_map.get(x, '📚')} {genre_kor_map.get(x, x)}", # Use Korean map
            selection_mode="multi"
        )
        if selected_genres:
            final_filtered_df = search_filtered_df[search_filtered_df['primary_genre'].isin(selected_genres)]
        else:
            final_filtered_df = search_filtered_df
    else:
        final_filtered_df = search_filtered_df
        st.warning("`primary_genre` 컬럼을 찾을 수 없어 장르 필터를 비활성화합니다.")

    # --- STEP 4: Translate dataframe content and headers before display ---
    display_cols = ['fuzzy_rank', '제목', '저자', 'primary_genre', 'salespoint', 'nyb_max_s', 'nyt_genre_score', 'imdb_genre_score','fuzzy_topsis_score', 'ISBN']

    if not final_filtered_df.empty:
        # Sort the original filtered dataframe
        df_sorted_original = final_filtered_df.sort_values(by=sort_by, ascending=is_ascending).reset_index(drop=True)

        # Create a copy for display purposes
        df_to_display = df_sorted_original[display_cols].copy()

        # Translate genre content to Korean + Emoji
        df_to_display['primary_genre'] = df_to_display['primary_genre'].map(
            lambda x: f"{genre_emoji_map.get(x, '📚')} {genre_kor_map.get(x, x)}" if pd.notna(x) else x
        )
        
        # Translate column headers to Korean
        df_to_display.columns = [display_labels.get(col, col) for col in df_to_display.columns]

    
        # Display the translated dataframe
        selection = st.dataframe(
            df_to_display,
            height = 500, 
            on_select="rerun",
            selection_mode="single-row",
            hide_index=True,
            use_container_width=True,
            column_config={
                "NYT 유사도": st.column_config.NumberColumn(format="%.2f"),
                "IMDB 유사도": st.column_config.NumberColumn(format="%.2f"),
                "종합 평가 점수": st.column_config.NumberColumn(format="%.2f"),
            }
        )

        # Get selected ISBN from the original sorted dataframe to ensure correctness
        if selection.selection.rows:
            selected_row_index = selection.selection.rows[0]
            st.session_state.selected_book_isbn = df_sorted_original.iloc[selected_row_index]['ISBN']
    else:
        st.info("검색 또는 필터링 결과가 없습니다.")

with col_detail:
    if st.session_state.selected_book_isbn:
        book_data = df_ranked[df_ranked['ISBN'] == st.session_state.selected_book_isbn]
        if not book_data.empty:
            book = book_data.iloc[0]
            image_url = book.get('image_url', '')
            title = book.get('제목', 'N/A')
            author = book.get('저자', 'N/A')
            pub_year_val = book.get('발행년도')
            pub_year = str(int(pub_year_val)) if pd.notna(pub_year_val) else 'N/A'
            isbn = book.get('ISBN', 'N/A')
            genre_eng = book.get('primary_genre', 'N/A')
            genre_kor = genre_kor_map.get(genre_eng, genre_eng)
            score_val = book.get('fuzzy_topsis_score')
            score = f"{score_val:.2f}" if pd.notna(score_val) else 'N/A'
            description = book.get('description', '소개 정보가 없습니다.')

            # --- CHANGE: Improved details card styling ---
            st.markdown(f"""
            <div class="details-card-window">
                <div class="details-card-content">
                    <div class="details-card-img-wrap">
                        <img src="{image_url if pd.notna(image_url) else ''}" class="details-card-img" alt="Book Cover">
                    </div>
                    <div class="details-card-title">{title}</div>
                    <div class="details-card-meta"><b>저자:</b> {author}</div>
                    <div class="details-card-meta"><b>발행년도:</b> {pub_year}</div>
                    <div class="details-card-meta"><b>ISBN:</b> {isbn}</div>
                    <div class="details-card-meta"><b>장르:</b> {genre_kor}</div>
                    <div class="details-card-meta"><b>최종 흥행 예측 지수:</b> {score}</div>
                    <div class="details-card-desc">{description}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        # --- CHANGE: Styled placeholder card ---
        with stylable_container(
            key="placeholder_card",
            css_styles="""
            .content-card {
                height: 800px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            """
        ):
            st.markdown(
                '<div class="content-card placeholder-card">'
                '흥행예측도서 순위 리스트에서<br>상세정보를 조회하고자 하는 도서를 클릭해주세요.'
                '</div>', 
                unsafe_allow_html=True
            )

st.divider()

#장르별 색상 지정 -> 위에서 imdb랑 다르게 mapping 해서 영어로 색상 지정 


# 장르 분석 파트 생성
genre_kor_map = {
    'Thriller': '스릴러', 'Mystery': '미스터리', 'Crime Fiction': '범죄소설', 'Suspense': '서스펜스', 'Romance': '로맨스',
    'Fantasy': '판타지', 'Magical Realism': '마술적 사실주의', 'Mythic Fiction': '신화소설', 'Adventure': '모험',
    'Historical Fiction': '역사소설', 'Historical & Political Fiction': '역사/정치소설', 'Science Fiction': 'SF',
    'Philosophical Fiction': '철학소설', 'Contemporary Fiction': '현대소설', 'Literary Fiction': '문학소설',
    'Family_Saga': '가족서사', 'Coming-of-Age': '성장소설' 
}

genre_kor_map_imdb = {
    'Thriller': '스릴러', 'Mystery': '미스터리', 'Crime Fiction': '범죄', 'Suspense': '서스펜스', 'Romance': '로맨스',
    'Fantasy': '판타지', 'Magical Realism': '마술적 사실주의', 'Mythic Fiction': '신화', 'Adventure': '모험',
    'Historical Fiction': '역사', 'Historical & Political Fiction': '역사/정치', 'Science Fiction': 'SF',
    'Philosophical Fiction': '철학', 'Contemporary Fiction': '현대', 'Literary Fiction': '문학',
    'Family_Saga': '가족서사', 'Coming-of-Age': '성장' 
}


genre_emoji_map = {
    'Thriller': '🔪', 'Mystery': '🔍', 'Crime Fiction': '⚖️', 'Suspense': '⏳', 'Romance': '❤️',
    'Fantasy': '✨', 'Magical Realism': '🧙‍♂️', 'Mythic Fiction': '🧚‍♀️', 'Adventure': '🗺️',
    'Historical Fiction': '🏛️', 'Historical & Political Fiction': '🏛️', 'Science Fiction': '🚀',
    'Philosophical Fiction': '🤔', 'Contemporary Fiction': '🏙️', 'Literary Fiction': '📖',
    'Family_Saga': '👨‍👩‍👧‍👦', 'Coming-of-Age': '🌱'
}
# --- 색상 지정  --- 참고용 
custom_palette = [
              "#A3C9A8", "#84B1BE", "#F2D388", "#C98474", "#8E7DBE",
              "#F5B7B1", "#AED6F1", "#F9E79F", "#D7BDE2", "#A2D9CE",
              "#FADBD8", "#F5CBA7", "#D2B4DE", "#A9CCE3", "#A3E4D7"
]

genre_color_map = {
    "🔪 스릴러": "#A3C9A8",
    "🔍 미스터리": "#84B1BE",
    "⚖️ 범죄소설": "#F2D388",
    "⏳ 서스펜스": "#C98474",
    "❤️ 로맨스": "#8E7DBE",
    "✨ 판타지": "#F5B7B1",
    "🧙‍♂️ 마술적 사실주의": "#AED6F1",
    "🧚‍♀️ 신화소설": "#F9E79F",
    "🗺️ 모험": "#D7BDE2",
    "🏛️ 역사소설": "#A2D9CE",
    "🏛️ 역사/정치소설": "#FADBD8",
    "🚀 SF": "#F5CBA7",
    "🤔 철학소설": "#D2B4DE",
    "🏙️ 현대소설": "#A9CCE3",
    "📖 문학소설": "#A3E4D7",
    "👨‍👩‍👧‍👦 가족서사": "#B7B7B7",
    "🌱 성장소설": "#FFD700"
}


genre_color_map_imdb = {
    "🔪 스릴러": "#A3C9A8",
    "🔍 미스터리": "#84B1BE",
    "⚖️ 범죄": "#F2D388",
    "⏳ 서스펜스": "#C98474",
    "❤️ 로맨스": "#8E7DBE",
    "✨ 판타지": "#F5B7B1",
    "🧙‍♂️ 마술적 사실주의": "#AED6F1",
    "🧚‍♀️ 신화": "#F9E79F",
    "🗺️ 모험": "#D7BDE2",
    "🏛️ 역사": "#A2D9CE",
    "🏛️ 역사/정치": "#FADBD8",
    "🚀 SF": "#F5CBA7",
    "🤔 철학": "#D2B4DE",
    "🏙️ 현대": "#A9CCE3",
    "📖 문학": "#A3E4D7",
    "👨‍👩‍👧‍👦 가족서사": "#B7B7B7",
    "🌱 성장": "#FFD700"
}

# --- 한글+이모지 매핑 함수 ---
def apply_kor_emoji_map(data_series, kor_map, emoji_map):
    return data_series.map(
        lambda x: f"{emoji_map.get(x, '')} {kor_map.get(x, x)}" if pd.notna(x) else x
    )

# --- 파이(도넛) 차트 함수 ---
def plot_genre_pie(data, title, kor_map, emoji_map, color_map):
    mapped = apply_kor_emoji_map(data, kor_map, emoji_map)
    counts = mapped.value_counts().reset_index()
    counts.columns = ['category', 'count']
    total = counts['count'].sum()
    fig = px.pie(
        counts,
        values='count',
        names='category',
        color='category',
        title=title,
        hole=0.4,
        color_discrete_map=color_map
    )
    fig.update_layout(
        width=650,
        height=650,
        paper_bgcolor='#f4f4f4',
        plot_bgcolor='#f4f4f4',
        font_color='black',
        title_font_color='black',
        legend_font_color='black',
        annotations=[dict(
            text=f'전체<br>{total}권',
            x=0.5, y=0.5,
            font_size=20,
            font_color='black',
            showarrow=False
        )],
        showlegend=True,
        legend=dict(title=title, yanchor="top", y=1, xanchor="left", x=1.05, font=dict(size=9))
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        insidetextorientation='horizontal',
        textfont_size=30
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 사용 예시 ---
col_gen, col_nyt, col_imdb = st.columns([1, 1, 1], gap="large")
with col_gen:
    st.subheader("흥행예측도서 장르 분포")
    plot_genre_pie(
        df_ranked['primary_genre'],
        title=" ",
        kor_map=genre_kor_map,
        emoji_map=genre_emoji_map,
        color_map=genre_color_map
    )
with col_nyt:
    st.subheader("미국 인기 도서 장르 분포")
    plot_genre_pie(
        df_nyb['primary_genre'],
        title=" ",
        kor_map=genre_kor_map,
        emoji_map=genre_emoji_map,
        color_map=genre_color_map
    )
with col_imdb:
    st.subheader("K-Contents 장르 분포")
    plot_genre_pie(
        df_imdb['primary_genre'],
        title=" ",
        kor_map=genre_kor_map_imdb,
        emoji_map=genre_emoji_map,
        color_map=genre_color_map_imdb
    )
