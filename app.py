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