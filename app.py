import streamlit as st
import requests
import pandas as pd


# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="공공데이터 탐정",
    page_icon="🔎",
    layout="wide"
)


# ==========================================
# API 설정
# ==========================================
API_KEY = st.secrets["DATA_GO_KR_API_KEY"]

API_URL = (
    "https://api.odcloud.kr/api"
    "/GetSearchDataList/v1/searchData"
)


# ==========================================
# 제목
# ==========================================
st.title("🔎 공공데이터 탐정")

st.write(
    "공공데이터포털의 다양한 데이터를 "
    "키워드로 찾아보고 정보를 확인할 수 있습니다."
)

st.divider()


# ==========================================
# 검색 설정
# ==========================================
keyword = st.text_input(
    "🔍 검색어",
    placeholder="예: 인공지능, 교통, 환경, 교육"
)


col1, col2 = st.columns(2)


with col1:
    data_types = st.multiselect(
        "데이터 유형",
        ["FILE", "API", "STD"],
        default=["FILE", "API", "STD"],
        help=(
            "FILE: 파일데이터\n"
            "API: 오픈API\n"
            "STD: 표준데이터"
        )
    )


with col2:
    result_size = st.slider(
        "검색 결과 수",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )


search_button = st.button(
    "🔎 데이터 탐색하기",
    type="primary",
    use_container_width=True
)


