import streamlit as st
import pandas as pd
from src.text_searcher.services.search_service import SearchService


st.set_page_config(
    page_title="Поиск новостей",
    page_icon="📊",
)
search_service = SearchService()
search_service.build_faiss_index()


st.title('Найти похожую новость 📰')


@st.cache_data
def similar_data(query):
    news = search_service.retrieve(query)
    df = pd.DataFrame(news, columns=['summary', 'url'])
    return df


user_query = st.text_input('Введите промпт')

if st.button('Найти', type='primary') or user_query:
    if user_query.strip():
        with st.spinner('Поиск...', show_time=True):
            df = similar_data(user_query)
            st.table(df)
        st.success('Готово')


