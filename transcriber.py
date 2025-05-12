import streamlit as st

def transcriber_tab():
    st.markdown("AI 기반 음성 자막 생성 도구를 Google Colab에서 실행하세요!")

    st.subheader("Google Colab 실행")
    colab_url = "https://colab.research.google.com/drive/14FvsarkxDMjGCudHym-ttJy0qzwKu41o?usp=sharing"
    st.markdown(f"[Google Colab에서 실행하기]({colab_url})")
    
    default_code = """!git clone https://github.com/yujinc726/Whisper-AI-with-Gradio.git
%cd Whisper-AI-with-Gradio
!pip install -r requirements.txt
%run main.py"""
    st.code(default_code, language="python")
    st.caption("위 코드를 복사하여 Google Colab에서 실행하세요.")

    st.subheader("코드 실행 방법")
    steps = [
        "위 링크에 접속하거나 코드를 복사하여 Google Colab에 붙여넣습니다.",
        "우측 상단에서 런타임 유형이 'T4' 또는 기타 GPU로 설정되어 있는지 확인합니다.",
        "코드를 실행하고 약 2분 후 출력된 링크로 접속합니다.",
        "오디오 파일을 업로드하고 'Generate Subtitles' 버튼을 클릭합니다."
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f"{i}. {step}")
    st.markdown("---")

    """Whisper AI 설정 방법을 안내합니다."""
    st.subheader("Whisper AI 설정 가이드")
    settings = {
        "Model Size": "모델 크기가 클수록 정확도가 높지만 처리 속도가 느립니다. Turbo 모델은 정확도와 속도의 균형을 유지합니다.",
        "Language": "자막 생성 시 사용할 언어를 선택하세요.",
        "Stable-ts": "자막 파일의 타임스탬프를 안정화하는 모드입니다. (권장)",
        "Arrange Options": "자막 파일의 후처리 방식을 선택합니다.",
        "Prompt": "AI가 자막 생성 시 참고할 프롬프트를 입력하세요."
    }
    for key, value in settings.items():
        st.markdown(f"- **{key}**: {value}")
    st.markdown("---")