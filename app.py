import streamlit as st
import requests
import pandas as pd

# ---------------------------------------
# 페이지 설정
# ---------------------------------------
st.set_page_config(
    page_title="공공데이터 탐정",
    page_icon="🔎",
    layout="wide"
)

# ---------------------------------------
# API 설정
# ---------------------------------------
API_KEY = st.secrets["DATA_GO_KR_API_KEY"]

API_URL = (
    "https://api.odcloud.kr/api"
    "/GetSearchDataList/v1/searchData"
)

# ---------------------------------------
# 화면
# ---------------------------------------
st.title("🔎 공공데이터 탐정")
st.write(
    "공공데이터포털의 다양한 데이터를 "
    "키워드로 찾아보는 탐색 서비스입니다."
)

st.divider()

keyword = st.text_input(
    "🔍 검색어",
    placeholder="예: 인공지능, 교통, 환경, 교육"
)

col1, col2 = st.columns([1, 1])

with col1:
    data_types = st.multiselect(
        "데이터 유형",
        ["FILE", "API", "STD"],
        default=["FILE", "API", "STD"],
        help="FILE: 파일데이터 / API: 오픈API / STD: 표준데이터"
    )

with col2:
    result_size = st.slider(
        "검색 결과 수",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )

search = st.button(
    "🔎 데이터 탐색하기",
    type="primary",
    use_container_width=True
)

# ---------------------------------------
# 검색
# ---------------------------------------
if search:

    if not keyword.strip():
        st.warning("검색어를 입력해주세요.")
        st.stop()

    if not data_types:
        st.warning("최소 하나의 데이터 유형을 선택해주세요.")
        st.stop()

    request_body = {
        "page": 1,
        "size": result_size,
        "keyword": keyword.strip(),
        "dataType": data_types
    }

    headers = {
        "Content-Type": "application/json"
    }

    with st.spinner("공공데이터를 탐색하고 있습니다..."):

        try:
            response = requests.post(
                API_URL,
                params={
                    "serviceKey": API_KEY
                },
                headers=headers,
                json=request_body,
                timeout=20
            )

            response.raise_for_status()

            result = response.json()

        except requests.exceptions.Timeout:
            st.error(
                "API 서버의 응답 시간이 초과되었습니다. "
                "잠시 후 다시 시도해주세요."
            )
            st.stop()

        except requests.exceptions.HTTPError as e:
            st.error(
                f"API 요청에 실패했습니다. "
                f"(HTTP {response.status_code})"
            )

            with st.expander("오류 응답 확인"):
                st.code(response.text)

            st.stop()

        except requests.exceptions.RequestException as e:
            st.error(f"API 요청 중 오류가 발생했습니다: {e}")
            st.stop()

        except ValueError:
            st.error("API에서 올바른 JSON 데이터를 받지 못했습니다.")

            with st.expander("서버 응답 확인"):
                st.code(response.text)

            st.stop()

    # ---------------------------------------
    # 응답 분석
    # ---------------------------------------
    if result.get("statusCode") != 200:
        st.error("API에서 정상적인 결과를 반환하지 않았습니다.")

        with st.expander("API 응답 확인"):
            st.json(result)

        st.stop()

    results = result.get("result", [])

    if not results:
        st.info(
            f"'{keyword}'에 대한 검색 결과가 없습니다."
        )
        st.stop()

    # API 응답의 result 안에서 실제 데이터 찾기
    result_info = results[0]

    total_count = result_info.get("sum", 0)
    data_count = result_info.get("dataCount", 0)
    data_list = result_info.get("data", [])

    # ---------------------------------------
    # 검색 결과 요약
    # ---------------------------------------
    st.success(
        f"'{keyword}' 검색이 완료되었습니다."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "전체 검색 결과",
            f"{total_count:,}개"
        )

    with c2:
        st.metric(
            "이번 검색 결과",
            f"{data_count:,}개"
        )

    with c3:
        st.metric(
            "검색어",
            keyword
        )

    st.divider()

    # ---------------------------------------
    # 데이터가 있는 경우
    # ---------------------------------------
    if data_list:

        # 표에 표시할 데이터 구성
        rows = []

        for item in data_list:

            rows.append({
                "데이터명": item.get("dataName", ""),
                "제공기관": item.get("organization", ""),
                "데이터 유형": item.get("dataType", ""),
                "서비스 유형": item.get("dataProvisionType", ""),
                "분류": (
                    f"{item.get('firstBrmName', '')} "
                    f"/ {item.get('secondBrmName', '')}"
                ),
                "수정일": item.get("updateDate", ""),
                "설명": item.get("dataDescription", "")
            })

        df = pd.DataFrame(rows)

        st.subheader("📊 검색 결과")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "설명": st.column_config.TextColumn(
                    width="large"
                )
            }
        )

        # ---------------------------------------
        # 개별 데이터 상세 보기
        # ---------------------------------------
        st.subheader("📁 데이터 상세 보기")

        for index, item in enumerate(data_list):

            data_name = item.get(
                "dataName",
                "이름 없는 데이터"
            )

            with st.expander(
                f"{index + 1}. {data_name}"
            ):

                description = item.get(
                    "dataDescription",
                    "설명이 없습니다."
                )

                st.write(description)

                info1, info2 = st.columns(2)

                with info1:
                    st.write(
                        f"**제공기관:** "
                        f"{item.get('organization', '-')}"
                    )

                    st.write(
                        f"**데이터 유형:** "
                        f"{item.get('dataType', '-')}"
                    )

                    st.write(
                        f"**서비스 유형:** "
                        f"{item.get('dataProvisionType', '-')}"
                    )

                with info2:
                    st.write(
                        f"**수정일:** "
                        f"{item.get('updateDate', '-')}"
                    )

                    st.write(
                        f"**분류:** "
                        f"{item.get('firstBrmName', '-')} / "
                        f"{item.get('secondBrmName', '-')}"
                    )

                    st.write(
                        f"**이용허락범위:** "
                        f"{item.get('useScopeCode', '-')}"
                    )

                # 키워드
                keywords = item.get("keywords", [])

                if keywords:
                    st.write(
                        "**키워드:** "
                        + ", ".join(keywords)
                    )

                # 상세 페이지
                detail_url = item.get(
                    "detailPageUrl"
                )

                if detail_url:
                    st.link_button(
                        "🔗 데이터 상세 페이지",
                        detail_url
                    )

    else:
        st.info("검색 결과 데이터가 없습니다.")

    # ---------------------------------------
    # CSV 다운로드
    # ---------------------------------------
    if data_list:

        csv = df.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            "📥 검색 결과 CSV 다운로드",
            data=csv,
            file_name=f"공공데이터_{keyword}.csv",
            mime="text/csv"
        )

    # ---------------------------------------
    # API 원본 응답
    # ---------------------------------------
    with st.expander("🔧 API 원본 응답 보기"):
        st.json(result)

# ---------------------------------------
# 하단 설명
# ---------------------------------------
st.divider()

st.caption(
    "공공데이터포털 검색 서비스 Open API를 활용한 "
    "공공데이터 탐색 프로젝트"
)
