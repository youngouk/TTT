import streamlit as st
from modules import video_processing, database
import time

st.set_page_config(page_title="Process Video - AskOnTube", page_icon="🎥", layout="wide")


def show_video_processing_form():
    st.header("새 YouTube 영상 처리")
    st.warning(f"주의: 현재 {video_processing.MAX_VIDEO_DURATION // 60}분 이하의 영상만 처리 가능합니다.")

    video_url = st.text_input("YouTube 영상 URL 입력")
    if st.button("영상 처리", key="process_video_button"):
        if not video_url:
            st.error("YouTube 영상 URL을 입력해주세요.")
            return

        try:
            user_id = st.session_state.user['_id']
            with st.spinner("영상 정보 가져오는 중... ⏳"):
                title, channel, duration = video_processing.get_video_info(video_url)
                estimated_time = (duration // 600) * 60 + (duration % 600) // 10  # 10분당 60초 기준 계산
                st.info(f"**{title}** ({channel}) - 예상 처리 시간: 약 {estimated_time}초 ⏰")

            # 기존에 처리된 영상인지 확인
            _, video_id = video_processing.extract_video_id_and_process(video_url)
            existing_video = video_processing.get_existing_video(video_id)

            is_new_video = False
            if existing_video:
                st.info(f"이 영상은 이미 처리되었습니다. 기존 데이터를 사용합니다.")
                video_processing.update_user_for_video(existing_video['_id'], user_id)
                video_id = existing_video['_id']
            else:
                is_new_video = True
                progress_bar = st.progress(0, text="영상 처리 중... 🏃")
                start_time = time.time()

                video_id = video_processing.process_video(video_url, user_id, progress_bar)

                end_time = time.time()
                elapsed_time = end_time - start_time
                st.success(f"영상 처리 완료! 🎉  ({video_processing.format_time(elapsed_time)} 소요)")

            st.session_state.last_processed_video_id = video_id

        #     # 태그 정보 가져오기 (Session State 확인)
        #     video_tags = st.session_state.get('video_tags', {}).get(video_id, [])
        #     has_tags = bool(video_tags)
        #
        #     # 태그 입력 섹션 (새 영상이거나 태그가 없는 경우에만 표시)
        #     if is_new_video or not has_tags:
        #         st.markdown("<h4 style='font-size: 1.1em;'>태그 추가</h4>", unsafe_allow_html=True)
        #         col1, col2 = st.columns([3, 1])
        #         with col1:
        #             input_key = f"new_tag_{video_id}_{st.session_state.get('tag_input_key', 0)}"
        #             new_tag = st.text_input("새 태그 추가", key=input_key, placeholder="새 태그 입력")
        #         with col2:
        #             if st.button("태그 추가", key=f"add_tag_{video_id}"):
        #                 if new_tag:
        #                     if database.add_tag_to_video(video_id, new_tag):
        #                         st.success("태그가 추가되었습니다.")
        #                         # Session State를 사용하여 태그 정보 업데이트
        #                         if 'video_tags' not in st.session_state:
        #                             st.session_state['video_tags'] = {}
        #                         st.session_state['video_tags'][video_id] = database.get_video_tags(video_id)
        #                         st.session_state['tag_input_key'] = st.session_state.get('tag_input_key', 0) + 1
        #                     else:
        #                         st.warning("태그를 추가할 수 없습니다. (최대 3개)")
        #                 else:
        #                     st.warning("태그를 입력해주세요.")
        #     else:
        #         st.info(f"현재 태그: {', '.join(video_tags)}")
        #
            st.write("다음으로 무엇을 하시겠습니까?")
            col1, col2 = st.columns(2)
            with col1:
                st.page_link("pages/02_ask_question.py", label="이 영상에 대해 질문하기", icon="💬")
            with col2:
                st.page_link("pages/03_video_list.py", label="처리된 영상 목록 보기", icon="📋")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")


def main():
    st.title("⌛ Process New YouTube Video")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("영상을 처리하려면 로그인이 필요합니다.")
        st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
        return

    show_video_processing_form()


if __name__ == "__main__":
    main()