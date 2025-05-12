import streamlit as st

def transcriber_tab():
    st.markdown(f'[Google Colaboratory](https://colab.research.google.com/drive/14FvsarkxDMjGCudHym-ttJy0qzwKu41o?usp=sharing)')
    st.text_area("Code", value="!git clone https://github.com/yujinc726/Whisper-AI-with-Gradio.git\n%cd Whisper-AI-with-Gradio\n!pip install -r requirements.txt\n%run main.py", height=120)
    st.markdown("---")
    st.markdown("### 코드 실행 방법")
    st.markdown("1. 링크에 접속하거나 코드를 복사하여 Google Colab에 붙여넣습니다.")
    st.markdown("2. 우측 상단에 런타임 유형이 'T4' 혹은 기타 GPU인지 확인합니다.")
    st.markdown("3. 코드를 실행하고 약 2분 후에 출력된 링크로 접속합니다.")
    st.markdown("4. 오디오 파일을 업로드하고 'Generate Subtitles' 버튼을 누릅니다.")
    st.markdown("---")
    st.markdown("### Whisper AI 설정 소개")
    st.markdown("1. Model Size: 아래로 갈수록 모델의 크기가 크고 정확도가 높아지지만 작업 속도가 오래 걸립니다. 단, turbo 모델은 정확도를 최대한 유지하면서 빠른 작업속도를 유지하는 모델입니다.")
    st.markdown("2. Language: 자막 생성 언어를 선택합니다.")
    st.markdown("3. stable-ts: 자막 파일의 time stamp를 안정화하는 모드입니다. (권장)")
    st.markdown("4. Arrange Options: 자막 파일의 후처리 방식을 선택합니다.")
    st.markdown("5. Prompt: 자막 생성시 AI가 참고할만한 Prompt를 입력합니다.")
