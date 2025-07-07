# utils/data_loader.py
import pandas as pd
import streamlit as st
import gdown
import os
# Google Drive 파일 매핑 (파일명: 공유 링크)
GOOGLE_DRIVE_LINKS = {
    "book_korean.csv": "https://drive.google.com/file/d/10WYtmbT_ZjtffvWCpKzmF-hO1Kkj0Qx0/view?usp=sharing",
    "cluster_Similarity.csv": "https://drive.google.com/file/d/1P7-KhhJbwX_9emA-Mqfd_kt7lBxwNmPB/view?usp=drive_link",
    "imdb_llm_filtered_final.csv": "https://drive.google.com/file/d/1zg1qIDDd-glOxFWB_BrL8fpB9lHCXLGl/view?usp=drive_link",
    "nyt_bestseller_with_keyword.csv": "https://drive.google.com/file/d/1Y1yUAz_2wU7JibNtPYapYoI0ykqYdUwy/view?usp=drive_link",
    "reviews_final_with_clusters.csv": "https://drive.google.com/file/d/1RPfPwOubOi9RMh8X1Cl1m9uL0Q-F16_S/view?usp=drive_link",
    "trans_final_with_url.csv": "https://drive.google.com/file/d/1jcCTprvfQLgpbjv2946lueI-Pd1xafzp/view?usp=drive_link",
    "흥행예측도서_ranked.csv": "https://drive.google.com/file/d/101J67nfFOxgWMQb8M57BFQO6I1Pogjjf/view?usp=drive_link"
}
@st.cache_data
def load_data(file_name):
    """
    Google Drive에서 파일을 다운로드하여 DataFrame으로 반환.
    파일이 이미 있으면 재다운로드하지 않음.
    """
    # data 폴더가 없으면 생성
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", file_name)
    # 파일이 없으면 Google Drive에서 다운로드
    if not os.path.exists(file_path):
        url = GOOGLE_DRIVE_LINKS.get(file_name)
        if url is None:
            st.error(f"Google Drive 링크가 등록되지 않은 파일명입니다: {file_name}")
            return pd.DataFrame()
        with st.spinner(f"{file_name} 다운로드 중..."):
            gdown.download(url, file_path, quiet=False, fuzzy=True)
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"CSV 파일을 읽는 중 오류 발생: {e}")
        return pd.DataFrame()