import streamlit as st
from modules import auth, ui

st.set_page_config(page_title="AskOnTube", page_icon="🎥", layout="wide")


def main():
    ui.show_header()

    if 'user' not in st.session_state or not st.session_state.user:
        show_login_form()
    else:
        show_main_menu()


def show_login_form():
    st.subheader("로그인")
    username = st.text_input("사용자명")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        user = auth.authenticate_user(username, password)
        if user:
            st.session_state.user = user
            st.success("로그인 성공!")
            st.rerun()
        else:
            st.error("로그인 실패. 사용자명과 비밀번호를 확인하세요.")


def show_main_menu():
    st.write(f"환영합니다, {st.session_state.user['username']}님!")

    st.page_link("pages/01_process_video.py", label="새 영상 처리", icon="🎥")
    st.page_link("pages/02_ask_question.py", label="질문하기", icon="❓")
    st.page_link("pages/03_video_list.py", label="영상 목록", icon="📋")

    if st.button("로그아웃"):
        st.session_state.user = None
        st.rerun()


if __name__ == "__main__":
    main()
