### English ver.
import streamlit as st
from modules import auth, ui

st.set_page_config(page_title="AskOnTube", page_icon="🎥", layout="wide")


def main():
    ui.show_header()

    if 'user' not in st.session_state or not st.session_state.user:
        show_auth_forms()
    else:
        show_main_menu()


def show_auth_forms():
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        show_login_form()

    with tab2:
        show_registration_form()


def show_login_form():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = auth.authenticate_user(username, password)
        if user:
            st.session_state.user = user
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Login failed. Please check your username and password.")


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

    st.page_link("pages/01_process_video.py", label="Process New Video", icon="🎥")
    st.page_link("pages/02_ask_question.py", label="Ask a Question", icon="❓")
    st.page_link("pages/03_video_list.py", label="Video List", icon="📋")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()


if __name__ == "__main__":
    main()


# ###아래는 한국어 코드
# def main():
#     ui.show_header()
#
#     if 'user' not in st.session_state or not st.session_state.user:
#         show_auth_forms()
#     else:
#         show_main_menu()
#
#
# def show_auth_forms():
#     tab1, tab2 = st.tabs(["로그인", "회원가입"])
#
#     with tab1:
#         show_login_form()
#
#     with tab2:
#         show_registration_form()
#
#
# def show_login_form():
#     st.subheader("로그인")
#     username = st.text_input("사용자명", key="login_username")
#     password = st.text_input("비밀번호", type="password", key="login_password")
#     if st.button("로그인"):
#         user = auth.authenticate_user(username, password)
#         if user:
#             st.session_state.user = user
#             st.success("로그인 성공!")
#             st.rerun()
#         else:
#             st.error("로그인 실패. 사용자명과 비밀번호를 확인하세요.")
#
#
# def show_registration_form():
#     st.subheader("회원가입")
#     new_username = st.text_input("새 사용자명", key="reg_username")
#     new_password = st.text_input("새 비밀번호", type="password", key="reg_password")
#     confirm_password = st.text_input("비밀번호 확인", type="password", key="confirm_password")
#
#     if st.button("회원가입"):
#         if new_password != confirm_password:
#             st.error("비밀번호가 일치하지 않습니다.")
#         elif auth.register_user(new_username, new_password):
#             st.success("회원가입 성공! 이제 로그인할 수 있습니다.")
#         else:
#             st.error("회원가입 실패. 이미 존재하는 사용자명일 수 있습니다.")
#
#
# def show_main_menu():
#     st.write(f"환영합니다, {st.session_state.user['username']}님!")
#
#     st.page_link("pages/01_process_video.py", label="새 영상 처리", icon="🎥")
#     st.page_link("pages/02_ask_question.py", label="질문하기", icon="❓")
#     st.page_link("pages/03_video_list.py", label="영상 목록", icon="📋")
#
#     if st.button("로그아웃"):
#         st.session_state.user = None
#         st.rerun()
#
#
# if __name__ == "__main__":
#     main()
