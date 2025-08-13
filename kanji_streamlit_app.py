import streamlit as st
import json
import random
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="한자 암기 프로그램",
    page_icon="📚",
    layout="centered"
)

# 한자 데이터 로드
@st.cache_data
def load_kanji_data():
    with open("kanji_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 세션 상태 초기화
def init_session_state():
    if "kanji_data" not in st.session_state:
        st.session_state.kanji_data = load_kanji_data()
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "score" not in st.session_state:
        st.session_state.score = {"correct": 0, "total": 0}
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    if "user_meaning" not in st.session_state:
        st.session_state.user_meaning = ""
    if "user_korean_reading" not in st.session_state:
        st.session_state.user_korean_reading = ""
    if "user_japanese_reading" not in st.session_state:
        st.session_state.user_japanese_reading = ""
    if "mode" not in st.session_state:
        st.session_state.mode = "input"  # "input", "multiple_choice"
    if "quiz_type" not in st.session_state:
        st.session_state.quiz_type = "meaning"  # "meaning", "korean_reading", "japanese_reading", "both"
    if "multiple_choice_options" not in st.session_state:
        st.session_state.multiple_choice_options = []
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "quiz"  # "quiz", "word_list"

def reset_inputs():
    st.session_state.user_meaning = ""
    st.session_state.user_korean_reading = ""
    st.session_state.user_japanese_reading = ""
    st.session_state.show_answer = False
    st.session_state.selected_option = None
    st.session_state.multiple_choice_options = []

def generate_multiple_choice_options(correct_kanji):
    all_kanji = [k["kanji"] for k in st.session_state.kanji_data]
    options = [correct_kanji["kanji"]]
    
    while len(options) < 5:
        random_kanji = random.choice(all_kanji)
        if random_kanji not in options:
            options.append(random_kanji)
    
    random.shuffle(options)
    st.session_state.multiple_choice_options = options

def check_answer():
    current_kanji = st.session_state.kanji_data[st.session_state.current_index]
    is_correct = False

    if st.session_state.mode == "input":
        if st.session_state.quiz_type == "meaning":
            is_correct = st.session_state.user_meaning.strip() == current_kanji["meaning"]
        elif st.session_state.quiz_type == "korean_reading":
            is_correct = st.session_state.user_korean_reading.strip() == current_kanji["korean_reading"]
        elif st.session_state.quiz_type == "japanese_reading":
            user_inputs = [s.strip() for s in st.session_state.user_japanese_reading.split(",")]
            is_correct = any(jp in current_kanji["japanese_pronunciation"] for jp in user_inputs)
        elif st.session_state.quiz_type == "both":
            meaning_correct = st.session_state.user_meaning.strip() == current_kanji["meaning"]
            korean_reading_correct = st.session_state.user_korean_reading.strip() == current_kanji["korean_reading"]
            japanese_reading_correct = False
            if st.session_state.user_japanese_reading:
                user_inputs = [s.strip() for s in st.session_state.user_japanese_reading.split(",")]
                japanese_reading_correct = any(jp in current_kanji["japanese_pronunciation"] for jp in user_inputs)
            
            is_correct = meaning_correct and korean_reading_correct and japanese_reading_correct
    elif st.session_state.mode == "multiple_choice":
        is_correct = st.session_state.selected_option == current_kanji["kanji"]
    
    st.session_state.score["total"] += 1
    if is_correct:
        st.session_state.score["correct"] += 1
    
    st.session_state.show_answer = True

def next_kanji():
    if st.session_state.current_index < len(st.session_state.kanji_data) - 1:
        st.session_state.current_index += 1
        reset_inputs()
        if st.session_state.mode == "multiple_choice":
            generate_multiple_choice_options(st.session_state.kanji_data[st.session_state.current_index])
    else:
        st.session_state.quiz_completed = True

def reset_quiz():
    st.session_state.current_index = 0
    st.session_state.score = {"correct": 0, "total": 0}
    st.session_state.quiz_completed = False
    reset_inputs()
    if st.session_state.mode == "multiple_choice":
        generate_multiple_choice_options(st.session_state.kanji_data[st.session_state.current_index])

def show_word_list():
    st.title("📋 한자 목록")
    
    # 데이터프레임 생성
    data = []
    for kanji_item in st.session_state.kanji_data:
        data.append({
            "한자": kanji_item["kanji"],
            "뜻": kanji_item["meaning"],
            "한국 음": kanji_item["korean_reading"],
            "일본 음": ", ".join(kanji_item["japanese_pronunciation"]),
            "예시 단어": ", ".join(kanji_item["examples"]) if kanji_item["examples"] else "-"
        })
    
    df = pd.DataFrame(data)
    
    # 표 표시
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "한자": st.column_config.TextColumn("한자", width="small"),
            "뜻": st.column_config.TextColumn("뜻", width="medium"),
            "한국 음": st.column_config.TextColumn("한국 음", width="small"),
            "일본 음": st.column_config.TextColumn("일본 음", width="medium"),
            "예시 단어": st.column_config.TextColumn("예시 단어", width="large")
        }
    )
    
    st.markdown(f"**총 {len(df)}개의 한자**")

