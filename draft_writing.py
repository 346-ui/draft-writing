import streamlit as st

# st.set_page_config(...)

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="초고 전용 몰입 글쓰기",
    page_icon="✍️",
    layout="centered"
)

# 2. 세션 상태 초기화
if "full_text" not in st.session_state:
    st.session_state["full_text"] = ""
if "current_input" not in st.session_state:
    st.session_state["current_input"] = ""
# 초기화 확인 버튼 상태 관리
if "confirm_reset" not in st.session_state:
    st.session_state["confirm_reset"] = False

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    target_count = st.number_input(
        "목표 글자 수", 
        min_value=50, 
        value=1000, 
        step=50,
        help="목표를 달성하면 작성한 글의 수정 잠금이 해제됩니다."
    )
    
    st.divider()
    
    show_counter = st.toggle("글자 수 표시", value=True)
    hide_history = st.toggle("몰입 모드 (이전 글 숨기기)", value=False)
    
    st.divider()
    
    st.download_button(
        label="📄 작성된 글 다운로드 (.txt)",
        data=st.session_state["full_text"],
        file_name="my_draft.txt",
        mime="text/plain"
    )
    
    # [기능 추가 1] 안전한 초기화 로직
    if st.button("🗑️ 전체 초기화"):
        st.session_state["confirm_reset"] = True

    # 초기화 버튼을 눌렀을 때만 보이는 확인 메뉴
    if st.session_state["confirm_reset"]:
        st.error("정말 모든 내용을 삭제하시겠습니까?")
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("✅ 예", use_container_width=True):
                st.session_state["full_text"] = ""
                st.session_state["confirm_reset"] = False
                st.rerun() # 화면 새로고침
        
        with col_no:
            if st.button("❌ 아니오", use_container_width=True):
                st.session_state["confirm_reset"] = False
                st.rerun()

# 4. 메인 화면 구성
st.title("✍️ 초고 전용 글쓰기 툴")

with st.expander("ℹ️ 사용법 안내 (클릭해서 열기/닫기)", expanded=True):
    st.markdown("""
    **'멈추지 말고 계속 쓰세요!'**
    
    1.  **입력창**에 문장을 입력하고 **Enter**를 누르세요.
    2.  입력한 문장은 저장되며 수정할 수 없습니다.
    3.  **목표 글자 수를 달성하면** 글이 '언락(Unlock)' 되어 복사 및 수정이 가능해집니다.
    """)

st.divider()

# 현재 글자 수 계산 및 달성 여부 확인
current_length = len(st.session_state["full_text"])
is_goal_reached = current_length >= target_count

# 프로그래스 바 및 상태 표시
if show_counter:
    progress = min(current_length / target_count, 1.0)
    
    # 목표 달성 시 초록색 축하 메시지
    if is_goal_reached:
        st.success(f"🎉 목표 달성! ({current_length}자 / {target_count}자) - 이제 글을 복사하거나 수정할 수 있습니다.")
        st.progress(1.0)
    else:
        st.progress(progress)
        st.caption(f"현재: {current_length}자 / 목표: {target_count}자 ({int(progress*100)}%)")

# 텍스트 입력 처리 함수
def submit_text():
    text = st.session_state.widget_input
    if text:
        st.session_state["full_text"] += text + "\n"
        st.session_state.widget_input = ""

# 입력창 (목표 달성 후에도 계속 쓸 수 있음)
st.text_input(
    "여기에 내용을 입력하고 Enter를 누르세요 👇",
    key="widget_input",
    on_change=submit_text,
    placeholder="생각나는 대로 적고 엔터를 누르세요."
)

# 작성된 글 보여주기 로직
st.subheader("📝 작성된 내용")

if hide_history and not is_goal_reached:
    # 몰입 모드이고 목표 미달성 시에는 숨김
    st.info("🔒 몰입 모드: 작성된 내용은 숨겨져 있습니다.")
else:
    # [기능 추가 2] 목표 달성 여부에 따라 disabled 속성 변경
    # 목표 달성(True) -> disabled=False (수정/복사 가능)
    # 목표 미달성(False) -> disabled=True (수정 불가)
    text_area_height = 400
    if is_goal_reached:
        st.caption("🔓 잠금 해제됨: 자유롭게 복사(Ctrl+C)와 수정이 가능합니다.")
    
    st.text_area(
        label="지금까지 쓴 글",
        value=st.session_state["full_text"],
        height=text_area_height,
        disabled=not is_goal_reached  # 여기가 핵심 로직입니다

    )
