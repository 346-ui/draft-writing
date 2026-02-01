import streamlit as st
import streamlit.components.v1 as components
from streamlit_local_storage import LocalStorage # [추가된 라이브러리]
import time

# 1. 페이지 설정
st.set_page_config(page_title="초고 전용 몰입 글쓰기", page_icon="✍️", layout="centered")

# [핵심] 로컬 스토리지 초기화
localS = LocalStorage()

# 세션에 목표 글자 수가 없다면, 로컬 스토리지에서 확인해서 가져옴
if "target_count_val" not in st.session_state:
    saved_target = localS.getItem("my_target_count") # 저장된 키: my_target_count
    if saved_target:
        st.session_state["target_count_val"] = int(saved_target)
    else:
        st.session_state["target_count_val"] = 1000 # 기본값

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
# (1) 글자 수 표시 설정
if "show_counter_val" not in st.session_state:
    saved_show = localS.getItem("setting_show_counter")
    # 저장된 값이 없으면 기본값 True (켜짐)
    if saved_show is None: 
        st.session_state["show_counter_val"] = True
    else:
        st.session_state["show_counter_val"] = saved_show

# (2) 몰입 모드 설정
if "hide_history_val" not in st.session_state:
    saved_hide = localS.getItem("setting_hide_history")
    # 저장된 값이 없으면 기본값 False (꺼짐)
    if saved_hide is None:
        st.session_state["hide_history_val"] = False
    else:
        st.session_state["hide_history_val"] = saved_hide
        
if "confirm_reset" not in st.session_state: st.session_state["confirm_reset"] = False


# 3. 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    # [추가된 로직 2] 목표 글자 수 변경 시 실행될 저장 함수
    def save_target_count():
        # 현재 입력된 값을 가져와서 로컬 스토리지에 저장
        current_val = st.session_state["target_count_val"]
        localS.setItem("my_target_count", current_val)
    def save_show_counter():
        localS.setItem("setting_show_counter", st.session_state["show_counter_val"])
        
    def save_hide_history():
        localS.setItem("setting_hide_history", st.session_state["hide_history_val"])

    # [수정된 입력창] key와 on_change를 사용하여 값 유지 및 자동 저장 구현
    target_count = st.number_input(
        "목표 글자 수", 
        min_value=50, 
        step=50, 
        key="target_count_val",     # 세션 상태와 연결 (값 유지)
        on_change=save_target_count, # 값이 바뀌면 즉시 저장 함수 실행
        help="목표를 달성하면 작성한 글의 수정 잠금이 해제됩니다."
    )
    st.divider()
    # [수정됨] 토글에도 key와 on_change를 붙여서 상태 저장
    show_counter = st.toggle(
        "글자 수 표시", 
        key="show_counter_val", 
        on_change=save_show_counter)
    
    hide_history = st.toggle(
        "몰입 모드 (작성한 글 숨기기)", 
        key="hide_history_val", 
        on_change=save_hide_history)
    
    st.divider()
    st.download_button("💾 다운로드 (.txt)", st.session_state["full_text"], "draft.txt")
    
    if st.button("🗑️ 초기화"): st.session_state["confirm_reset"] = not st.session_state["confirm_reset"]
    
    if st.session_state["confirm_reset"]:
        st.warning("정말 모든 내용을 삭제하시겠습니까?")
        col1, col2 = st.columns(2)
        if col1.button("✅ 예"):
            st.session_state["full_text"] = ""
            # [핵심] 초기화 시 로컬 스토리지도 비우기
            localS.deleteItem("my_draft_text")
            localS.deleteItem("my_target_count")
            localS.deleteItem("setting_show_counter")
            localS.deleteItem("setting_hide_history")
            
            st.session_state["confirm_reset"] = False
            st.session_state["target_count_val"] = 1000
            st.session_state["show_counter_val"] = True
            st.session_state["hide_history_val"] = False
            
            st.rerun()
        if col2.button("❌ 아니오"):
            st.session_state["confirm_reset"] = False
            st.rerun()

# 4. 메인 화면
st.title("✍️ 초고 전용 몰입 글쓰기")

with st.expander("ℹ️ 사용법 및 주의사항 (클릭해서 열기/닫기)", expanded=False):
    st.markdown("""
    **'멈추지 말고 계속 쓰세요!'**
    
    1.  입력창에 문장을 입력하고 **Enter**를 누르세요. 입력한 문장은 저장되며 수정할 수 없습니다.
    2.  목표 글자 수를 달성하면 글이 '언락(Unlock)' 되어 수정이 가능해집니다.
    3.  왼쪽 사이드바에서 기타 설정을 변경할 수 있습니다.

    **💾 자동 저장 기능 안내**
    - 작성된 글은 서버가 아닌 **브라우저(로컬 스토리지)에 저장**되므로, 다른 기기나 브라우저와는 연동되지 않습니다.
    - 데이터를 삭제하지 않는 한 내용은 **반영구적으로 보존**됩니다. 새로고침이나 탭 삭제에도 안전해요.  
      (삭제 예시: 쿠키 삭제, 클리너 앱, 시크릿 창 종료 등)
    - 가장 안전한 보관을 위해 작업 후에는 꼭 [다운로드] 버튼을 눌러주세요.
    """)

# 현재 글자 수 계산 및 달성 여부 확인
current_length = len(st.session_state["full_text"])
is_goal_reached = current_length >= target_count

# 프로그래스 바 및 상태 표시
if show_counter:
    progress = min(current_length / target_count, 1.0)
    if is_goal_reached: st.success(f"🎉 ({current_length}자/{target_count}자) 목표 달성!")
    else: 
        st.progress(progress)
        st.caption(f"현재: {current_length}자 / 목표: {target_count}자 ({int(progress*100)}%)")

# [핵심] 텍스트 입력 및 저장 처리 함수

st.subheader("📝 작성된 내용")
if hide_history and not is_goal_reached:
    st.info("🔒 몰입 모드 실행 중...")
else:
    st.text_area("히스토리", st.session_state["full_text"], height=400, disabled=not is_goal_reached, label_visibility="collapsed")
    if is_goal_reached:
        st.caption("🔓 잠금 해제됨: 자유롭게 수정 가능합니다.")
        
def submit_text():
    input_text = st.session_state.widget_input
    if input_text:
        # 1. 세션에 추가
        st.session_state["full_text"] += input_text + "\n"
        # 2. 로컬 스토리지에 영구 저장 (Key: "my_draft_text")
        localS.setItem("my_draft_text", st.session_state["full_text"])
        
        st.session_state.widget_input = ""

st.text_input("내용 입력 👇", key="widget_input", on_change=submit_text, placeholder="생각나는 대로 적고 엔터를 누르세요.")


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





















