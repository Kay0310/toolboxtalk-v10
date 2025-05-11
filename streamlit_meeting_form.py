import streamlit as st
import datetime
import os
from fpdf import FPDF

# 기본 세션 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.room_code = ""
    st.session_state.rooms = {}

# 회의방 코드 생성 or 입장
if not st.session_state.logged_in:
    st.title("🔐 Toolbox Talk 로그인")

    role = st.radio("역할", ["관리자", "팀원"])
    name = st.text_input("이름")

    if role == "관리자":
        st.subheader("📁 회의방 생성")
        new_room_code = st.text_input("회의 코드 입력 (예: A팀-0511)")
        team_list = st.text_area("팀원 이름 입력 (쉼표로 구분)", "김강윤,이민우,박지현")
        if st.button("회의방 생성") and new_room_code and team_list:
            st.session_state.rooms[new_room_code] = {
                "admin": name,
                "members": [n.strip() for n in team_list.split(",")],
                "attendees": [],
                "confirmations": [],
                "discussion": [],
                "tasks": [],
                "info": {},
                "additional": ""
            }
            st.session_state.room_code = new_room_code
            st.session_state.username = name
            st.session_state.role = role
            st.session_state.logged_in = True
    else:
        st.subheader("🧑‍🤝‍🧑 회의방 입장")
        room_code = st.text_input("참여할 회의 코드 입력")
        if st.button("입장") and name and room_code:
            if room_code in st.session_state.rooms:
                if name in st.session_state.rooms[room_code]["members"]:
                    st.session_state.room_code = room_code
                    st.session_state.username = name
                    st.session_state.role = role
                    st.session_state.logged_in = True
                else:
                    st.warning("등록되지 않은 팀원입니다.")
            else:
                st.error("해당 회의 코드가 존재하지 않습니다.")
    st.stop()

# 회의방 입장 후 메인
room = st.session_state.rooms[st.session_state.room_code]
user = st.session_state.username
is_admin = st.session_state.role == "관리자"

# 출석 처리
if user not in room["attendees"]:
    room["attendees"].append(user)

st.title(f"📋 Toolbox Talk 회의록 - [{st.session_state.room_code}]")

# 관리자만 회의 정보 입력 가능
st.header("1️⃣ 회의 정보")
if is_admin:
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜", datetime.date.today())
        place = st.text_input("장소", "현장 A")
    with col2:
        time = st.text_input("시간", datetime.datetime.now().strftime("%H:%M"))
        task = st.text_input("작업 내용", "고소작업")
    room["info"] = {"date": str(date), "place": place, "time": time, "task": task}
else:
    info = room.get("info", {})
    st.markdown(f"- 날짜: {info.get('date', '')}")
    st.markdown(f"- 시간: {info.get('time', '')}")
    st.markdown(f"- 장소: {info.get('place', '')}")
    st.markdown(f"- 작업내용: {info.get('task', '')}")

# 참석자 표시
st.header("2️⃣ 참석자 명단")
st.markdown("✔ 출석체크 완료된 인원:")
for name in room["attendees"]:
    st.markdown(f"- {name}")

# 논의 내용 입력
st.header("3️⃣ 논의 내용")
if is_admin:
    risk = st.text_input("위험요소", key="risk")
    measure = st.text_input("안전대책", key="measure")
    if st.button("논의 내용 추가") and risk and measure:
        room["discussion"].append((risk, measure))
else:
    for idx, (r, m) in enumerate(room["discussion"]):
        st.markdown(f"**{idx+1}. 위험요소:** {r}  \\n➡️ **안전대책:** {m}")

# 추가 논의
st.header("4️⃣ 추가 논의 사항")
if is_admin:
    room["additional"] = st.text_area("추가 논의 사항", value=room.get("additional", ""))
else:
    st.markdown(room.get("additional", ""))

# 결정사항
st.header("5️⃣ 결정사항 및 조치")
if is_admin:
    col1, col2, col3 = st.columns(3)
    person = col1.text_input("담당자", key="person")
    role = col2.text_input("업무/역할", key="t_role")
    due = col3.date_input("완료예정일", datetime.date.today())
    if st.button("조치 추가") and person and role:
        room["tasks"].append((person, role, due))
else:
    for p, r, d in room["tasks"]:
        st.markdown(f"- **{p}**: {r} (완료일: {d})")

# 회의 확인
st.header("6️⃣ 회의록 확인 및 서명")
if user not in room["confirmations"]:
    if st.button("✅ 회의 내용 확인"):
        room["confirmations"].append(user)
        st.success(f"{user}님의 확인이 저장되었습니다.")
else:
    st.success(f"{user}님은 이미 확인하셨습니다.")

if is_admin:
    st.markdown(f"### 🧾 서명 완료 현황: {len(room['confirmations'])} / {len(room['members'])}")
    for name in room["members"]:
        status = "✅" if name in room["confirmations"] else "❌"
        st.markdown(f"- {name} {status}")