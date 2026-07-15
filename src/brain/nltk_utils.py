import inspect
import re

import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer


if not hasattr(inspect, "getargspec"):
    def _getargspec_wrapper(func):
        full_spec = inspect.getfullargspec(func)
        return full_spec.args, full_spec.varargs, full_spec.varkw, full_spec.defaults

    inspect.getargspec = _getargspec_wrapper


_TOKEN_FALLBACK_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)
stemmer = PorterStemmer()


def tokenize(sentence):
    """Split a sentence into tokens with a safe fallback when punkt is unavailable."""
    text = str(sentence or "").strip()
    if not text:
        return []

    try:
        return nltk.word_tokenize(text)
    except LookupError:
        return _TOKEN_FALLBACK_PATTERN.findall(text)


def stem(word):
    """Reduce a word to its base form."""
    return stemmer.stem(str(word).lower())


def bag_of_words(tokenized_sentence, words):
    """Create a binary bag-of-words vector for the input sentence."""
    sentence_words = {stem(word) for word in tokenized_sentence}
    bag = np.zeros(len(words), dtype=np.float32)
    for index, word in enumerate(words):
        if word in sentence_words:
            bag[index] = 1.0
    return bag
