# main.py

import streamlit as st
import time 
from modules import auth, ui

st.set_page_config(page_title="유튜브 질문하기", page_icon="🎥", layout="wide")

# CSS 스타일 적용 (개선된 버전)
st.markdown(
    """
    <style>
    /* 폰트 변경 */
    body {
        font-family: 'Arial', sans-serif; /* 폰트 변경 예시, 원하는 폰트로 변경 가능 */
    }

    /* 버튼 스타일 변경 */
    .stButton button {
        background-color: #007bff; /* 파란색 */
        border: none;
        color: white;
        padding: 10px 20px; /* 버튼 크기 조정 */
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        border-radius: 5px; /* 둥근 모서리 */
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2); /* 그림자 효과 */
    }

    .stButton button:hover {
        background-color: #0056b3; /* 짙은 파란색 */
    }

    /* 로그아웃 버튼 스타일 */
    #logout-button {
        background-color: #dc3545; /* 빨간색 */
    }

    #logout-button:hover {
        background-color: #c82333; /* 짙은 빨간색 */
    }

    /* 카드 스타일 */
    .card {
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f5f5f5; /* 밝은 회색 배경 추가 */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def main():
    ui.show_header()
    check_session_timeout()  # 세션 타임아웃 체크 및 갱신

    # OAuth 콜백 처리
    query_params = st.query_params  # st.experimental_get_query_params() 대신 st.query_params 사용
    if "code" in query_params:
        code = query_params["code"]
        if isinstance(code, list):
            code = code[0]  # 여러 값이 올 경우 첫 번째 값 사용
        user = auth.authenticate_google_user(code)
        if user:
            st.session_state.user = {
                "_id": str(user["_id"]),
                "email": user["email"],
                "name": user.get("name", ""),
                "picture": user.get("picture", "")
            }
            st.session_state.login_time = time.time()
            st.success("Google 계정으로 로그인 성공!")
            st.query_params.clear()  # URL에서 query params 제거
            st.experimental_rerun()
        else:
            st.error("Google 계정으로 로그인하는 중 오류가 발생했습니다.")
            st.query_params.clear()  # 오류 발생 시 query params 제거

    if 'user' not in st.session_state or not st.session_state.user:
        show_auth_forms()
    else:
        show_main_menu()

def show_auth_forms():
    # 카드 형태로 Google OAuth 로그인 버튼 감싸기
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("로그인")
        auth_url = auth.get_google_auth_url()
        # 버튼을 HTML 앵커 태그로 감싸 Google OAuth 흐름 시작
        st.markdown(
            f'''
            <a href="{auth_url}" target="_self">
                <button>Google 계정으로 로그인</button>
            </a>
            ''',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

def check_session_timeout():
    """세션 타임아웃을 확인하고 세션을 갱신하는 함수"""
    if 'login_time' in st.session_state:
        current_time = time.time()
        session_duration = current_time - st.session_state.login_time
        if session_duration > 1800:  # 30분 = 1800초
            st.session_state.user = None
            st.session_state.login_time = None
            st.warning("세션이 만료되었습니다. 다시 로그인해주세요.")
            st.experimental_rerun()
        else:
            st.session_state.login_time = current_time  # 세션 시간 갱신

def show_main_menu():
    st.write(f"환영합니다, {st.session_state.user['name']}님!")

    # 사용자 활동 시 세션 갱신
    st.session_state.login_time = time.time()

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link("pages/01_process_video.py", label="새 동영상 처리", icon="🎥")
        with col2:
            st.page_link("pages/02_ask_question.py", label="질문하기", icon="❓")
        with col3:
            st.page_link("pages/03_video_list.py", label="동영상 목록", icon="📋")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("로그아웃", key="logout-button"):
        st.session_state.user = None
        st.rerun()

if __name__ == "__main__":
    main()