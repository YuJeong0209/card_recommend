import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import pandas as pd
from elastic_api import search_index, search_index_with_date_range

st.title("카드 정보 조회") 
st.markdown(
    """     <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}     </style>
    """, unsafe_allow_html=True )

st.sidebar.header("조회하고 싶은 카드를 입력하시오")
index_name = st.sidebar.text_input('인덱스명', value="card_info").lower()

field_name = st.sidebar.text_input('필드명', value="card_name")

match_name = st.sidebar.text_input('조회하려는 내용', value="카드의정석")
clicked1 = st.sidebar.button("해당 정보 확인")



if(clicked1 == True):
    result = search_index(index_name, field_name, match_name)
    hits = result.to_dict()["hits"]["hits"]     
    if hits:
        for hit in hits:
            card_info = hit["_source"]
            st.subheader(card_info["card_name"])
            st.write(f"연회비 (국내): {card_info['domestic_year_cost']}원")
            st.write(f"연회비 (해외): {card_info['abroad_year_cost']}원")
            st.write(f"전월 실적 조건: {card_info['previous_month_performance']}만원 이상")
            st.write(f"[카드 상세 링크]({card_info['card_link']})")

            st.markdown("### 혜택 및 조건")
            for category in card_info["category"]:
                st.write(f"**카테고리**: {category['class']}")
                st.write(f"**혜택**: {category['benefit']}")
                
                # HTML을 Markdown으로 처리
                st.markdown(category["condition"], unsafe_allow_html=True)

                st.write("---")
    else:
        st.write("조회된 카드 정보가 없습니다.")    



