import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Streamlit 컴포넌트 쇼케이스",
    page_icon="🎛️",
    layout="wide",
)


@st.cache_data
def get_demo_data():
    categories = ["플랫폼", "분석", "콘텐츠", "고객 지원"]
    months = pd.date_range("2025-01-01", periods=12, freq="MS")
    records = []
    for month_index, month in enumerate(months):
        for category_index, category in enumerate(categories):
            records.append(
                {
                    "월": month,
                    "서비스": category,
                    "요청 수": 420 + month_index * 43 + category_index * 117
                    + (month_index * category_index * 17) % 91,
                    "완료율": 82 + (month_index * 2 + category_index * 3) % 17,
                    "평점": round(3.7 + ((month_index + category_index * 2) % 13) / 10, 1),
                }
            )
    return pd.DataFrame(records)


demo_df = get_demo_data()
months = sorted(demo_df["월"].unique())
categories = demo_df["서비스"].unique().tolist()

st.title("🎛️ Streamlit 컴포넌트 쇼케이스")
st.caption("데이터 앱에서 활용하는 입력, 시각화, 레이아웃, 피드백 요소를 한 화면에서 살펴보세요.")

with st.sidebar:
    st.header("탐색 조건")
    month_range = st.select_slider(
        "조회 기간",
        options=months,
        value=(months[-6], months[-1]),
        format_func=lambda month: month.strftime("%Y년 %m월"),
    )
    selected_categories = st.multiselect(
        "서비스 영역",
        options=categories,
        default=categories,
        help="선택한 항목이 지표와 차트에 반영됩니다.",
    )
    show_table = st.toggle("데이터 표 표시", value=True)
    with st.popover("빠른 옵션"):
        st.checkbox("완료율 90% 이상만", key="high_completion")
        st.radio("정렬 기준", ["요청 수", "완료율", "평점"], key="sort_by")

filtered_df = demo_df[
    demo_df["월"].between(month_range[0], month_range[1])
    & demo_df["서비스"].isin(selected_categories)
].copy()
if st.session_state.get("high_completion"):
    filtered_df = filtered_df[filtered_df["완료율"] >= 90]
sort_column = st.session_state.get("sort_by", "요청 수")
latest_month = pd.Timestamp(month_range[1])
latest_rows = filtered_df[filtered_df["월"] == latest_month]

st.header("요약 지표", divider="gray")
metric_columns = st.columns(4)
metric_columns[0].metric("서비스 영역", f"{filtered_df['서비스'].nunique()}개")
metric_columns[1].metric("조회 레코드", f"{len(filtered_df):,}건")
metric_columns[2].metric("월간 요청", f"{latest_rows['요청 수'].sum():,}건")
average_completion = filtered_df["완료율"].mean()
metric_columns[3].metric(
    "평균 완료율",
    f"{average_completion:.1f}%" if pd.notna(average_completion) else "—",
)

st.header("차트", divider="gray")
chart_tabs = st.tabs(["추이 · 선 차트", "비교 · 막대 차트", "누적 · 영역 차트"])
with chart_tabs[0]:
    if filtered_df.empty:
        st.info("차트를 표시할 데이터가 없습니다. 사이드바에서 조건을 조정하세요.")
    else:
        st.line_chart(filtered_df, x="월", y="요청 수", color="서비스")
with chart_tabs[1]:
    if latest_rows.empty:
        st.info("선택한 기간의 마지막 달에 표시할 데이터가 없습니다.")
    else:
        st.bar_chart(latest_rows, x="서비스", y="요청 수", color="서비스")
with chart_tabs[2]:
    if filtered_df.empty:
        st.info("차트를 표시할 데이터가 없습니다. 사이드바에서 조건을 조정하세요.")
    else:
        st.area_chart(filtered_df, x="월", y="요청 수", color="서비스")

st.header("입력 요소", divider="gray")
input_columns = st.columns(3)
with input_columns[0]:
    st.selectbox("셀렉트박스", ["요약 보기", "상세 보기", "비교 보기"])
    st.radio("라디오 버튼", ["일간", "주간", "월간"], horizontal=True)
    st.checkbox("체크박스", value=True)
with input_columns[1]:
    st.segmented_control("세그먼트 컨트롤", ["전체", "진행 중", "완료"], default="전체")
    st.number_input("목표 값", min_value=0, max_value=100, value=72, step=1)
    st.date_input("기준 날짜")
with input_columns[2]:
    st.text_input("검색어", placeholder="이름이나 키워드")
    st.color_picker("강조 색상", value="#138A72")
    st.button("새로고침 예시", icon="🔄", help="누르면 앱이 다시 실행됩니다.")

with st.expander("추가 입력과 작업 요소"):
    extra_columns = st.columns(3)
    with extra_columns[0]:
        st.text_area("메모", placeholder="내용을 입력하세요.", height=100)
        st.time_input("알림 시간")
    with extra_columns[1]:
        st.file_uploader("파일 업로드", type=["csv", "xlsx", "json"])
        st.progress(72, text="처리 진행률 예시")
    with extra_columns[2]:
        st.download_button(
            "샘플 데이터 다운로드",
            data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="sample_app_data.csv",
            mime="text/csv",
            icon="⬇️",
        )
        with st.status("데이터 준비 완료", state="complete", expanded=False):
            st.write(f"{len(filtered_df)}개 레코드를 불러왔습니다.")

st.header("폼과 알림", divider="gray")
form_column, message_column = st.columns([1, 1])
with form_column:
    with st.form("feedback_form"):
        st.subheader("폼")
        feedback_name = st.text_input("이름")
        feedback = st.text_area("의견", height=90)
        submitted = st.form_submit_button("의견 제출", type="primary")
    if submitted:
        st.success(f"{feedback_name or '사용자'}님의 의견을 접수했습니다.")
with message_column:
    st.subheader("상태 메시지")
    st.info("정보: 참고할 내용을 전달합니다.")
    st.success("성공: 작업이 정상적으로 완료되었습니다.")
    st.warning("주의: 확인이 필요한 항목을 알립니다.")
    with st.expander("오류 메시지 예시"):
        st.error("오류: 입력값이나 데이터 상태를 확인하세요.")

st.header("데이터 미리보기", divider="gray")
if show_table:
    sort_ascending = sort_column == "평점"
    st.dataframe(
        filtered_df.sort_values(sort_column, ascending=sort_ascending),
        width="stretch",
        hide_index=True,
        column_config={
            "월": st.column_config.DateColumn("월", format="YYYY년 MM월"),
            "요청 수": st.column_config.NumberColumn("요청 수", format="%d건"),
            "완료율": st.column_config.ProgressColumn(
                "완료율", min_value=0, max_value=100, format="%d%%"
            ),
            "평점": st.column_config.NumberColumn("평점", format="%.1f점"),
        },
    )
else:
    st.caption("사이드바에서 데이터 표 표시를 켜면 표가 나타납니다.")

with st.expander("마크다운과 코드"):
    st.markdown("Streamlit은 Python으로 **인터랙티브 웹 앱**을 빠르게 만들 수 있습니다.")
    st.code("st.metric('활성 사용자', '1,284', '+8.2%')", language="python")
    st.write("텍스트, 링크, 코드 블록 등도 원하는 위치에 배치할 수 있습니다.")