def show_quiz():
    # 진행률 표시
    progress = (st.session_state.current_index + 1) / len(st.session_state.kanji_data)
    accuracy = (st.session_state.score["correct"] / st.session_state.score["total"] * 100) if st.session_state.score["total"] > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("진행률", f"{st.session_state.current_index + 1} / {len(st.session_state.kanji_data)}")
    with col2:
        st.metric("정답률", f"{accuracy:.1f}%")
    
    st.progress(progress)
    
    # 퀴즈 완료 체크
    if hasattr(st.session_state, "quiz_completed") and st.session_state.quiz_completed:
        st.success("🎉 모든 한자를 완료했습니다!")
        st.balloons()
        
        final_score = st.session_state.score["correct"]
        total_questions = st.session_state.score["total"]
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
            <h1 style="font-size: 4rem; margin: 0; color: #1f1f1f;">{current_kanji["kanji"]}</h1>
            {f'<p style="color: #666; margin: 0.5rem 0;">정자체: {current_kanji["traditional"]}</p>' if current_kanji["traditional"] else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # 입력 필드 또는 객관식
    if not st.session_state.show_answer:
        if st.session_state.mode == "input":
            if st.session_state.quiz_type == "meaning":
                st.session_state.user_meaning = st.text_input(
                    "뜻을 입력하세요:",
                    value=st.session_state.user_meaning,
                    placeholder="예: 사랑",
                    key="meaning_input"
                )
            elif st.session_state.quiz_type == "korean_reading":
                st.session_state.user_korean_reading = st.text_input(
                    "한국 음을 입력하세요:",
                    value=st.session_state.user_korean_reading,
                    placeholder="예: 애",
                    key="korean_reading_input"
                )
            elif st.session_state.quiz_type == "japanese_reading":
                st.session_state.user_japanese_reading = st.text_input(
                    "일본 음을 입력하세요 (여러 개일 경우 쉼표로 구분):",
                    value=st.session_state.user_japanese_reading,
                    placeholder="例: アイ, あ-る",
                    key="japanese_reading_input"
                )
            elif st.session_state.quiz_type == "both":
                st.session_state.user_meaning = st.text_input(
                    "뜻을 입력하세요:",
                    value=st.session_state.user_meaning,
                    placeholder="예: 사랑",
                    key="meaning_input"
                )
                st.session_state.user_korean_reading = st.text_input(
                    "한국 음을 입력하세요:",
                    value=st.session_state.user_korean_reading,
                    placeholder="예: 애",
                    key="korean_reading_input"
                )
                # 일본 음 입력 필드 삭제됨

            
            # 답안 확인 버튼
            if st.button("답안 확인", use_container_width=True, type="primary"):
                check_answer()
                st.rerun()
        
        elif st.session_state.mode == "multiple_choice":
            if not st.session_state.multiple_choice_options:
                generate_multiple_choice_options(current_kanji)

            # 뜻과 음 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**뜻:** {current_kanji['meaning']}")
            with col2:
                st.info(f"**한국 음:** {current_kanji['korean_reading']}")
            with col3:
                st.info(f"**일본 음:** {', '.join(current_kanji['japanese_pronunciation'])}")

            st.markdown("### 다음 중 이 한자에 해당하는 것은?")
            
            for option in st.session_state.multiple_choice_options:
                if st.button(option, key=f"mc_option_{option}", use_container_width=True):
                    st.session_state.selected_option = option
                    check_answer()
                    st.rerun()

    # 답안 표시
    if st.session_state.show_answer:
        # 정답/오답 표시
        current_kanji = st.session_state.kanji_data[st.session_state.current_index]
        
        is_correct = False
        if st.session_state.mode == "input":
            if st.session_state.quiz_type == "meaning":
                is_correct = st.session_state.user_meaning.strip() == current_kanji["meaning"]
            elif st.session_state.quiz_type == "korean_reading":
                is_correct = st.session_state.user_korean_reading.strip() == current_kanji["korean_reading"]
            elif st.session_state.quiz_type == "japanese_reading":
                user_inputs = [s.strip() for s in st.session_state.user_japanese_reading.split(",")]
                is_correct = any(jp in current_kanji["japanese_pronunciation"] for jp in user_inputs)
            elif st.session_state.quiz_type == "both":
                meaning_correct = st.session_state.user_meaning.strip() == current_kanji["meaning"]
                korean_reading_correct = st.session_state.user_korean_reading.strip() == current_kanji["korean_reading"]
                japanese_reading_correct = False
                if st.session_state.user_japanese_reading:
                    user_inputs = [s.strip() for s in st.session_state.user_japanese_reading.split(",")]
                    japanese_reading_correct = any(jp in current_kanji["japanese_pronunciation"] for jp in user_inputs)
                is_correct = meaning_correct and korean_reading_correct and japanese_reading_correct
        elif st.session_state.mode == "multiple_choice":
            is_correct = st.session_state.selected_option == current_kanji["kanji"]

        if is_correct:
            st.success("✅ 정답입니다!")
        else:
            st.error("❌ 틀렸습니다.")
        
        # 정답 표시
        st.markdown("### 정답")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**뜻:** {current_kanji['meaning']}")
        with col2:
            st.info(f"**한국 음:** {current_kanji['korean_reading']}")
        with col3:
            st.info(f"**일본 음:** {', '.join(current_kanji['japanese_pronunciation'])}")
        
        # 예시 단어
        if current_kanji["examples"]:
            st.markdown("### 예시 단어")
            examples_text = " • ".join(current_kanji["examples"])
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

# 메인 앱
def main():
    init_session_state()
    
    # 제목
    st.title("📚 한자 암기 프로그램")
    st.markdown("일본 상용한자를 한국어 뜻과 음으로 학습하세요")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("메뉴")
        
        # 화면 모드 선택
        view_mode = st.radio(
            "화면 선택",
            ("퀴즈", "단어 목록"),
            index=0 if st.session_state.view_mode == "quiz" else 1
        )
        
        if view_mode == "퀴즈":
            st.session_state.view_mode = "quiz"
        else:
            st.session_state.view_mode = "word_list"
        
        if st.session_state.view_mode == "quiz":
            st.divider()
            
            # 학습 모드 선택 (입력 vs 객관식)
            st.subheader("학습 모드")
            mode_selection = st.radio(
                "모드 선택",
                ("입력 모드", "객관식 모드"),
                index=0 if st.session_state.mode == "input" else 1
            )
            if mode_selection == "입력 모드":
                st.session_state.mode = "input"
            else:
                st.session_state.mode = "multiple_choice"

            # 퀴즈 타입 선택 (뜻만, 한국 음만, 일본 음만, 뜻 + 음)
            st.subheader("퀴즈 타입")
            quiz_type_selection = st.radio(
                "타입 선택",
                ("뜻만", "한국 음만", "일본 음만", "뜻 + 음"),
                index=["meaning", "korean_reading", "japanese_reading", "both"].index(st.session_state.quiz_type)
            )
            if quiz_type_selection == "뜻만":
                st.session_state.quiz_type = "meaning"
            elif quiz_type_selection == "한국 음만":
                st.session_state.quiz_type = "korean_reading"
            elif quiz_type_selection == "일본 음만":
                st.session_state.quiz_type = "japanese_reading"
            else:
                st.session_state.quiz_type = "both"

            st.divider()

            # 현재 점수 표시
            st.subheader("현재 점수")
            st.metric("정답", st.session_state.score["correct"])
            st.metric("총 문제", st.session_state.score["total"])
            
            st.divider()
            
            if st.button("퀴즈 초기화", use_container_width=True):
                reset_quiz()
                st.rerun()
    
    # 메인 화면 표시
    if st.session_state.view_mode == "quiz":
        show_quiz()
    else:
        show_word_list()

if __name__ == "__main__":
    main()


