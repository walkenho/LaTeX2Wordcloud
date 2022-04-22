# from latex2wordcloud.LaTeXStripper import strip_text

from ipywidgets import FileUpload

from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import plotly.express as px
import pandas as pd

from typing import List
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import pos_tag
import re
import string

from latex2wordcloud.LaTeXStripper import strip_text

universal_tags_to_wordnet = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}
wordnet_to_universal_tags = {v: k for k, v in universal_tags_to_wordnet.items()}

"""Map universal POS tags to WordNet POS tags.

Wordnet has five tags:
n - NOUN 
v - VERB 
a - ADJECTIVE 
s - ADJECTIVE SATELLITE 
r - ADVERB

Ignore the 's' tag.
"""


def lemmatize_universal_tagged_token(tagged_token, lemmatizer=WordNetLemmatizer()):
    wordnet_tag = universal_tags_to_wordnet.get(tagged_token[1], "undefined")
    if wordnet_tag == "undefined":
        return (lemmatizer.lemmatize(tagged_token[0]), wordnet_tag)
    else:
        return (lemmatizer.lemmatize(tagged_token[0], wordnet_tag), wordnet_tag)


def tokenize_text(text):
    return pos_tag(word_tokenize(text), tagset="universal")


def lemmatize_tokens(tokens):
    return [lemmatize_universal_tagged_token(token) for token in tokens]


def convert_tokens_to_lowercase(tokens):
    return [(token[0].lower().strip(), token[1]) for token in tokens]


def filter_stopwords(tokens, stopwords):
    return [token for token in tokens if token[0] not in stopwords]


def keep_only_specified_tags(tokens, tag_list):
    return [token for token in tokens if token[1] in tag_list]


def delete_punctuation_from_tokens(tokens):
    """Delete punctuation but keep hyphens. Filter out punctuation tokens."""
    punctuation_without_hyphen = re.sub("-", "", string.punctuation)
    return [
        (token[0].translate(str.maketrans("", "", punctuation_without_hyphen)), token[1])
        for token in tokens
        if re.sub("^\W*", "", token[0])
    ]


def delete_single_characters_from_tokens(tokens):
    return [token for token in tokens if len(token[0]) > 1]


def split_hyphenated_tokens(tokens):
    return [(token_p, token[1]) for token in tokens for token_p in token[0].split("-")]


def convert_text_to_clean_tokens(
    text: str,
    clean_latex=False,
    split_hyphenation=False,
    lemmatize=False,
    stopwords=None,
    taglist=None,
    delete_punctuation=False,
    delete_single_characters=False
):
    """Convert text to list of (cleaned) tokens using NLTK tokenizer
    :param
    clean_latex: Use LaTeXStripper to remove LaTeX formatting, Default: False
    split_hyphenation: Split hyphenation before lemmatization, Default: False
    lemmatizatize: Lemmatize tokens, Default: False
    stopwords: List of stopwords to be filtered out. If None, nothing is filtered out.
    taglist: List of pos-tags to be kept. If None, all tags are kept.
    delete_punctuation: Delete punctuation, Default: False
    delete_single_character: Delete single character, Default: False
    """

    if clean_latex:
        text = strip_text(text)

    tokens = tokenize_text(text)

    # split hyphenation before lemmatization!!
    if split_hyphenation:
        tokens = split_hyphenated_tokens(tokens)

    if lemmatize:
        tokens = lemmatize_tokens(tokens)

    tokens = convert_tokens_to_lowercase(tokens)

    if stopwords:
        tokens = filter_stopwords(tokens, stopwords)

    if taglist:
        tokens = keep_only_specified_tags(tokens, taglist)

    if delete_punctuation:
        tokens = delete_punctuation_from_tokens(tokens)

    if delete_single_characters:
        tokens = delete_single_characters_from_tokens(tokens)

    return tokens


def is_latex(string):
    if string in [
        "end",
        "begin",
        "eq",
        "mathscr",
        "rangle",
        "equation",
        "frac",
        "equation",
        "left",
        "right",
        "label",
        "ref",
        "eqnarray",
        "cite",
        "fig",
        "figure",
        "section",
        "sec",
        "eqref",
        "nonumber",
    ]:
        return "LaTeX"
    else:
        return "Other"


def is_latex_math_or_text(string):
    latex = is_latex(string)
    if latex == "LaTeX":
        return latex
    elif string in [
        "omega",
        "omega_",
        "hat",
        "d_",
        "d",
        "bar",
        "tau",
        "psi",
        "pi",
        "phi",
        "sin",
        "varphi",
        "chi",
    ]:
        return "Math"
    else:
        return "Text"


def create_wordcounts_bar_chart(wordcounts: pd.DataFrame, top=50, color_by="TextType") -> None:
    # TODO: Add hoverinfo to display texttype and latex or not
    # todo: update axis labels
    words_to_include = (
        wordcounts[["word", "total_count"]]
        .drop_duplicates()
        .nlargest(top, "total_count")["word"]
        .values
    )
    fig = px.bar(
        wordcounts[wordcounts["word"].isin(words_to_include)], x="word", y="count", color=color_by
    )
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"})
    #fig.show()
    return fig


def create_wordcounts(tokens):
    df = pd.DataFrame([{"word": token[0], "pos_tag": token[1]} for token in tokens])
    df = df.groupby(["word", "pos_tag"], as_index=False).size().rename(columns={"size": "count"})
    df["total_count"] = df.groupby("word")["count"].transform(lambda x: x.sum())
    df["TextType"] = df["word"].map(lambda x: is_latex_math_or_text(x))
    df["pos_tag"] = df["pos_tag"].map(lambda x: wordnet_to_universal_tags.get(x, "other"))
    return df


def create_wordcounts_text(text):
    # CountVectorizer stop_words problematic, see: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
    # cv_raw = CountVectorizer(min_df=0, stop_words='english', max_features=50)
    cv_raw = CountVectorizer(min_df=0, max_features=50)
    counts_raw = cv_raw.fit_transform([text])

    wordcounts = []
    for word, count in zip(cv_raw.get_feature_names_out(), counts_raw.toarray()[0]):
        wordcounts.append({"word": word, "count": count})
    df_wordcounts = pd.DataFrame(wordcounts)
    df_wordcounts["is_latex"] = df_wordcounts["word"].map(lambda x: is_latex(x))
    df_wordcounts["TextType"] = df_wordcounts["word"].map(lambda x: is_latex_math_or_text(x))
    return df_wordcounts


from wordcloud import WordCloud


def create_wordcloud(words_cleaned: pd.DataFrame, filename=None):
    wordcloud = WordCloud().generate_from_frequencies(
        words_cleaned[["word", "total_count"]]
        .drop_duplicates()
        .set_index("word")
        .to_dict()["total_count"]
    )

    if filename:
        wordcloud.to_file(filename)

    display(wordcloud.to_image().resize((800, 400)))