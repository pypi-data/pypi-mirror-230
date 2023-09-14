from __future__ import annotations

from typing import Tuple

from sklearn.feature_extraction.text import TfidfVectorizer

TOKEN = str
TFIDF = float
TOKEN_TFIDF_PAIR = Tuple[TOKEN, TFIDF]


class TfidfInterpreter:
    """
    >>> corpus = [
    ...     "This is the first document.",
    ...     "This document is the second document.",
    ...     "And this is the third one.",
    ...     "Is this the first document?",
    ... ]
    >>> vectorizer = TfidfVectorizer().fit(corpus)
    >>> interpreter = TfidfInterpreter(vectorizer)
    >>> tfidf = interpreter.interpret(corpus[0])
    >>> for item in tfidf:
    ...     print(item[0], item[1])
    first 0.5802858236844359
    document 0.46979138557992045
    this 0.38408524091481483
    the 0.38408524091481483
    is 0.38408524091481483
    """

    def __init__(self, vectorizer: TfidfVectorizer) -> None:
        self.vectorizer = vectorizer

    def interpret(self, document: str) -> list[TOKEN_TFIDF_PAIR]:
        tfidf_vector = self.vectorizer.transform([document])[0]
        tfidf_array = tfidf_vector.toarray()[0]
        tokens = self.vectorizer.inverse_transform(tfidf_vector)[0]
        pairs = [
            (token, tfidf_array[self.vectorizer.vocabulary_[token]])
            for token in tokens
        ]
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)
