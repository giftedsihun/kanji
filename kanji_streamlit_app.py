import streamlit as st
import json
import random

# 페이지 설정
st.set_page_config(
    page_title="한자 암기 프로그램",
    page_icon="📚",
    layout="centered"
)

# 한자 데이터 로드
@st.cache_data
def load_kanji_data():
    with open('kanji_data_with_meaning.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 세션 상태 초기화
def init_session_state():
    if 'kanji_data' not in st.session_state:
        st.session_state.kanji_data = load_kanji_data()
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'score' not in st.session_state:
        st.session_state.score = {'correct': 0, 'total': 0}
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'user_meaning' not in st.session_state:
        st.session_state.user_meaning = ""
    if 'user_reading' not in st.session_state:
        st.session_state.user_reading = ""
    if 'mode' not in st.session_state:
        st.session_state.mode = "both"  # "meaning", "reading", "both"

def reset_inputs():
    st.session_state.user_meaning = ""
    st.session_state.user_reading = ""
    st.session_state.show_answer = False

def check_answer():
    current_kanji = st.session_state.kanji_data[st.session_state.current_index]
    
    if st.session_state.mode == "meaning":
        is_correct = st.session_state.user_meaning.strip() == current_kanji['meaning']
    elif st.session_state.mode == "reading":
        is_correct = st.session_state.user_reading.strip() == current_kanji['korean_reading']
    else:  # both
        meaning_correct = st.session_state.user_meaning.strip() == current_kanji['meaning']
        reading_correct = st.session_state.user_reading.strip() == current_kanji['korean_reading']
        is_correct = meaning_correct and reading_correct
    
    st.session_state.score['total'] += 1
    if is_correct:
        st.session_state.score['correct'] += 1
    
    st.session_state.show_answer = True

def next_kanji():
    if st.session_state.current_index < len(st.session_state.kanji_data) - 1:
        st.session_state.current_index += 1
        reset_inputs()
    else:
        st.session_state.quiz_completed = True

def reset_quiz():
    st.session_state.current_index = 0
    st.session_state.score = {'correct': 0, 'total': 0}
    st.session_state.quiz_completed = False
    reset_inputs()

# 메인 앱
def main():
    init_session_state()
    
    # 제목
    st.title("📚 한자 암기 프로그램")
    st.markdown("일본 상용한자를 한국어 뜻과 음으로 학습하세요")
    
    # 모드 선택
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("뜻만", use_container_width=True, type="primary" if st.session_state.mode == "meaning" else "secondary"):
            st.session_state.mode = "meaning"
            reset_inputs()
    with col2:
        if st.button("음만", use_container_width=True, type="primary" if st.session_state.mode == "reading" else "secondary"):
            st.session_state.mode = "reading"
            reset_inputs()
    with col3:
        if st.button("뜻 + 음", use_container_width=True, type="primary" if st.session_state.mode == "both" else "secondary"):
            st.session_state.mode = "both"
            reset_inputs()
    
    st.divider()
    
    # 진행률 표시
    progress = (st.session_state.current_index + 1) / len(st.session_state.kanji_data)
    accuracy = (st.session_state.score['correct'] / st.session_state.score['total'] * 100) if st.session_state.score['total'] > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("진행률", f"{st.session_state.current_index + 1} / {len(st.session_state.kanji_data)}")
    with col2:
        st.metric("정답률", f"{accuracy:.1f}%")
    
    st.progress(progress)
    
    # 퀴즈 완료 체크
    if hasattr(st.session_state, 'quiz_completed') and st.session_state.quiz_completed:
        st.success("🎉 모든 한자를 완료했습니다!")
        st.balloons()
        
        final_score = st.session_state.score['correct']
        total_questions = st.session_state.score['total']
        final_accuracy = (final_score / total_questions * 100) if total_questions > 0 else 0
        
        st.markdown(f"""
        ### 최종 결과
        - 총 문제 수: {total_questions}개
        - 정답 수: {final_score}개
        - 정답률: {final_accuracy:.1f}%
        """)
        
        if st.button("다시 시작", use_container_width=True, type="primary"):
            reset_quiz()
            st.rerun()
        return
    
    # 현재 한자 표시
    current_kanji = st.session_state.kanji_data[st.session_state.current_index]
    
    # 한자 카드
    with st.container():
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px; margin: 1rem 0;">
            <h1 style="font-size: 4rem; margin: 0; color: #1f1f1f;">{current_kanji['kanji']}</h1>
            {f'<p style="color: #666; margin: 0.5rem 0;">정자체: {current_kanji["traditional"]}</p>' if current_kanji['traditional'] else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # 입력 필드
    if not st.session_state.show_answer:
        if st.session_state.mode in ["meaning", "both"]:
            st.session_state.user_meaning = st.text_input(
                "뜻을 입력하세요:",
                value=st.session_state.user_meaning,
                placeholder="예: 사랑",
                key="meaning_input"
            )
        
        if st.session_state.mode in ["reading", "both"]:
            st.session_state.user_reading = st.text_input(
                "한국 음을 입력하세요:",
                value=st.session_state.user_reading,
                placeholder="예: 애",
                key="reading_input"
            )
        
        # 답안 확인 버튼
        if st.button("답안 확인", use_container_width=True, type="primary"):
            check_answer()
            st.rerun()
    
    # 답안 표시
    if st.session_state.show_answer:
        # 정답/오답 표시
        current_kanji = st.session_state.kanji_data[st.session_state.current_index]
        
        if st.session_state.mode == "meaning":
            is_correct = st.session_state.user_meaning.strip() == current_kanji['meaning']
        elif st.session_state.mode == "reading":
            is_correct = st.session_state.user_reading.strip() == current_kanji['korean_reading']
        else:  # both
            meaning_correct = st.session_state.user_meaning.strip() == current_kanji['meaning']
            reading_correct = st.session_state.user_reading.strip() == current_kanji['korean_reading']
            is_correct = meaning_correct and reading_correct
        
        if is_correct:
            st.success("✅ 정답입니다!")
        else:
            st.error("❌ 틀렸습니다.")
        
        # 정답 표시
        st.markdown("### 정답")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**뜻:** {current_kanji['meaning']}")
        with col2:
            st.info(f"**한국 음:** {current_kanji['korean_reading']}")
        
        # 예시 단어
        if current_kanji['examples']:
            st.markdown("### 예시 단어")
            examples_text = " • ".join(current_kanji['examples'])
            st.markdown(f"• {examples_text}")
        
        # 다음 버튼
        if st.session_state.current_index < len(st.session_state.kanji_data) - 1:
            if st.button("다음 한자", use_container_width=True, type="primary"):
                next_kanji()
                st.rerun()
        else:
            if st.button("결과 보기", use_container_width=True, type="primary"):
                st.session_state.quiz_completed = True
                st.rerun()
    
    # 사이드바에 점수 표시
    with st.sidebar:
        st.markdown("### 현재 점수")
        st.metric("정답", st.session_state.score['correct'])
        st.metric("총 문제", st.session_state.score['total'])
        
        st.divider()
        
        if st.button("퀴즈 초기화", use_container_width=True):
            reset_quiz()
            st.rerun()

if __name__ == "__main__":
    main()

