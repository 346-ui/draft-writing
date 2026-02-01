import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage # [추가된 라이브러리]
import time

# 1. 페이지 설정
st.set_page_config(page_title="초고 전용 몰입 글쓰기", page_icon="✍️", layout="centered")

# [핵심] 로컬 스토리지 초기화
localS = LocalStorage()

# 2. 세션 상태 초기화 및 데이터 복구 로직
if "full_text" not in st.session_state:
    # (1) 로컬 스토리지에서 저장된 글이 있는지 확인
    saved_text = localS.getItem("my_draft_text")
    
    if saved_text:
        st.session_state["full_text"] = saved_text
        # 복구되었음을 알리는 작은 알림 (선택사항)
        # st.toast("🔄 이전에 쓰던 글을 복구했습니다!", icon="📂")
    else:
        st.session_state["full_text"] = ""

if "confirm_reset" not in st.session_state: st.session_state["confirm_reset"] = False


# 3. 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    target_count = st.number_input("목표 글자 수", min_value=50, value=1000, step=50, help="목표를 달성하면 작성한 글의 수정 잠금이 해제됩니다.")
    st.divider()
    show_counter = st.toggle("글자 수 표시", value=True)
    hide_history = st.toggle("몰입 모드 (작성한 글 숨기기)", value=False)
    st.divider()
    st.download_button("💾 다운로드 (.txt)", st.session_state["full_text"], "draft.txt")
    
    if st.button("🗑️ 초기화"): st.session_state["confirm_reset"] = True
    
    if st.session_state["confirm_reset"]:
        st.warning("정말 모든 내용을 삭제하시겠습니까?")
        col1, col2 = st.columns(2)
        if col1.button("✅ 예"):
            st.session_state["full_text"] = ""
            # [핵심] 초기화 시 로컬 스토리지도 비우기
            localS.deleteItem("my_draft_text") 
            st.session_state["confirm_reset"] = False
            st.rerun()
        if col2.button("❌ 아니오"):
            st.session_state["confirm_reset"] = False
            st.rerun()

# 4. 메인 화면
st.title("✍️ 초고 전용 몰입 글쓰기")

with st.expander("ℹ️ 사용법 및 주의사항 (클릭해서 열기/닫기)", expanded=False):
    st.markdown("""
    **'멈추지 말고 계속 쓰세요!'**
    
    1.  **입력창**에 문장을 입력하고 **Enter**를 누르세요.
    2.  입력한 문장은 저장되며 수정할 수 없습니다.
    3.  **목표 글자 수를 달성하면** 글이 '언락(Unlock)' 되어 수정이 가능해집니다. (목표 글자 수는 왼쪽 사이드바에서 설정 가능합니다)

    **💾 자동 저장 기능 안내**
작성된 글은 서버가 아닌 **브라우저(로컬 스토리지)에 저장**되므로, **다른 기기나 브라우저와는 연동되지 않습니다.**
데이터를 직접 삭제(시크릿 창 종료, 쿠키 삭제, 클리너 앱 등)하지 않는 한 내용은 **반영구적으로 보존**됩니다.
가장 안전한 보관을 위해 작업 후에는 꼭 **[다운로드]** 버튼을 눌러주세요.
    """)

# 현재 글자 수 계산 및 달성 여부 확인
current_length = len(st.session_state["full_text"])
is_goal_reached = current_length >= target_count

# 프로그래스 바 및 상태 표시
if show_counter:
    progress = min(current_length / target_count, 1.0)
    if is_goal_reached: st.success(f"🎉 ({current_length}자) 목표 달성!")
    else: 
        st.progress(progress)
        st.caption(f"현재: {current_length}자 / 목표: {target_count}자 ({int(progress*100)}%)")

# [핵심] 텍스트 입력 및 저장 처리 함수
def submit_text():
    input_text = st.session_state.widget_input
    if input_text:
        # 1. 세션에 추가
        st.session_state["full_text"] += input_text + "\n"
        # 2. 로컬 스토리지에 영구 저장 (Key: "my_draft_text")
        localS.setItem("my_draft_text", st.session_state["full_text"])
        
        st.session_state.widget_input = ""

st.text_input("내용 입력 👇", key="widget_input", on_change=submit_text, placeholder="생각나는 대로 적고 엔터를 누르세요.")

st.subheader("📝 작성된 내용")

if hide_history and not is_goal_reached:
    st.info("🔒 몰입 모드 실행 중...")
else:
    st.text_area("히스토리", st.session_state["full_text"], height=400, disabled=not is_goal_reached, label_visibility="collapsed")
    if is_goal_reached:
        st.caption("🔓 잠금 해제됨: 자유롭게 수정 가능합니다.")

    # 스크롤 유지 기능 (MutationObserver)
    js_observer = f"""
    <script>
        function adjustScroll() {{
            var textArea = window.parent.document.querySelector('textarea');
            if (!textArea) return;
            // isAtBottom: 사용자가 마지막으로 맨 아래를 보고 있었는지 여부 (true/false)
            var isAtBottom = sessionStorage.getItem("textAreaIsAtBottom") === 'true';
            var savedPos = sessionStorage.getItem("textAreaScrollPosition");

            if (isAtBottom) {{
                textArea.scrollTop = textArea.scrollHeight;
            }} else if (savedPos) {{
                textArea.scrollTop = savedPos;
            }}
           // 이벤트 리스너 재등록 (중복 방지 처리) 
            textArea.onscroll = function() {{
                sessionStorage.setItem("textAreaScrollPosition", textArea.scrollTop);
                var atBottom = (textArea.scrollHeight - textArea.scrollTop - textArea.clientHeight) < 10;
                sessionStorage.setItem("textAreaIsAtBottom", atBottom);
            }};
        }}
        // 2. MutationObserver: 화면에 textarea가 등장하는지 감시
        var observer = new MutationObserver(function(mutations) {{
            var textArea = window.parent.document.querySelector('textarea');
            if (textArea) {{
                adjustScroll();
                observer.disconnect();
            }}
        }});
        // 3. 감시 시작 (부모 문서의 body를 감시)
        observer.observe(window.parent.document.body, {{ childList: true, subtree: true }});
        // 혹시 이미 로딩되어 있을 경우를 대비해 한 번 즉시 실행
        adjustScroll();
    </script>
    <div style="display:none;">{time.time()}</div>
    """
    components.html(js_observer, height=0)


