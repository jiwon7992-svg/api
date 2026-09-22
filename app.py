import streamlit as st
import requests
import pandas as pd
from urllib.parse import unquote

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="공공데이터 탐정",
    page_icon="🔎",
    layout="wide"
)

# -----------------------------
# API Key
# -----------------------------
try:
    API_KEY = st.secrets["DATA_GO_KR_API_KEY"]
except Exception:
    st.error("DATA_GO_KR_API_KEY가 Streamlit Secrets에 설정되지 않았습니다.")
    st.info(
        "Streamlit Cloud → Settings → Secrets에서 "
        "DATA_GO_KR_API_KEY를 추가해주세요."
    )
    st.stop()

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
    .title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #777;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .result-card {
        padding: 22px;
        border-radius: 15px;
        border: 1px solid #e5e5e5;
        margin-bottom: 15px;
        background-color: #fafafa;
    }

    .result-title {
        font-size: 21px;
        font-weight: 700;
    }

    .tag {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 8px;
        background-color: #eeeeee;
        margin-right: 5px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# API 호출 함수
# -----------------------------
@st.cache_data(ttl=300)
def search_public_data(keyword, page_no=1, num_rows=10):

    url = "https://api.data.go.kr/openapi/"

    params = {
        "serviceKey": API_KEY,
        "pageNo": page_no,
        "numOfRows": num_rows,
        "type": "json",
        "keyword": keyword
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# -----------------------------
# 데이터 구조 찾기
# -----------------------------
def find_items(data):
    """
    API 응답 구조가 조금 달라도
    items/list/item 등을 찾아서 반환합니다.
    """

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    # 흔히 사용되는 구조
    for key in ["items", "item", "data", "result", "results"]:

        if key in data:

            value = data[key]

            if isinstance(value, list):
                return value

            if isinstance(value, dict):

                for sub_key in ["items", "item", "data", "list"]:

                    if sub_key in value:

                        if isinstance(value[sub_key], list):
                            return value[sub_key]

    # 재귀 탐색
    for value in data.values():

        if isinstance(value, dict):
            result = find_items(value)

            if result:
                return result

        elif isinstance(value, list):

            if value and isinstance(value[0], dict):
                return value

    return []


# -----------------------------
# 제목 추출
# -----------------------------
def get_value(item, possible_keys):

    for key in possible_keys:

        if key in item:

            value = item[key]

            if value is not None and str(value).strip():
                return str(value)

    return "-"


# -----------------------------
# 제목
# -----------------------------
st.markdown(
    '<div class="title">🔎 공공데이터 탐정</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '궁금한 주제를 입력하면 관련 공공데이터를 찾아드립니다.'
    '</div>',
    unsafe_allow_html=True
)


# -----------------------------
# 검색창
# -----------------------------
keyword = st.text_input(
    "무엇이 궁금한가요?",
    placeholder="예: 전기차, 인구, 교통, AI, 학교, 날씨..."
)

col1, col2 = st.columns([1, 5])

with col1:
    search_button = st.button(
        "🔍 데이터 찾기",
        use_container_width=True
    )


# -----------------------------
# 검색 실행
# -----------------------------
if search_button:

    if not keyword.strip():
        st.warning("검색어를 입력해주세요.")
        st.stop()

    with st.spinner("공공데이터를 탐색하는 중입니다..."):

        try:

            result = search_public_data(
                keyword.strip(),
                page_no=1,
                num_rows=10
            )

            items = find_items(result)

            if not items:

                st.warning(
                    "검색 결과를 찾지 못했습니다. "
                    "다른 검색어를 사용해보세요."
                )

            else:

                st.success(
                    f"'{keyword}'와 관련된 데이터를 찾았습니다."
                )

                st.subheader("📊 검색 결과")

                for index, item in enumerate(items):

                    title = get_value(
                        item,
                        [
                            "title",
                            "dataTitle",
                            "datasetName",
                            "name",
                            "제목",
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

                    category = get_value(
                        item,
                        [
                            "category",
                            "classification",
                            "분류"
                        ]
                    )

                    st.markdown(
                        f"""
                        <div class="result-card">

                        <div class="result-title">
                        {index + 1}. {title}
                        </div>

                        <br>

                        <span class="tag">
                        🏛️ {organization}
                        </span>

                        <span class="tag">
                        📁 {category}
                        </span>

                        <br><br>

                        <b>설명</b><br>
                        {description}

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # -----------------------------
                # 원본 데이터
                # -----------------------------
                with st.expander("🧩 API 원본 데이터 보기"):

                    st.json(result)

        except requests.exceptions.Timeout:

            st.error(
                "공공데이터 API 응답 시간이 초과되었습니다. "
                "잠시 후 다시 시도해주세요."
            )

        except requests.exceptions.RequestException as e:

            st.error(
                "API 요청 중 오류가 발생했습니다."
            )

            st.code(str(e))

        except Exception as e:

            st.error(
                "데이터를 처리하는 중 오류가 발생했습니다."
            )

            st.code(str(e))
