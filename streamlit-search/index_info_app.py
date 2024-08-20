import streamlit as st
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

st.title("CARD CAPYBARA") 
st.markdown(
    """     
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}     
    </style>
    """, unsafe_allow_html=True
)

client_name = Elasticsearch('http://localhost:9200') 
st.sidebar.header("조회하고 싶은 카드명을 입력하세요")
match_name = st.sidebar.text_input('조회하려는 내용', value="우리")
radio_name = st.sidebar.radio(label='카드 종류', options=['신용', '체크'])

index_name = "card_info"
field_name = "card_name"
# 각 정보를 출력하는 버튼들
clicked_image = st.sidebar.button("카드 이미지 출력하기")
clicked_domestic = st.sidebar.button("연회비(국내) 조회하기")
clicked_abroad = st.sidebar.button("연회비(해외) 조회하기")
clicked_performance = st.sidebar.button("전월 실적 조건 조회하기")
clicked_link = st.sidebar.button("카드 상세 링크 조회하기")
clicked_benefit = st.sidebar.button("Benefit 조회하기")


#benefit 카드 비교
st.sidebar.header("받고 싶은 혜택 키워드를 입력하세요")
search_name = st.sidebar.text_input('내용', value='대중교통')
card_compare = st.sidebar.button("비슷한 benefit 카드 비교하기")

# 카드 정보 검색 함수
def get_card_info():
    # 쿼리 정의
    if radio_name == '신용':
        query = {
            "bool": {
                "must": [
                    {"match": {field_name: match_name}},
                    {"bool": {
                        "must_not": [
                            {"wildcard": {field_name: "*체크*"}},
                            {"wildcard": {field_name: "*check*"}},
                            {"wildcard": {field_name: "*체크카드*"}}
                        ]
                    }}
                ]
            }
        }
    else:
        query = {
            "bool": {
                "must": [
                    {"match": {field_name: match_name}},
                    {"bool": {
                        "should": [
                            {"wildcard": {field_name: "*체크*"}},
                            {"wildcard": {field_name: "*check*"}},
                            {"wildcard": {field_name: "*체크카드*"}}
                        ]
                    }}
                ]
            }
        }

    s = Search(using=client_name, index=index_name).query(query)
    response = s.execute()
    hits = response.hits.hits
    if hits:
        return hits[0]["_source"]
    else:
        st.write("해당하는 내용을 찾을 수 없습니다.")
        return None

# 이미지 URL 생성 함수
def generate_image_url(card_id):
    base_url = "https://woori-fisa-bucket.s3.ap-northeast-2.amazonaws.com/index_img/"
    image_filename = f"bcc_{str(card_id).zfill(3)}.png"
    return base_url + image_filename

# 버튼 클릭 시 해당 정보를 출력
if clicked_domestic:
    card_info = get_card_info()
    if card_info:
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.write(f"연회비 (국내): {card_info.domestic_year_cost}원")

if clicked_abroad:
    card_info = get_card_info()
    if card_info:
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.write(f"연회비 (해외): {card_info.abroad_year_cost}원")

if clicked_performance:
    card_info = get_card_info()
    if card_info:
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.write(f"전월 실적 조건: {card_info.previous_month_performance}만원 이상")

if clicked_link:
    card_info = get_card_info()
    if card_info:
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.write(f"[카드 상세 링크]({card_info.card_link})")

if clicked_benefit:
    card_info = get_card_info()
    if card_info:
        benefit_list = []
        for category_entry in card_info.category:
            benefit = category_entry.benefit
            if benefit:
                benefit_list.append(benefit)
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.write("Benefit Details:")
        for benefit in benefit_list:
            
            st.write(benefit)

# 버튼 클릭 시 카드 이미지 출력
if clicked_image:
    card_info = get_card_info()
    if card_info:
        card_id = card_info.id
        image_url = generate_image_url(card_id)
        st.write(f"**카드명**: **{card_info.card_name}**")
        st.image(image_url, caption=f"Card ID: {card_id}", width=250)

# 카드 비교하기, benefit안에 search_name이 있는 경우
if card_compare:
    s = Search(using=client_name, index="card_info") \
        .query("match", **{"category.class": search_name})

    response = s[:2].execute()
    hits = response.hits.hits

    if len(hits) >= 2:
        col1, col2 = st.columns(2)

        with col1:
            card_id = hits[0]["_source"].id
            image_url = generate_image_url(card_id)
            st.image(image_url, caption=f"Card ID: {card_id}", width=250)
            st.subheader(hits[0]["_source"].card_name)
            st.write(f"Benefit: {hits[0]['_source'].category[0].benefit}")
            st.write(f"연회비 (국내): {hits[0]['_source'].domestic_year_cost}")
            st.write(f"연회비 (해외): {hits[0]['_source'].abroad_year_cost}")
            st.write(f"전월 실적 조건: {hits[0]['_source'].previous_month_performance}")
            st.write(f"[카드 상세 링크]({hits[0]['_source'].card_link})")
        
        with col2:
            card_id = hits[1]["_source"].id
            image_url = generate_image_url(card_id)
            st.image(image_url, caption=f"Card ID: {card_id}", width=250)
            st.subheader(hits[1]["_source"].card_name)
            st.write(f"Benefit: {hits[1]['_source'].category[0].benefit}")
            st.write(f"연회비 (국내): {hits[1]['_source'].domestic_year_cost}")
            st.write(f"연회비 (해외): {hits[1]['_source'].abroad_year_cost}")
            st.write(f"전월 실적 조건: {hits[1]['_source'].previous_month_performance}")
            st.write(f"[카드 상세 링크]({hits[1]['_source'].card_link})")
    else:
        st.write("검색 결과가 충분하지 않습니다.")