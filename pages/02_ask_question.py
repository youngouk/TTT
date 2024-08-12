import streamlit as st
from modules import database, nlp

st.set_page_config(page_title="Ask Questions - AskOnTube", page_icon="❓", layout="wide")

def show_individual_video_question(user_id):
    user_videos = database.get_user_videos(user_id)
    if user_videos:
        video_options = {f"{v['title']} - {v['channel']}": v['video_id'] for v in user_videos}
        selected_video_title = st.selectbox("Select a video", list(video_options.keys()), key="individual_video_selector")
        selected_video_id = video_options[selected_video_title]

        question = st.text_input("Enter your question")
        if st.button("Get Answer"):
            if question:
                with st.spinner("Generating answer..."):
                    try:
                        video_data = database.get_video_info_from_db([selected_video_id])
                        if video_data and 'transcript' in video_data[0]:
                            response = nlp.generate_response(question, [video_data[0]['transcript']])
                            display_response(question, response)
                        else:
                            st.error("Transcript for the selected video not found.")
                    except Exception as e:
                        st.error(f"An error occurred while generating the answer: {str(e)}")
            else:
                st.warning("Please enter a question.")
    else:
        st.info("No processed videos found. Please process a video first.")
        st.page_link("pages/01_process_video.py", label="Process a new video", icon="🎥")

def show_tag_based_question(user_id):
    all_tags = database.get_all_tags()
    selected_tags = st.multiselect("Select tags", all_tags, key="tag_selector")

    if selected_tags:
        videos = database.get_videos_by_tags(selected_tags)
        if videos:
            st.write(f"Number of selected videos: {len(videos)}")

            # Limit video titles to the first 10 characters and add ellipsis
            video_titles = [f"{v['title'][:10]}..." for v in videos]

            # Join the limited titles into a string
            titles_str = ", ".join(video_titles)

            # Truncate the resulting string if it's too long
            max_display_length = 100  # Set maximum display length
            if len(titles_str) > max_display_length:
                titles_str = titles_str[:max_display_length] + "..."

            st.write(f"Selected videos: {titles_str}")

            question = st.text_input("Enter your question")
            if st.button("Get Answer"):
                if question:
                    with st.spinner("Generating answer..."):
                        try:
                            video_data = database.get_video_info_from_db([v['video_id'] for v in videos])
                            if video_data:
                                transcripts = [v['transcript'] for v in video_data if 'transcript' in v]
                                response = nlp.generate_response(question, transcripts)
                                display_response(question, response)
                            else:
                                st.error("Transcripts for the selected videos not found.")
                        except Exception as e:
                            st.error(f"An error occurred while generating the answer: {str(e)}")
                else:
                    st.warning("Please enter a question.")
        else:
            st.warning("No videos found for the selected tags.")
    else:
        st.info("Select tags to filter videos.")

def display_response(question, response):
    st.markdown("### Question:")
    st.write(question)
    st.divider()
    st.markdown("### Answer:")
    st.write(response)

def main():
    st.title("💬 Ask Questions About Videos")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("You need to log in to use the question-asking feature.")
        st.page_link("main.py", label="Go to Login Page", icon="🏠")
        return

    user_id = st.session_state.user['_id']

    # Question mode selection
    question_mode = st.radio("Select question mode", ["Question based on a single video", "Question based on multiple videos by tags"])

    if question_mode == "Question based on a single video":
        show_individual_video_question(user_id)
    else:
        show_tag_based_question(user_id)

if __name__ == "__main__":
    main()

# ### 한국어 코드
# def show_individual_video_question(user_id):
#     user_videos = database.get_user_videos(user_id)
#     if user_videos:
#         video_options = {f"{v['title']} - {v['channel']}": v['video_id'] for v in user_videos}
#         selected_video_title = st.selectbox("영상 선택", list(video_options.keys()), key="individual_video_selector")
#         selected_video_id = video_options[selected_video_title]
#
#         question = st.text_input("질문을 입력하세요")
#         if st.button("답변 받기"):
#             if question:
#                 with st.spinner("답변 생성 중..."):
#                     try:
#                         video_data = database.get_video_info_from_db([selected_video_id])
#                         if video_data and 'transcript' in video_data[0]:
#                             response = nlp.generate_response(question, [video_data[0]['transcript']])
#                             display_response(question, response)
#                         else:
#                             st.error("선택한 영상의 트랜스크립트를 찾을 수 없습니다.")
#                     except Exception as e:
#                         st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
#             else:
#                 st.warning("질문을 입력해주세요.")
#     else:
#         st.info("처리된 영상이 없습니다. 먼저 영상을 처리해주세요.")
#         st.page_link("pages/01_process_video.py", label="새 영상 처리하기", icon="🎥")
#
#
# def show_tag_based_question(user_id):
#     all_tags = database.get_all_tags()
#     selected_tags = st.multiselect("태그 선택", all_tags, key="tag_selector")
#
#     if selected_tags:
#         videos = database.get_videos_by_tags(selected_tags)
#         if videos:
#             st.write(f"선택된 영상 수: {len(videos)}")
#
#             # 영상 제목을 앞 10글자로 제한하고 생략 부호(...) 추가
#             video_titles = [f"{v['title'][:10]}..." for v in videos]
#
#             # 제한된 제목 목록을 문자열로 결합
#             titles_str = ", ".join(video_titles)
#
#             # 결과 문자열이 너무 길 경우 잘라내기
#             max_display_length = 100  # 최대 표시 길이 설정
#             if len(titles_str) > max_display_length:
#                 titles_str = titles_str[:max_display_length] + "..."
#
#             st.write(f"선택된 영상: {titles_str}")
#
#             question = st.text_input("질문을 입력하세요")
#             if st.button("답변 받기"):
#                 if question:
#                     with st.spinner("답변 생성 중..."):
#                         try:
#                             video_data = database.get_video_info_from_db([v['video_id'] for v in videos])
#                             if video_data:
#                                 transcripts = [v['transcript'] for v in video_data if 'transcript' in v]
#                                 response = nlp.generate_response(question, transcripts)
#                                 display_response(question, response)
#                             else:
#                                 st.error("선택한 영상의 트랜스크립트를 찾을 수 없습니다.")
#                         except Exception as e:
#                             st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
#                 else:
#                     st.warning("질문을 입력해주세요.")
#         else:
#             st.warning("선택한 태그에 해당하는 영상이 없습니다.")
#     else:
#         st.info("태그를 선택하여 영상을 필터링하세요.")
#
# def display_response(question, response):
#     st.markdown("### 질문:")
#     st.write(question)
#     st.divider()
#     st.markdown("### 답변:")
#     st.write(response)
#
# def main():
#     st.title("💬 영상에 대해 질문하기")
#
#     if 'user' not in st.session_state or not st.session_state.user:
#         st.warning("질문하기 기능을 사용하려면 로그인이 필요합니다.")
#         st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
#         return
#
#     user_id = st.session_state.user['_id']
#
#     # 질문 모드 선택
#     question_mode = st.radio("질문 모드 선택", ["하나의 영상 기반 질문", "태그에 포함된 다수 영상 기반 질문"])
#
#     if question_mode == "하나의 영상 기반 질문":
#         show_individual_video_question(user_id)
#     else:
#         show_tag_based_question(user_id)
#
# if __name__ == "__main__":
#     main()
