import streamlit as st
import requests
import pandas as pd

# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="공공데이터 탐정",
    page_icon="🔎",
    layout="wide"
)

# =========================================================
# Secrets
# =========================================================

try:
    API_KEY = st.secrets["DATA_GO_KR_API_KEY"]
    API_URL = st.secrets["DATA_GO_KR_API_URL"]
except KeyError:
    st.error("Streamlit Secrets 설정이 필요합니다.")
    st.code("""
DATA_GO_KR_API_KEY = "공공데이터포털_인증키"
DATA_GO_KR_API_URL = "실제_API_요청_URL"
    """)
    st.stop()

# =========================================================
# 화면 디자인
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    font-size: 18px;
    color: #777;
    margin-bottom: 35px;
}

.card {
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e5e5;
    margin-bottom: 16px;
}

.card-title {
    font-size: 22px;
    font-weight: 700;
}

.small {
    color: #777;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 제목
# =========================================================

st.markdown(
    '<div class="main-title">🔎 공공데이터 탐정</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '공공데이터를 검색하고, 숫자 속에 숨은 정보를 찾아보세요.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# 검색 영역
# =========================================================

keyword = st.text_input(
    "🔍 검색어",
    placeholder="예: 인구, 청년, 고용, 물가, 출생률"
)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.button(
        "🔎 데이터 탐색",
        use_container_width=True
    )

with col2:
    rows = st.selectbox(
        "결과 수",
        [5, 10, 20],
        index=1
    )

with col3:
    st.write("")
    st.write("")
    clear = st.button(
        "초기화",
        use_container_width=True
    )

# =========================================================
# API 요청 함수
# =========================================================

@st.cache_data(ttl=300)
def request_api(keyword, rows):

    params = {
        "serviceKey": API_KEY,
        "keyword": keyword,
        "pageNo": 1,
        "numOfRows": rows,
        "type": "json"
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# API 결과에서 리스트 찾기
# =========================================================

def find_list(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        # 일반적인 API 구조
        for key in [
            "items",
            "item",
            "data",
            "results",
            "result",
            "list"
        ]:

            if key in data:

                value = data[key]

                if isinstance(value, list):
                    return value

                if isinstance(value, dict):

                    result = find_list(value)

                    if result:
                        return result

        # 재귀 탐색
        for value in data.values():

            if isinstance(value, (dict, list)):

                result = find_list(value)

                if result:
                    return result

    return []


# =========================================================
# 값 찾기
# =========================================================

def get_value(item, keys):

    for key in keys:

        if key in item:

            value = item[key]

            if value is not None:
                value = str(value).strip()

                if value:
                    return value

    return "-"


# =========================================================
# 검색
# =========================================================

if search:

    if not keyword.strip():

        st.warning("검색어를 입력해주세요.")

    else:

        with st.spinner("공공데이터를 탐색하고 있습니다..."):

            try:

                data = request_api(
                    keyword.strip(),
                    rows
                )

                items = find_list(data)

                if not items:

                    st.warning(
                        "검색 결과가 없습니다."
                    )

                else:

                    st.success(
                        f"'{keyword}' 검색 결과 "
                        f"{len(items)}건"
                    )

                    # -----------------------------------------
                    # 결과 데이터 정리
                    # -----------------------------------------

                    result_rows = []

                    for item in items:

                        title = get_value(
                            item,
                            [
                                "title",
                                "dataTitle",
                                "datasetName",
                                "name",
                                "dataNm",
                                "지표명",
                                "데이터명"
                            ]
                        )

                        organization = get_value(
                            item,
                            [
                                "organization",
                                "orgName",
                                "provider",
                                "기관명",
                                "제공기관"
                            ]
                        )

                        description = get_value(
                            item,
                            [
                                "description",
                                "dataDescription",
                                "desc",
                                "설명"
                            ]
                        )

                        result_rows.append({
                            "데이터": title,
                            "제공기관": organization,
                            "설명": description
                        })

                    df = pd.DataFrame(result_rows)

                    # -----------------------------------------
                    # 표
                    # -----------------------------------------

                    st.subheader("📊 발견한 데이터")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # -----------------------------------------
                    # 카드
                    # -----------------------------------------

                    st.subheader("🔍 자세히 보기")

                    for i, item in enumerate(items):

                        title = get_value(
                            item,
                            [
                                "title",
                                "dataTitle",
                                "datasetName",
                                "name",
                                "dataNm",
                                "지표명",
                                "데이터명"
                            ]
                        )

                        organization = get_value(
                            item,
                            [
                                "organization",
                                "orgName",
                                "provider",
                                "기관명",
                                "제공기관"
                            ]
                        )

                        description = get_value(
                            item,
                            [
                                "description",
                                "dataDescription",
                                "desc",
                                "설명"
                            ]
                        )

                        with st.container(border=True):

                            st.markdown(
                                f"### {i + 1}. {title}"
                            )

                            st.write(
                                f"🏛️ **제공기관:** "
                                f"{organization}"
                            )

                            st.write(
                                f"📝 **설명:** "
                                f"{description}"
                            )

                    # -----------------------------------------
                    # 다운로드
                    # -----------------------------------------

                    csv = df.to_csv(
                        index=False
                    ).encode("utf-8-sig")

                    st.download_button(
                        "⬇️ 검색 결과 CSV 다운로드",
                        csv,
                        "public_data_results.csv",
                        "text/csv",
                        use_container_width=True
                    )

                    # -----------------------------------------
                    # 원본 API
                    # -----------------------------------------

                    with st.expander(
                        "🧩 개발자용: API 원본 응답"
                    ):

                        st.json(data)

            except requests.exceptions.Timeout:

                st.error(
                    "API 서버 응답 시간이 초과되었습니다."
                )

            except requests.exceptions.HTTPError as e:

                st.error(
                    "API 요청에 실패했습니다."
                )

                st.code(str(e))

            except requests.exceptions.RequestException as e:

                st.error(
                    "네트워크 오류가 발생했습니다."
                )

                st.code(str(e))

            except Exception as e:

                st.error(
                    "데이터를 처리하는 중 오류가 발생했습니다."
                )

                st.code(str(e))
