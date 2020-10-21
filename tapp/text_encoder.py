import numpy as np
import nltk
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn import utils
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary
from abc import ABC, abstractmethod


class TextEncoder(ABC):

    def __init__(self, language="english", encoding_length=50):
        self.language = language

        try:
            nltk.data.find("corpora/wordnet")
        except LookupError:
            nltk.download("wordnet")
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords")

        self.encoding_length = encoding_length
        self.stop_words = set(stopwords.words(language))
        self.stop_words.remove("not")
        self.stop_words.remove("no")
        self.lemmatizer = WordNetLemmatizer() if language == "english" else None
        self.stemmer = SnowballStemmer(language)

        super().__init__()

    def preprocess_docs(self, docs, as_list=True):
        docs_preprocessed = []
        for doc in docs:
            doc = doc.lower()
            words = word_tokenize(doc, language=self.language)
            if self.lemmatizer is not None:
                words_processed = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words and word.isalpha()]
            else:
                words_processed = [self.stemmer.stem(word) for word in words if word not in self.stop_words and word.isalpha()]
            if as_list:
                docs_preprocessed.append(words_processed)
            else:
                docs_preprocessed.append(" ".join(words_processed))
        return docs_preprocessed

    @abstractmethod
    def fit(self, docs):
        pass

    @abstractmethod
    def transform(self, docs):
        pass


class BoWTextEncoder(TextEncoder):

    def __init__(self, language="english", encoding_length=100):
        self.name = "BoW"
        self.vectorizer = None
        super().__init__(language=language, encoding_length=encoding_length)

    def fit(self, docs):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 1), max_features=self.encoding_length, analyzer='word', norm="l2")
        self.vectorizer.fit(self.preprocess_docs(docs, as_list=False))
        return self

    def transform(self, docs):
        return self.vectorizer.transform(self.preprocess_docs(docs, as_list=False)).toarray()


class BoNGTextEncoder(TextEncoder):

    def __init__(self, language="english", encoding_length=100, n=2):
        self.name = "BoNG"
        self.n = n
        self.vectorizer = None
        super().__init__(language=language, encoding_length=encoding_length)

    def fit(self, docs):
        self.vectorizer = TfidfVectorizer(ngram_range=(self.n, self.n), max_features=self.encoding_length, analyzer='word', norm="l2")
        self.vectorizer.fit(self.preprocess_docs(docs, as_list=False))
        return self

    def transform(self, docs):
        return self.vectorizer.transform(self.preprocess_docs(docs, as_list=False)).toarray()


class PVTextEncoder(TextEncoder):

    def __init__(self,  language="english", encoding_length=20, epochs=15, min_count=2):
        self.name = "PV"
        self.epochs = epochs
        self.min_count = min_count
        self.model = None
        super().__init__(language=language, encoding_length=encoding_length)

    def fit(self, docs):
        docs = self.preprocess_docs(docs)

        tagged_docs = [TaggedDocument(words=doc, tags=[i]) for i, doc in enumerate(docs)]

        self.model = Doc2Vec(dm=1, vector_size=self.encoding_length, min_count=self.min_count, window=8)
        self.model.build_vocab(tagged_docs)

        self.model.train(utils.shuffle(tagged_docs), total_examples=len(tagged_docs), epochs=self.epochs)
        return self

    def transform(self, docs):
        docs = self.preprocess_docs(docs)
        return np.array([self.model.infer_vector(doc) for doc in docs])


class LDATextEncoder(TextEncoder):

    def __init__(self, language="english", encoding_length=20):
        self.name = "LDA"
        self.model = None
        self.num_topics = encoding_length
        self.dictionary = None
        super().__init__(language=language, encoding_length=encoding_length)

    def fit(self, docs):
        docs = self.preprocess_docs(docs)
        self.dictionary = Dictionary(docs)
        corpus = [self.dictionary.doc2bow(doc) for doc in docs]
        self.model = LdaModel(corpus, id2word=self.dictionary, num_topics=self.num_topics, minimum_probability=0.0)
        return self

    def transform(self, docs):
        docs = self.preprocess_docs(docs)
        docs = [self.dictionary.doc2bow(doc) for doc in docs]
        return np.array([self.model[doc] for doc in docs])[:, :, 1]
