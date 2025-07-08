# pages/2_us_market.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from collections import Counter
import os
from streamlit_extras.stylable_container import stylable_container

# --- Import utility functions ---
import sys
sys.path.append('..')
from utils.data_loader import load_data
from utils.style import apply_custom_style

# --- Page Config ---
st.set_page_config(page_title="미국 도서시장 분석", page_icon="🇺🇸", layout="wide", initial_sidebar_state="expanded")
if "theme" not in st.session_state: st.session_state.theme = "Light"
apply_custom_style(st.session_state.theme)

# --- Hide Default Nav ---
hide_pages_nav = """
<style>
    div[data-testid="stSidebarNav"] {
        display: none;
    }
</style>
"""
st.markdown(hide_pages_nav, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("K-소설 해외진출 나침반 🧭")
    # Add new homepage link at the top
    st.page_link("Home.py", label="대시보드 홈")
    st.page_link("pages/1_translation.py", label="흥행 예측도서 분석")
    st.page_link("pages/2_us_market.py", label="미국 도서시장 분석")
    st.page_link("pages/3_domestic_market.py", label="한국 도서시장 현황")
    st.divider()

custom_palette = [
              "#A3C9A8", "#84B1BE", "#F2D388", "#C98474", "#8E7DBE",
              "#F5B7B1", "#AED6F1", "#F9E79F", "#D7BDE2", "#A2D9CE",
              "#FADBD8", "#F5CBA7", "#D2B4DE", "#A9CCE3", "#A3E4D7"
            ]

# --- Data Loading ---
@st.cache_data
def load_all_data():
    df_nyt = load_data('nyt_bestseller_with_keyword.csv')
    df_trans = load_data('trans_final_with_url.csv')
    df_reviews = load_data('reviews_final_with_clusters.csv')
    
    if not df_nyt.empty:
        def extract_rating(s):
            try: return float(s.split(' ')[0]) if isinstance(s, str) else None
            except: return None
        df_nyt['amazon_rating_numeric'] = df_nyt['amazon_rating'].apply(extract_rating)
        def extract_review(s):
            try: return int(s.replace(',', '').split(' ')[0]) if isinstance(s, str) else None
            except: return None
        df_nyt['review_count_numeric'] = df_nyt['amazon_review_count'].apply(extract_review)
        df_nyt['rank_numeric'] = pd.to_numeric(df_nyt['rank'], errors='coerce')
        df_nyt['weeks_on_list_numeric'] = pd.to_numeric(df_nyt['weeks_on_list'], errors='coerce')

        def extract_primary(j):
            try: return max(json.loads(j.replace("'", '"')), key=lambda k: float(json.loads(j.replace("'", '"'))[k])) if isinstance(j, str) else None
            except: return None
        json_cols = {'primary_plot': 'plot_elements', 'primary_character': 'character_types', 'primary_theme': 'theme_categories', 'primary_setting': 'setting_categories', 'primary_tone': 'tone_categories'}
        for new, old in json_cols.items():
            if old in df_nyt: df_nyt[new] = df_nyt[old].apply(extract_primary)
            else: df_nyt[new] = None

    if not df_reviews.empty:
        def safe_json_load(s):
            try: return json.loads(s.replace("'", '"')) if isinstance(s, str) else {}
            except: return {}
        df_reviews['parsed_keywords'] = df_reviews['parsed_keywords'].apply(safe_json_load)

    return df_nyt, df_trans, df_reviews

df_nyt, df_trans, df_reviews = load_all_data()
df_book_korean = load_data('book_korean.csv')

# --- PAGE START ---
st.title("🇺🇸 미국 도서시장 분석")
st.divider()

# --- SECTION 1: Metrics ---
st.subheader("흥행 비교 분석")

# --- NEW: Add a button to toggle all expanders ---
if 'expand_all_metrics' not in st.session_state:
    st.session_state.expand_all_metrics = False

if st.button("지표 설명 모두 보기/접기", key="us_expand"):
    st.session_state.expand_all_metrics = not st.session_state.expand_all_metrics

# --- REVISED: Create a structured list of metrics ---
if not df_trans.empty and not df_nyt.empty:
    avg_sim_success = df_trans[df_trans['success'] == 1]['nyb_max_s'].mean()
    avg_sim_fail = df_trans[df_trans['success'] == 0]['nyb_max_s'].mean()
    avg_rating_success = df_trans[df_trans['success'] == 1]['amazon_rating_clean'].mean()
    avg_rating_fail = df_trans[df_trans['success'] == 0]['amazon_rating_clean'].mean()
    translated_count = df_trans['ISBN_K'].nunique()
    review_count_success = df_trans[df_trans['success'] == 1]['amazon_review_count'].mean()
    review_count_fail = df_trans[df_trans['success'] == 0]['amazon_review_count'].mean()
    untranslated_count = df_book_korean['ISBN'].nunique()
    total_books = translated_count + untranslated_count
    translation_percentage = (translated_count / total_books) * 100 if total_books > 0 else 0
else:
    avg_sim_success, avg_sim_fail, avg_rating_success, avg_rating_fail = 0, 0, 0, 0

metrics = [
    {
        "label": "번역된 도서 비율",
        "value": f"{translation_percentage:.2f}%",
        "expander": """
        - **설명:** 전체 한국소설 중, 해외에 번역 출간된 도서의 비율입니다.
        - **의미:** 이 비율이 높을수록 K-소설의 해외 진출이 활발함을 의미합니다.
        """
    },
    {
        "label": "NYT 베스트셀러 유사도 (흥행작)",
        "value": f"{avg_sim_success:.2f} / 1",
        "expander": """
        - **설명:** 미국 시장에서 흥행에 성공한 K-소설과 NYT 베스트셀러 간의 평균 유사도입니다. **유사도**란 도서의 설명에 포함된 장르, 배경, 캐릭터, 분위기, 전개 등 도서 내용 및 의미가 유사한 정도를 수치화한 지수입니다.
        - **의미:** 미국 시장에서 흥행한 K-소설의 특징을 파악하는 데 활용됩니다.
        """
    },
    {
        "label": "아마존 리뷰 수 평균 (흥행작)",
        "value": f"{review_count_success:.0f}개",
        "expander": """
        - **설명:** 미국 아마존에서 흥행한 K-소설의 평균 리뷰 수입니다. 
        - **의미:** 현지 독자들의 관심을 보여주는 척도입니다.
        """
    },
    {
        "label": "아마존 리뷰 수 (비흥행작)",
        "value": f"{review_count_fail:.0f}개",
        "expander": """
        - **설명:** 미국 아마존에서 흥행에 실패한 K-소설의 평균 리뷰 수입니다.
        - **의미:** 현지 독자들의 관심을 보여주는 척도입니다.
        """
    },
    {
        "label": "아마존 리뷰 평균 (흥행작)",
        "value": f"⭐{avg_rating_fail:.2f}점",
        "expander": """
        - **설명:** 흥행에 실패한 K-소설의 평균 독자 평점입니다. (5점 만점)
        - **의미:** 독자들의 낮은 평가 원인을 파악하는 데 참고할 수 있습니다.
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


# --- SECTION 4: Reader Persona Analysis ---
st.subheader("미국 도서시장 독자 분석")
persona_data = {
    0: {"name": "두 얼굴의 팬층", "emoji": "🎭", "size": "1,868개 (10%)", "traits": "높은 충성도와 높은 실망 성향의 결합", "role": "고위험 팬 베이스", "color": "#E57373"},
    1: {"name": "캐주얼 독자층", "emoji": "😊", "size": "7,770개 (43%)", "traits": "안정적인 엔터테인먼트와 폭넓게 어필하는 스토리를 추구", "role": "가장 크고 기반이 되는 독자층", "color": "#81C784"},
    2: {"name": "문학적 분석가", "emoji": "🧐", "size": "2,388개 (13%)", "traits": "글쓰기 기법과 지적 깊이를 중시하며, 결함에 대해서는 비판적", "role": "권위 및 수상작 독자층", "color": "#64B5F6"},
    3: {"name": "감정적 열성팬", "emoji": "💖", "size": "4,158개 (23%)", "traits": "강렬한 감정적 연결과 장르에 대한 사랑으로 움직임", "role": "높은 참여도의 홍보자", "color": "#FFB74D"},
    4: {"name": "깐깐한 비평가", "emoji": "✍️", "size": "1,822개 (10%)", "traits": "플롯, 페이싱, 글쓰기의 구체적이고 기술적인 결함을 자주 지적", "role": "실행 가능한 피드백의 원천", "color": "#BA68C8"}
}

keyword_data = {
    0: ['author or series loyalist', 'emotional impact', 'stale', 'pleasure', 'tragic', 'powerful', 'chilling', 'sappy', 'ludicrous', 'harrowing'],
    1: ['entertainment', 'enthralled', 'inspirational', 'heartwarming', 'emotional processing', 'read through pretty quickly', 'upset', 'compassion', 'compelling characters'],
    2: ['intellectual stimulation', 'strong themes', 'good book', 'melodramatic', 'confident', 'quaint', 'scared', 'lost', 'anxious', 'intense'],
    3: ['genre fan', 'melancholy', 'impatient', 'inappropriate', 'fascination', 'introspective', 'amazement', 'disturbing', 'moved profundly'],
    4: ['critical reader', 'want to discuss', 'betrayal', 'unlikable', 'speed reading', 'unnecessary drama', 'unsatisfying ending', 'weak plot', 'poor writing']
}

persona_keyword_kor_map = {
    'author or series loyalist': '작가/시리즈 충성 독자', 'emotional impact': '감정적 울림', 'stale': '진부한',
    'pleasure': '즐거움', 'tragic': '비극적인', 'powerful': '강렬한', 'chilling': '오싹한', 'sappy': '오글거리는',
    'ludicrous': '터무니없는', 'harrowing': '참혹한', 'entertainment': '재미', 'enthralled': '매료된',
    'inspirational': '영감을 주는', 'heartwarming': '훈훈한', 'emotional processing': '정서적인',
    'read through pretty quickly': '술술 읽히는', 'upset': '속상한', 'compassion': '연민', 'intellectual stimulation': '지적 자극',
    'strong themes': '강렬한 메시지', 'good book': '수작(秀作)', 'melodramatic': '멜로드라마틱한', 'confident': '확신에 찬',
    'quaint': '기묘한', 'scared': '무서운', 'lost': '혼란스러운', 'anxious': '불안한', 'intense': '몰입도 높은',
    'genre fan': '장르 팬', 'melancholy': '우울한', 'impatient': '안달 나는', 'inappropriate': '부적절한',
    'fascination': '매혹적인', 'introspective': '생각에 잠기게 하는', 'amazement': '놀라움', 'disturbing': '불편한',
    'moved profundly': '큰 울림을 받은', 'critical reader': '비평적인 독자', 'want to discuss': '토론하고 싶어지는',
    'betrayal': '배신감', 'unlikable': '정이 안 가는', 'speed reading': '속독', 'unnecessary drama': '과한 설정',
    'unsatisfying ending': '용두사미', 'weak plot': '개연성 부족', 'poor writing': '필력이 아쉬운', 'compelling characters': '설득력 있는 캐릭터 설정'
}

emotion_kor_map = {
    "love": "사랑", "excitement": "흥미진진함", "delight": "기쁨", "appreciation": "감사함",
    "satisfaction": "만족감", "moved deeply": "뭉클함", "memorable": "인상적인", "conflicted": "복잡한 심경",
    "roller coaster ride": "감정 기복이 심한", "thought provoking": "곱씹게 되는", "irritation": "거슬림",
    "annoyed": "짜증", "dissatisfaction": "불만족", "frustration": "답답함", "disappointment": "실망감"
}

cluster_labels = [f"{v['emoji']} {v['name']}" for v in persona_data.values()]

# --- 미국 도서시장 독자 분석: 완전히 독립된 필터 ---
if 'selected_persona_label_analysis' not in st.session_state:
    st.session_state.selected_persona_label_analysis = cluster_labels[0]

selected_persona_label_analysis = st.pills(
    "독자 페르소나 필터 (분석용)",
    cluster_labels,
    default=st.session_state.selected_persona_label_analysis,
    key="main_persona_filter_analysis"
)
# 클릭 시 바로 반영: 선택값을 세션에 저장
if selected_persona_label_analysis != st.session_state.selected_persona_label_analysis:
    st.session_state.selected_persona_label_analysis = selected_persona_label_analysis

selected_cluster_id_analysis = next(
    (k for k, v in persona_data.items() if f"{v['emoji']} {v['name']}" == selected_persona_label_analysis), 0
)

col_persona_main, col_analysis_main = st.columns([6, 4], gap="large")

with col_persona_main:
    persona = persona_data[selected_cluster_id_analysis]

    with stylable_container("persona_details_card", css_styles=".content-card"):
        st.markdown(f"<div class='persona-name-card' style='background-color:{persona['color']};'>{persona['name']}</div>", unsafe_allow_html=True)

        img_col, details_col = st.columns([1, 1])
        with img_col:
            img_path = f"images/cluster_{selected_cluster_id_analysis}.png"
            if os.path.exists(img_path):
                st.image(img_path, width=225)

        with details_col:
            with stylable_container("persona_text_card", css_styles=".content-card"):
                st.markdown(f"<div class='persona-detail-label'>군집 규모:</div><div class='persona-detail-text'>{persona['size']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='persona-detail-label'>특성:</div><div class='persona-detail-text'>{persona['traits']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='persona-detail-label'>도서 시장에서의 역할:</div><div class='persona-detail-text'>{persona['role']}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    with stylable_container("keyword_card_bottom", css_styles=".content-card"):
        st.markdown(f"<div class='persona-detail-label'>페르소나 TOP 키워드</div>", unsafe_allow_html=True)
        keywords = keyword_data[selected_cluster_id_analysis]
        korean_keywords = [persona_keyword_kor_map.get(kw, kw) for kw in keywords]
        keyword_html = "".join([f"<span class='keyword-tag' style='background-color:{persona['color']};'>{kor_kw}</span>" for kor_kw in korean_keywords])
        st.markdown(f"<div style='text-align: center; padding-top: 1rem;'>{keyword_html}</div>", unsafe_allow_html=True)

with col_analysis_main:
    with stylable_container("radar_chart_card", css_styles=".content-card"):
        st.subheader("리뷰 감정분석")
        if not df_reviews.empty:
            cluster_df = df_reviews[df_reviews['cluster'] == selected_cluster_id_analysis]
            emotion_counter = Counter()
            for _, row in cluster_df.iterrows():
                parsed = row.get('parsed_keywords', {})
                if isinstance(parsed, dict):
                    for key in ['emotions_positive', 'emotions_negative', 'emotions_complex']:
                        if key in parsed and isinstance(parsed[key], dict):
                            emotion_counter.update(parsed[key].keys())

            fixed_emotion_labels = ["love", "excitement", "delight", "appreciation", "satisfaction", "moved deeply", "conflicted", "roller coaster ride", "thought provoking", "memorable", "irritation", "annoyed", "dissatisfaction", "frustration", "disappointment"]
            radar_data = {'Emotion': fixed_emotion_labels, 'Count': [emotion_counter.get(label, 0) for label in fixed_emotion_labels]}
            df_radar = pd.DataFrame(radar_data)

            if not df_radar.empty:
                df_radar['Emotion'] = df_radar['Emotion'].map(emotion_kor_map).fillna(df_radar['Emotion'])

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=df_radar['Count'], theta=df_radar['Emotion'], fill='toself', name='Emotions', line=dict(color=persona['color'])))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, gridcolor='lightgrey')), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="grey" if st.session_state.theme == "Light" else "white"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("이 클러스터에 대한 감정 데이터를 찾을 수 없습니다.")

# --- 페르소나별 추천 도서 페어링 (순수 HTML+CSS 버전) ---
genre_kor_map = {
    'Thriller': '스릴러', 'Mystery': '미스터리', 'Crime Fiction': '범죄소설', 'Suspense': '서스펜스', 'Romance': '로맨스',
    'Fantasy': '판타지', 'Magical Realism': '마술적 사실주의', 'Mythic Fiction': '신화소설', 'Adventure': '모험',
    'Historical Fiction': '역사소설', 'Historical & Political Fiction': '역사/정치소설', 'Science Fiction': 'SF',
    'Philosophical Fiction': '철학소설', 'Contemporary Fiction': '현대소설', 'Literary Fiction': '문학소설',
    'Family_Saga': '가족서사', 'Coming-of-Age': '성장소설'
}

st.divider()
st.subheader("페르소나별 추천 도서 페어링")
st.markdown("선택된 독자 페르소나가 가장 많이 읽은 미국 도서와 내용이 가장 유사한 한국 도서를 추천합니다.")

if 'selected_persona_label_pairing' not in st.session_state:
    st.session_state.selected_persona_label_pairing = cluster_labels[0]

selected_persona_label_pairing = st.pills(
    "독자 페르소나 필터 (페어링용)",
    cluster_labels,
    default=st.session_state.selected_persona_label_pairing,
    key="pairing_persona_filter_pairing"
)
if selected_persona_label_pairing != st.session_state.selected_persona_label_pairing:
    st.session_state.selected_persona_label_pairing = selected_persona_label_pairing

df_similarity = load_data('cluster_Similarity.csv')

if df_similarity is not None and not df_similarity.empty:
    current_cluster_id_pairing = next(
        (k for k, v in persona_data.items() if f"{v['emoji']} {v['name']}" == selected_persona_label_pairing), 0
    )
    persona_books = df_similarity[df_similarity['cluseter Index'] == current_cluster_id_pairing].head(5).reset_index(drop=True)
    persona_books['nyt_genre_kor'] = persona_books['nyt_genre'].map(genre_kor_map).fillna(persona_books['nyt_genre'])
    persona_books['pred_genre_kor'] = persona_books['pred_genre'].map(genre_kor_map).fillna(persona_books['pred_genre'])

    if not persona_books.empty:
        # --- CSS ---
        st.markdown("""
        <style>
        .book-pair-grid {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
            align-items: center;
            margin-bottom: 2.5rem;
        }
        .book-pair-row {
            display: flex;
            flex-direction: row;
            justify-content: center;
            gap: 2rem;
            width: 100%;
        }
        .book-pair-card {
            background: var(--secondary-background-color, #fff);
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.07);
            border: 1px solid #e0e0e0;
            width: 320px;
            min-width: 300px;
            max-width: 340px;
            height: 260px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 0;
            transition: box-shadow 0.2s;
            position: relative;
        }
        .book-pair-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        .pair-content {
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            justify-content: space-between;
            width: 94%;
            height: 90%;
            gap: 0.5rem;
        }
        .book-info {
            width: 40%;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
        .book-info img {
            width: 90px;
            height: 130px;
            object-fit: cover;
            border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            margin-bottom: 0.5rem;
        }
        .book-title {
            font-weight: bold;
            font-size: 15px;
            margin-bottom: 0.2rem;
            margin-top: 0.1rem;
            height: 38px;
            line-height: 19px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        .book-genre {
            font-size: 13px;
            color: #888;
            margin-bottom: 0.1rem;
            margin-top: 0.1rem;
        }
        .similarity-connector {
            flex: 1 1 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-width: 52px;
            max-width: 52px;
            position: relative;
        }
        .similarity-connector .dotted-line-top {
            border-left: 2px dotted #bdbdbd;
            height: 40px;
            position: absolute;
            left: 50%;
            top: 0;
            z-index: 0;
            transform: translateX(-50%);
        }
        .similarity-connector .dotted-line-bottom {
            border-left: 2px dotted #bdbdbd;
            height: 40px;
            position: absolute;
            left: 50%;
            bottom: 0;
            z-index: 0;
            transform: translateX(-50%);
        }
        .similarity-text {
            background: var(--secondary-background-color, #fff);
            position: relative;
            z-index: 1;
            text-align: center;
            padding: 1px 0;
            margin-bottom: 2px;
            margin-top: 2px;
        }
        .similarity-label {
            font-size: 13px;
            color: #888;
            margin-bottom: 1px;
        }
        .similarity-value {
            font-size: 17px;
            font-weight: bold;
            color: var(--primary-color, #588157);
        }
        @media (max-width: 1100px) {
            .book-pair-row { flex-direction: column; align-items: center; }
            .book-pair-card { width: 95vw; min-width: 0; max-width: 98vw; margin-bottom: 1.2rem;}
        }
        </style>
        """, unsafe_allow_html=True)

        # --- HTML ---
        html_rows = []
        # First row: up to 3 cards
        row1 = ""
        for i in range(min(3, len(persona_books))):
            row1 += f"""
            <div class="book-pair-card">
                <div class="pair-content">
                    <div class="book-info">
                        <img src="{persona_books.loc[i, 'nyt_image_url']}" alt="NYT Book Cover">
                        <div class="book-title" title="{persona_books.loc[i, 'nyt_title']}">{persona_books.loc[i, 'nyt_title']}</div>
                        <div class="book-genre">{persona_books.loc[i, 'nyt_genre_kor']}</div>
                    </div>
                    <div class="similarity-connector">
                        <div class="dotted-line-top"></div>
                        <div class="similarity-text">
                            <div class="similarity-label">유사도</div>
                            <div class="similarity-value">{persona_books.loc[i, 'Similarity']*100:.1f}%</div>
                        </div>
                        <div class="dotted-line-bottom"></div>
                    </div>
                    <div class="book-info">
                        <img src="{persona_books.loc[i, 'korean_image_url']}" alt="Korean Book Cover">
                        <div class="book-title" title="{persona_books.loc[i, 'pred_title']}">{persona_books.loc[i, 'pred_title']}</div>
                        <div class="book-genre">{persona_books.loc[i, 'pred_genre_kor']}</div>
                    </div>
                </div>
            </div>
            """
        html_rows.append(f'<div class="book-pair-row">{row1}</div>')

        # Second row: up to 2 cards, centered
        if len(persona_books) > 3:
            row2 = ""
            for i in range(3, len(persona_books)):
                row2 += f"""
                <div class="book-pair-card">
                    <div class="pair-content">
                        <div class="book-info">
                            <img src="{persona_books.loc[i, 'nyt_image_url']}" alt="NYT Book Cover">
                            <div class="book-title" title="{persona_books.loc[i, 'nyt_title']}">{persona_books.loc[i, 'nyt_title']}</div>
                            <div class="book-genre">{persona_books.loc[i, 'nyt_genre_kor']}</div>
                        </div>
                        <div class="similarity-connector">
                            <div class="dotted-line-top"></div>
                            <div class="similarity-text">
                                <div class="similarity-label">유사도</div>
                                <div class="similarity-value">{persona_books.loc[i, 'Similarity']*100:.1f}%</div>
                            </div>
                            <div class="dotted-line-bottom"></div>
                        </div>
                        <div class="book-info">
                            <img src="{persona_books.loc[i, 'korean_image_url']}" alt="Korean Book Cover">
                            <div class="book-title" title="{persona_books.loc[i, 'pred_title']}">{persona_books.loc[i, 'pred_title']}</div>
                            <div class="book-genre">{persona_books.loc[i, 'pred_genre_kor']}</div>
                        </div>
                    </div>
                </div>
                """
            html_rows.append(f'<div class="book-pair-row" style="justify-content:center;">{row2}</div>')

        st.html(f"""
        <div class="book-pair-grid">
            {''.join(html_rows)}
        </div>
        """)
    else:
        st.info(f"선택된 페르소나({selected_persona_label_pairing})에 대한 추천 도서 페어링 데이터가 없습니다.")
else:
    st.warning("도서 페어링 데이터(`cluster_Similarity.csv`)를 찾을 수 없습니다.")


# --- SECTION 2: Bestseller Feature Analysis ---
st.subheader("미국 인기도서 특징 분석")

# --- Step 1: Add all the necessary Korean and Emoji mapping dictionaries ---
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
    'redemption': '속죄', 'fish_out_of_water': '낯선 환경에서의 갈등', 'second_chance': '두 번째 기회', 'rags_to_riches': '신분 상승 이야기',
    'magic_system': '마법', 'prophecy': '예언', 'enemies_to_lovers': "적에서 연인으로"
}

character_kor_map = { 
        "survivor": "생존자", "ordinary_person": "평범한 인물", "outsider": "국외자", "artist": "예술가", "student": "학생", 
        "anti_hero": "반(反)영웅", "reluctant_hero": "마지못해 영웅이 된 인물", "magic_user": "마법사", "detective": "탐정", "royalty": "왕족", 
        "spy": "스파이", "love_interest": "사랑의 대상", "teacher": "교사", "soldier": "군인", "leader": "리더", "complex_antagonist": "입체적 악역",
        "hero": "영웅", "mentor_figure": "멘토", "doctor": "의사", "journalist": "기자", "criminal": "범죄자", "scientist": "과학자", "writer": "작가",
        "warrior": "용사", "lawyer": "변호사", "rebel": "반역자", "scholar": "학자", "the innocent": "무고한 인물"
}

setting_kor_map = {
     "contemporary": "현대", "foreign_country": "외국", "rural": "시골", "dystopian_society": "디스토피아 사회", "magical_realm": "마법 세계", 
     "big_city": "대도시", "historical_medieval": "중세 시대", "fantasy_world": "판타지 세계", "historical_victorian": "빅토리아 시대", "historical_1920s": "1920년대", 
     "historical": "역사적 배경", "near_future": "가까운 미래", "historical_wwii": "2차 세계대전", "far_future": "먼 미래", "small_town": "소도시", "historical_1970s": "1970년대", 
     "prison": "감옥", "school_setting": "학교", "workplace": "직장", "post_apocalyptic": "포스트 아포칼립스", "historical_1950s": "1950년대", "historical_1980s": "1980년대", 
     "upper_class": "상류층", "military": "군대", "other_planet": "다른 행성", "working_class": "노동자 계급", "historical_1930s": "1930년대", "island": "섬",
     "suburban": "교외 지역", "historical_1960s": "1960년대", "hospital": "병원"
}

tone_kor_map = {
     "intense": "강렬한", "serious": "진지한", "emotional": "감정적인", "haunting": "잊혀지지 않는", "dark": "어두운", "suspenseful": "긴장감 있는", "poetic": "시적인", 
     "dramatic": "극적인", "hopeful": "희망적인", "whimsical": "기발한", "action_packed": "액션이 풍부한", "humorous": "유머러스한", "melancholic": "우울한", "uplifting": "격려하는", 
     "fast_paced": "빠른 전개", "philosophical": "철학적인", "eerie": "으스스한", "mysterious": "신비로운", "gentle": "부드러운", "nostalgic": "향수를 불러일으키는", "pessimistic": "비관적인",
     "heartening": "가슴 벅찬", "gripping": "사로잡는", "sexy": "관능적인", "heartwarming": "마음 따뜻해지는", "tense": "긴장감 있는", "warmhearted": "감동적인"
}

theme_kor_map = { 
    "survival_instinct": "생존 본능", "social_justice": "사회 정의", "personal_growth": "개인적 성장", "truth_seeking": "진실 추구", "justice": "정의", "family_bonds": "가족 유대", 
    "power_corruption": "권력의 부패", "identity_search": "정체성 탐색", "freedom": "자유", "environmental_issues": "환경 문제", "good_vs_evil": "선과 악", "belonging": "소속감",
      "cultural_clash": "문화 충돌", "technology_impact": "기술의 영향", "love_story": "사랑 이야기", "moral_dilemma": "도덕적 딜레마", "sacrifice_for_others": "타인을 위한 희생", 
      "tradition_vs_change": "전통과 변화의 갈등", "forgiveness": "용서", "love": "사랑", "legacy": "유산", "responsibility": "책임",
      "revenge": "복수", "loyalty": "충성심"
}

plot_emoji_map = {
    'survival':'🏕️', 'identity_crisis':'🎭', 'transformation':'🦋', 'coming_of_age':'🌱', 'revenge':'😠', 'rebellion':'✊', 
    'family_secrets':'🗝️', 'forgiveness':'🤝', 'curse':'🧙‍♂️', 'mystery_solving':'🕵️', 'love_story':'❤️', 'war':'⚔️', 'discovery':'💡', 
    'sacrifice':'🕊️', 'hero_journey':'🦸', 'political_intrigue':'🕴️', 'betrayal':'💔', 'forbidden_love':'🚫❤️', 'quest':'🗺️', 'exploration':'🧭',
    'redemption':'🙏', 'fish_out_of_water':'😰', 'second_chance':'🔄', 'rags_to_riches':'📈', 'magic_system': '🔮', 'prophecy': '👁️', 'enemies_to_lovers':'⚔️❤️'
}

character_emoji_map = {
    'ordinary_person': '🧑', 'survivor': '💪', 'outsider': '🚶', 'reluctant_hero': '🦸', 'love_interest': '💕',
    'anti_hero': '😈', 'mentor_figure': '🧑‍🏫', 'artist': '🎨', 'student': '🎒', 'magic_user': '🧙',
    'detective': '🕵️', 'royalty': '👑', 'spy': '🕶️', 'teacher': '👩‍🏫', 'soldier': '🪖', 'leader': '🧑‍💼',
    'complex_antagonist': '🦹', 'hero': '🦸', 'doctor': '👩‍⚕️', 'journalist': '📰', 'criminal': '🚓',
    'scientist': '🔬', 'writer': '✍️', "warrior": "🛡️", "lawyer": "👩‍⚖️", "rebel": "✊", "scholar": "🎓", "the innocent": "😇"
}
theme_emoji_map = {
    'personal_growth':'🌱', 'social_justice':'⚖️', 'identity_search':'❓', 'family_bonds':'👨‍👩‍👧‍👦', 'moral_dilemma':'🤔', 
    'cultural_clash':'🌍', 'survival_instinct':'🧠', 'truth_seeking':'🔎', 'justice':'🧑‍⚖️', 'power_corruption':'🤫', 'freedom':'🕊️', 
    'environmental_issues':'🌳', 'good_vs_evil':'⚔️', 'belonging':'🫂', 'technology_impact':'🤖', 'love_story':'❤️', 'sacrifice_for_others':'🕊️', 
    'tradition_vs_change':'🔄', 'forgiveness':'🤝', 'love':'💖', 'legacy':'🏛️', 'responsibility':'👩‍⚖️', "revenge": "🗡️", "loyalty": "🙇‍♂️"
}

setting_emoji_map = {
    'contemporary': '🌇', 'foreign_country': '✈️', 'rural': '🌾', 'dystopian_society': '🏭', 'magical_realm': '🪄',
    'big_city': '🚕', 'historical_medieval': '🏰', 'fantasy_world': '🐉', 'historical_victorian': '🎩', 'historical_1920s': '🎷',
    'historical': '📜', 'near_future': '🤖', 'historical_wwii': '💣', 'far_future': '🚀', 'small_town': '🏘️',
    'historical_1970s': '🕺', 'prison': '🚔', 'school_setting': '🏫', 'workplace': '💼', 'post_apocalyptic': '☢️',
    'historical_1950s': '🎙️', 'historical_1980s': '📼', 'upper_class': '💎', 'military': '🎖️', 'other_planet': '🪐',
    'working_class': '🔧', 'historical_1930s': '🎞️', 'island': '🏝️', "suburban": "🏞️", "historical_1960s": "📺", "hospital": "🏥"
}

tone_emoji_map = {
    'intense':'🔥', 'serious':'🧐', 'emotional':'😭', 'haunting':'👻', 'dark':'🌑', 'suspenseful':'😱', 'poetic':'🖋️',
    'dramatic':'🎭', 'hopeful':'🌅', 'whimsical':'🦄', 'action_packed':'💥', 'humorous':'🤣', 'melancholic':'😔', 
    'uplifting':'🌈', 'fast_paced':'⚡', 'philosophical':'🤔', 'eerie':'🕸️', 'mysterious':'🕵️‍♂️', 'gentle':'🕊️', 'nostalgic':'📻', 'pessimistic':'🙄',
    "heartening": "💖", "gripping": "🤩", "sexy": "💋", "heartwarming": "🥰", "tense": "😬", "warmhearted": "🤗"
    }

genre_emoji_map = {
    'Thriller': '🔪', 'Mystery': '🔍', 'Crime Fiction': '⚖️', 'Suspense': '⏳', 'Romance': '❤️',
    'Fantasy': '✨', 'Magical Realism': '🧙‍♂️', 'Mythic Fiction': '🧚‍♀️', 'Adventure': '🗺️',
    'Historical Fiction': '🏛️', 'Historical & Political Fiction': '🏛️', 'Science Fiction': '🚀',
    'Philosophical Fiction': '🤔', 'Contemporary Fiction': '🏙️', 'Literary Fiction': '📖',
    'Family_Saga': '👨‍👩‍👧‍👦', 'Coming-of-Age': '🌱'
}

# --- Step 2: Update analysis_map to include Korean mappings ---
analysis_map = {
    "장르": {"col": "primary_genre", "emoji": genre_emoji_map, "kor": genre_kor_map},
    "전개": {"col": "primary_plot", "emoji": plot_emoji_map, "kor": plot_kor_map},
    "등장인물": {"col": "primary_character", "emoji": character_emoji_map, "kor": character_kor_map},
    "주제": {"col": "primary_theme", "emoji": theme_emoji_map, "kor": theme_kor_map},
    "배경": {"col": "primary_setting", "emoji": setting_emoji_map, "kor": setting_kor_map},
    "분위기": {"col": "primary_tone", "emoji": tone_emoji_map, "kor": tone_kor_map}
}

if not df_nyt.empty:
    selected_category = st.radio("분석 카테고리 선택", options=analysis_map.keys(), horizontal=True, key="nyt_feature_filter")
    config = analysis_map[selected_category]
    data_series = df_nyt.get(config["col"])

    # --- Step 3: Modify each chart function to accept and use the Korean map ---
    def create_donut_chart(data_series, title_text, theme, kor_map, emoji_map):
        if data_series.dropna().empty: return
        counts = data_series.value_counts().reset_index()
        counts.columns = ['category', 'count']
        # Translate labels to Korean
        counts['category'] = counts['category'].apply(lambda x: f"{emoji_map.get(x, '📝')} {kor_map.get(x, x)}")
        total = counts['count'].sum()
        fig = px.pie(counts, values='count', names='category', title=f"{title_text} 분포", hole=0.4, template="plotly_white" if theme == "Light" else "plotly_dark", color_discrete_sequence=custom_palette)
        fig.update_traces(textposition='inside', textinfo='percent', insidetextorientation='radial')
        fig.update_layout(annotations=[dict(text=f'전체<br>{total}권', x=0.5, y=0.5, font_size=20, showarrow=False)], showlegend=True, legend=dict(title=title_text, yanchor="top", y=1, xanchor="left", x=1.05))
        st.plotly_chart(fig, use_container_width=True)

    def create_treemap_chart(data_series, title_text, emoji_map, theme, kor_map):
        if data_series.dropna().empty: return
        counts = Counter(data_series.dropna().astype(str))
        df_treemap = pd.DataFrame(counts.items(), columns=['label', 'value'])
        # Translate labels to "Emoji + Korean Name"
        df_treemap['formatted_label'] = df_treemap['label'].apply(lambda x: f"{emoji_map.get(x, '📝')}<br>{kor_map.get(x, x)}")
        fig = px.treemap(df_treemap, path=[px.Constant("all"), 'formatted_label'], values='value', color='label', color_discrete_sequence=custom_palette, hover_data={'value': ':,.0f'})
        fig.update_traces(textposition='middle center', textinfo='label+value', insidetextfont=dict(size=18, color='#333333'), marker=dict(cornerradius=5, line=dict(width=2, color='white')))
        fig.update_layout(title=f"{title_text} 분포", margin=dict(t=40, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    def create_bubble_chart(data_series, title_text, theme, kor_map, emoji_map):
        if data_series.dropna().empty: return
        counts = data_series.value_counts().reset_index()
        counts.columns = ['category', 'count']
        # Translate labels to Korean
        counts['category'] = counts['category'].apply(lambda x: f"{emoji_map.get(x, '📝')} {kor_map.get(x, x)}")
        fig = px.scatter(counts, x='category', y='count', size='count', color_discrete_sequence=custom_palette, color='category', title=f"{title_text} 분포", size_max=60, template="plotly_white" if theme == "Light" else "plotly_dark", labels={'category': title_text, 'count': '등장 횟수'})
        st.plotly_chart(fig, use_container_width=True)

    tab_donut, tab_treemap, tab_bubble = st.tabs(["도넛 차트", "트리맵", "버블 차트"])
    with tab_donut:
        create_donut_chart(data_series, selected_category, st.session_state.theme, config["kor"], config["emoji"])
    with tab_treemap:
        create_treemap_chart(data_series, selected_category, config["emoji"], st.session_state.theme, config["kor"])
    with tab_bubble:
        create_bubble_chart(data_series, selected_category, st.session_state.theme, config["kor"], config["emoji"])
else:
    st.warning("NYT 베스트셀러 데이터(`nyt_bestseller_with_keyword.csv`)를 찾을 수 없습니다.")
st.divider()


# --- SECTION 3: Bestseller List & Marketing Analysis ---
st.subheader("미국 도서시장 도서 분석")
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("###### 미국 시장 인기도서")
    sort_options = {"최장기간 베스트셀러": ("weeks_on_list_numeric", False), "최고 순위": ("rank_numeric", True), "최고 평점": ("amazon_rating_numeric", False), "최다 리뷰": ("review_count_numeric", False)}
    selected_sort = st.selectbox("정렬 기준", options=list(sort_options.keys()))
    
    if not df_nyt.empty:
        sort_col, ascending = sort_options[selected_sort]
        top_books = df_nyt.sort_values(by=sort_col, ascending=ascending).head(6)

        def create_book_card(row):
            rating = row.get('amazon_rating_numeric')
            stars = "⭐" * int(rating) + "☆" * (5 - int(rating)) if pd.notna(rating) else "N/A"
            reviews = f"{int(row.get('review_count_numeric', 0)):,}" if pd.notna(row.get('review_count_numeric')) else "N/A"
            return f"""<div class="nyt-book-card">
                        <div class="nyt-book-image"><img src="{row.get('book_image', '')}" alt="Cover"></div>
                        <div class="nyt-book-info">
                            <div class="nyt-book-title" title="{row.get('title', '')}">{row.get('title', '')}</div>
                            <div class="nyt-book-author" title="{row.get('author', '')}">저자: {row.get('author', '')}</div>
                            <div class="star-rating">{stars}</div>
                            <div class="nyt-book-reviews">리뷰 수: {reviews}</div>
                        </div></div>"""
        
        book_col1, book_col2 = st.columns(2)
        for i, row in top_books.reset_index().iterrows():
            with book_col1 if i < 3 else book_col2: st.markdown(create_book_card(row), unsafe_allow_html=True)

with col_right:
    st.subheader("마케팅 문구 분포")
    tab1, tab2 = st.tabs(["전체 비교", "종류별 비교"])
    with tab1:
        st.markdown("###### 해외 인기도서 vs. 한국 번역도서 - 전체 마케팅 문구 비교")
        if not df_nyt.empty and not df_trans.empty:
            avg_exp_nyt = df_nyt['marketing_exp'].mean()
            avg_exp_trans = df_trans['marketing_exp'].mean()
            df_plot = pd.DataFrame({'도서 유형': ['미국 베스트셀러', '한국 번역도서'], '평균 마케팅 문구 수': [avg_exp_nyt, avg_exp_trans]})
            fig = px.bar(df_plot, x='도서 유형', y='평균 마케팅 문구 수', color='도서 유형', text_auto='.2f', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False, yaxis_title="평균 문구 수", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.markdown("###### 해외 인기도서 vs. 한국 번역도서 - 마케팅 문구 종류별 비교")
        if not df_nyt.empty and not df_trans.empty:
            marketing_cols = ['marketing_social_media', 'marketing_tv_film_streaming', 'marketing_award', 'marketing_media_magazine_press', 'marketing_book_club', 'marketing_sales']
            labels_map = {"marketing_social_media": "소셜 미디어", "marketing_tv_film_streaming": "TV·영화", "marketing_award": "수상 이력", "marketing_media_magazine_press": "미디어·잡지", "marketing_book_club": "북클럽", "marketing_sales": "판매량"}
            nyt_counts = df_nyt[marketing_cols].sum()
            trans_counts = df_trans[marketing_cols].sum()
            df_plot = pd.DataFrame({'미국 베스트셀러': nyt_counts, '한국 번역도서': trans_counts}).reset_index().rename(columns={'index': '유형'})
            df_plot['유형'] = df_plot['유형'].map(labels_map)
            df_melted = df_plot.melt(id_vars='유형', var_name='데이터셋', value_name='언급 횟수')
            fig = px.bar(df_melted, x='유형', y='언급 횟수', color='데이터셋', barmode='group', text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(yaxis_title="언급 횟수", xaxis_title="마케팅 유형", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
st.divider()
