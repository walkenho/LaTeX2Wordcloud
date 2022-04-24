FROM python:3.8-slim-buster
LABEL maintainer="Jessica Walkenhorst"
LABEL description="LaTeX2Wordcloud"

#ARG PIP_VERSION="21.2.1"
#ARG POETRY_VERSION="1.1.6"

#RUN pip3 install -q "pip==$PIP_VERSION"
#RUN pip3 install -q "poetry==$POETRY_VERSION"

WORKDIR /home/

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

#RUN python -m nltk.downloader 'punkt' 'averaged_perceptron_tagger' 'universal_tagset' 'wordnet' 'stopwords' 'omw-1.4'

#COPY pyproject.toml poetry.lock ui.py ./
COPY LaTeX2Wordcloud.py ./
COPY src ./src/

#ADD nltk_data /root/nltk_data
ADD nltk_data /home/nltk_data
#COPY ./nltk_data /root/nltk_data
#RUN poetry install --no-dev
#RUN poetry run python -m nltk.downloader 'punkt' 'averaged_perceptron_tagger' 'universal_tagset' 'wordnet' 'stopwords' 'omw-1.4'

EXPOSE 8501

#ENTRYPOINT ["/bin/sh", "-c", "poetry", "run", "streamlit", "run",  "--server.port", "$PORT", "ui.py"]
#ENTRYPOINT ["/bin/sh", "-c", "streamlit", "run",  "--server.port", "$PORT", "ui.py"]
CMD streamlit run --server.port $PORT LaTeX2Wordcloud.py
