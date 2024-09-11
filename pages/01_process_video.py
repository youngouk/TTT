import streamlit as st
from modules import video_processing, database
import time

st.set_page_config(page_title="동영상 처리 - 유튜브 질문하기", page_icon="🎥", layout="wide")


# Update the maximum video duration to 30 minutes
video_processing.MAX_VIDEO_DURATION = 30 * 60  # 30 minutes in seconds

def show_video_processing_form():
    st.header("새 YouTube 동영상 처리")
    st.warning(f"참고: 현재 30분 미만의 동영상만 처리할 수 있습니다.")

    video_url = st.text_input("YouTube 동영상 URL 입력")
    if st.button("동영상 처리", key="process_video_button"):
        if not video_url:
            st.error("YouTube 동영상 URL을 입력해주세요.")
            return

        try:
            user_id = st.session_state.user['_id']
            with st.spinner("동영상 정보 가져오는 중... ⏳"):
                title, channel, duration = video_processing.get_video_info(video_url)
                if duration > video_processing.MAX_VIDEO_DURATION:
                    st.error(f"이 동영상은 {duration // 60}분 길이입니다. 30분 미만의 동영상만 처리할 수 있습니다.")
                    return
                estimated_time = (duration // 600) * 60 + (duration % 600) // 10  # Calculation based on 60 seconds per 10 minutes
                st.info(f"**{title}** ({channel}) - 예상 처리 시간: 약 {estimated_time}초 ⏰")

            # Check if the video has been processed before
            _, video_id = video_processing.extract_video_id_and_process(video_url)
            existing_video = video_processing.get_existing_video(video_id)

            is_new_video = False
            if existing_video:
                st.info(f"이 동영상은 이미 처리되었습니다. 기존 데이터를 사용합니다.")
                video_processing.update_user_for_video(existing_video['_id'], user_id)
                video_id = existing_video['_id']
            else:
                is_new_video = True
                progress_bar = st.progress(0, text="동영상 처리 중... 🏃")
                start_time = time.time()

                video_id = video_processing.process_video(video_url, user_id, progress_bar)

                end_time = time.time()
                elapsed_time = end_time - start_time
                st.success(f"동영상 처리 완료! 🎉 (소요 시간: {video_processing.format_time(elapsed_time)})")

            st.session_state.last_processed_video_id = video_id

            st.write("다음으로 무엇을 하시겠습니까?")
            col1, col2 = st.columns(2)
            with col1:
                st.page_link("pages/02_ask_question.py", label="이 동영상에 대해 질문하기", icon="💬")
            with col2:
                st.page_link("pages/03_video_list.py", label="처리된 동영상 목록 보기", icon="📋")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

def main():
    st.title("⌛ 새 YouTube 동영상 처리")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("동영상을 처리하려면 로그인이 필요합니다.")
        st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
        return

    show_video_processing_form()

if __name__ == "__main__":
    main()