# ==========================================
# 검색 실행
# ==========================================
if search_button:

    # 검색어 확인
    if not keyword.strip():
        st.warning("검색어를 입력해주세요.")
        st.stop()

    # 데이터 유형 확인
    if not data_types:
        st.warning("최소 하나의 데이터 유형을 선택해주세요.")
        st.stop()


    # ======================================
    # API 요청 데이터
    # ======================================
    request_body = {
        "page": 1,
        "size": result_size,
        "keyword": keyword.strip(),
        "dataType": data_types
    }


    headers = {
        "Content-Type": "application/json"
    }


    # ======================================
    # API 호출
    # ======================================
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


            # HTTP 오류 확인
            response.raise_for_status()


            # JSON 변환
            result = response.json()


        except requests.exceptions.Timeout:

            st.error(
                "API 서버의 응답 시간이 초과되었습니다. "
                "잠시 후 다시 시도해주세요."
            )

            st.stop()


        except requests.exceptions.HTTPError:

            st.error(
                f"API 요청에 실패했습니다. "
                f"(HTTP {response.status_code})"
            )

            with st.expander("🔧 서버 응답 확인"):

                st.code(
                    response.text
                )

            st.stop()


        except requests.exceptions.RequestException as e:

            st.error(
                f"API 요청 중 오류가 발생했습니다.\n\n{e}"
            )

            st.stop()


        except ValueError:

            st.error(
                "API에서 올바른 JSON 데이터를 "
                "받지 못했습니다."
            )

            with st.expander("🔧 서버 응답 확인"):

                st.code(
                    response.text
                )

            st.stop()


    # ======================================
    # API 상태 확인
    # ======================================
    if result.get("statusCode") != 200:

        st.error(
            "API에서 정상적인 결과를 반환하지 않았습니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # ======================================
    # result 가져오기
    # ======================================
    results = result.get("result")


    # result가 없는 경우
    if results is None:

        st.error(
            "API 응답에 result 데이터가 없습니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # result가 리스트가 아닌 경우
    if not isinstance(results, list):

        st.error(
            "API 응답의 result 형식이 예상과 다릅니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # ======================================
    # 검색 결과가 없는 경우
    # ======================================
    if len(results) == 0:

        st.info(
            f"'{keyword}'에 대한 검색 결과가 없습니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # ======================================
    # 첫 번째 결과 묶음
    # ======================================
    result_info = results[0]


    # 결과가 dictionary인지 확인
    if not isinstance(result_info, dict):

        st.error(
            "API 결과의 데이터 형식이 예상과 다릅니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # ======================================
    # 검색 결과 정보
    # ======================================
    total_count = result_info.get(
        "sum",
        0
    )


    data_count = result_info.get(
        "dataCount",
        0
    )


    data_list = result_info.get(
        "data",
        []
    )


    # data가 리스트가 아닌 경우
    if not isinstance(data_list, list):

        data_list = []


    # ======================================
    # 검색 완료
    # ======================================
    st.success(
        f"'{keyword}' 검색이 완료되었습니다."
    )


    # ======================================
    # 검색 결과 요약
    # ======================================
    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "전체 검색 결과",
            f"{total_count:,}개"
        )


    with col2:

        st.metric(
            "이번 검색 결과",
            f"{data_count:,}개"
        )


    with col3:

        st.metric(
            "검색어",
            keyword
        )


    st.divider()


    # ======================================
    # 실제 데이터가 없는 경우
    # ======================================
    if not data_list:

        st.info(
            "검색 결과는 확인되었지만 "
            "표시할 데이터가 없습니다."
        )

        with st.expander("🔧 API 원본 응답 확인"):

            st.json(result)

        st.stop()


    # ======================================
    # 데이터 표 만들기
    # ======================================
    rows = []


    for item in data_list:

        if not isinstance(item, dict):
            continue


        rows.append({

            "데이터명":
                item.get(
                    "dataName",
                    ""
                ),

            "제공기관":
                item.get(
                    "organization",
                    ""
                ),

            "데이터 유형":
                item.get(
                    "dataType",
                    ""
                ),

            "서비스 유형":
                item.get(
                    "dataProvisionType",
                    ""
                ),

            "분류":
                (
                    f"{item.get('firstBrmName', '')}"
                    f" / "
                    f"{item.get('secondBrmName', '')}"
                ),

            "수정일":
                item.get(
                    "updateDate",
                    ""
                ),

            "설명":
                item.get(
                    "dataDescription",
                    ""
                )
        })


    # DataFrame 생성
    df = pd.DataFrame(rows)


    # ======================================
    # 검색 결과 표시
    # ======================================
    st.subheader("📊 검색 결과")


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # ======================================
    # CSV 다운로드
    # ======================================
    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )


    st.download_button(
        label="📥 검색 결과 CSV 다운로드",
        data=csv,
        file_name=f"공공데이터_{keyword}.csv",
        mime="text/csv",
        use_container_width=True
    )


    st.divider()


    # ======================================
    # 상세 데이터
    # ======================================
    st.subheader("📁 데이터 상세 보기")


    for index, item in enumerate(data_list):

        if not isinstance(item, dict):
            continue


        data_name = item.get(
            "dataName",
            "이름 없는 데이터"
        )


        with st.expander(
            f"{index + 1}. {data_name}"
        ):

            # 설명
            description = item.get(
                "dataDescription",
                "설명이 없습니다."
            )


            st.write(description)


            st.divider()


            info1, info2 = st.columns(2)


            # ------------------------------
            # 왼쪽 정보
            # ------------------------------
            with info1:

                st.write(
                    "**제공기관:** "
                    + str(
                        item.get(
                            "organization",
                            "-"
                        )
                    )
                )


                st.write(
                    "**데이터 유형:** "
                    + str(
                        item.get(
                            "dataType",
                            "-"
                        )
                    )
                )


                st.write(
                    "**서비스 유형:** "
                    + str(
                        item.get(
                            "dataProvisionType",
                            "-"
                        )
                    )
                )


            # ------------------------------
            # 오른쪽 정보
            # ------------------------------
            with info2:

                st.write(
                    "**수정일:** "
                    + str(
                        item.get(
                            "updateDate",
                            "-"
                        )
                    )
                )


                st.write(
                    "**분류:** "
                    + str(
                        item.get(
                            "firstBrmName",
                            "-"
                        )
                    )
                    + " / "
                    + str(
                        item.get(
                            "secondBrmName",
                            "-"
                        )
                    )
                )


                st.write(
                    "**이용허락범위:** "
                    + str(
                        item.get(
                            "useScopeCode",
                            "-"
                        )
                    )
                )


            # ------------------------------
            # 키워드
            # ------------------------------
            keywords = item.get(
                "keywords",
                []
            )


            if keywords:

                if isinstance(keywords, list):

                    st.write(
                        "**키워드:** "
                        + ", ".join(
                            map(str, keywords)
                        )
                    )

                else:

                    st.write(
                        "**키워드:** "
                        + str(keywords)
                    )


            # ------------------------------
            # 상세 페이지
            # ------------------------------
            detail_url = item.get(
                "detailPageUrl"
            )


            if detail_url:

                st.link_button(
                    "🔗 데이터 상세 페이지",
                    detail_url
                )


    # ======================================
    # 원본 API 응답
    # ======================================
    st.divider()


    with st.expander(
        "🔧 API 원본 응답 보기"
    ):

        st.json(result)


# ==========================================
# 하단 안내
# ==========================================
st.divider()


st.caption(
    "공공데이터포털 검색 서비스 Open API를 "
    "활용한 공공데이터 탐색 프로젝트"
)
