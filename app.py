import streamlit as st
from slide_timer import lecture_timer_tab
from srt_parser import srt_parser_tab
from settings import settings_tab

st.set_page_config(
page_title="Slide Scribe",
page_icon="📝",
layout="wide",
initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] {
        font-size: 60px;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 8px;
    }
    .slide-number {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    pre, pre code {
        min-height: 200px !important;  /* 최소 높이 설정 */
        max-height: 400px !important;  /* 최대 높이 설정, 스크롤 가능 */
        overflow-y: auto !important;    /* 세로 스크롤 활성화 */
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 16px !important;
        line-height: 2.0 !important;
        padding: 15px !important;
        border-radius: 5px !important;
        margin-bottom: 20px !important;
        white-space: pre-wrap !important;  /* 줄바꿈 활성화 */
        word-wrap: break-word !important;  /* 단어 단위 줄바꿈 */
        overflow-wrap: break-word !important;  /* 긴 단어 줄바꿈 */
    }
</style>
""", unsafe_allow_html=True)


def main():
    try:
        
        # 세션 상태 초기화
        if 'result_df' not in st.session_state:
            st.session_state.result_df = None
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "SRT Parser"
        st.title('Slide Scribe')
        st.markdown('Made by 차유진.')
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["⏱️ Slide Timer", "📜 SRT Parser", "⚙️ Settings"])
        
        with tab1:
            lecture_timer_tab()
        
        with tab2:
            srt_parser_tab()
            
        with tab3:
            settings_tab()
    except Exception as e:
        st.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()