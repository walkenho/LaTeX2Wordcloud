import streamlit as st
from nltk.corpus import stopwords

from src.latex2wordcloud.LateX2WordCloud import (
    convert_text_to_clean_tokens,
    create_wordcounts,
    create_wordcounts_bar_chart,
)

st.title("LaTeX2Wordcloud")
st.markdown("Analyze your text data to find the most common words.")

uploaded_file = st.file_uploader("Upload Files", type=[".tex", ".txt", ".md"])
if uploaded_file is not None:
    file_details = {
        "FileName": uploaded_file.name,
        "FileType": uploaded_file.type,
        "FileSize": uploaded_file.size,
    }
    #st.write(file_details)

    # if file_details.get('FileType') == '.tex':
    text_raw = uploaded_file.read().decode("utf8")

    #    st.write(text_raw)
    # else:
    #    st.write("Sorry, docs are currently not supported.")

st.sidebar.header("Data Cleaning")
clean_latex = st.sidebar.checkbox("Clean LaTeX")
split_hyphenation = st.sidebar.checkbox("Split Hyphenation")
lemmatize = st.sidebar.checkbox("Lemmatize")
delete_stopwords = st.sidebar.checkbox("Delete Stopwords")
stopwords = stopwords.words("english") if delete_stopwords else []
delete_punctuation = st.sidebar.checkbox("Delete Punctuation")
delete_single_characters = st.sidebar.checkbox("Delete Single Characters")

if uploaded_file is not None:
    st.plotly_chart(
        create_wordcounts_bar_chart(
            create_wordcounts(
                convert_text_to_clean_tokens(
                    text_raw,
                    delete_punctuation=delete_punctuation,
                    delete_single_characters=delete_single_characters,
                    stopwords=stopwords,
                    clean_latex=clean_latex,
                    lemmatize=lemmatize,
                    split_hyphenation=split_hyphenation,
                )
            ),
            color_by="TextType",
        )
    )
