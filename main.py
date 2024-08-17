import streamlit as st
import time 
from modules import auth, ui

st.set_page_config(page_title="AskOnTube", page_icon="🎥", layout="wide")

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

    if 'user' not in st.session_state or not st.session_state.user:
        show_auth_forms()
    else:
        show_main_menu()



def show_auth_forms():
    # 카드 형태로 로그인/회원가입 폼 감싸기
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            show_login_form()

        with tab2:
            show_registration_form()
        st.markdown('</div>', unsafe_allow_html=True)


def show_login_form():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = auth.authenticate_user(username, password)
        if user:
            st.session_state.user = user
            st.session_state.login_time = time.time()  # 로그인 시각 저장
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Login failed. Please check your username and password.")


def check_session_timeout():
    """세션 타임아웃을 확인하고 세션을 갱신하는 함수"""
    if 'login_time' in st.session_state:
        current_time = time.time()
        session_duration = current_time - st.session_state.login_time
        if session_duration > 1800:  # 30분 = 1800초
            st.session_state.user = None
            st.session_state.login_time = None
            st.warning("Your session has expired. Please log in again.")
            st.rerun()
        else:
            st.session_state.login_time = current_time  # 세션 시간 갱신


def show_registration_form():
    st.subheader("Register")
    new_username = st.text_input("New Username", key="reg_username")
    new_password = st.text_input("New Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        elif auth.register_user(new_username, new_password):
            st.success("Registration successful! You can now log in.")
        else:
            st.error("Registration failed. The username may already exist.")


def show_main_menu():
    st.write(f"Welcome, {st.session_state.user['username']}!")
    
    # 사용자 활동 시 세션 갱신
    st.session_state.login_time = time.time()

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link("pages/01_process_video.py", label="Process New Video", icon="🎥")
        with col2:
            st.page_link("pages/02_ask_question.py", label="Ask a Question", icon="❓")
        with col3:
            st.page_link("pages/03_video_list.py", label="Video List", icon="📋")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Logout", key="logout-button"):
        st.session_state.user = None
        st.rerun()



if __name__ == "__main__":
    main()
