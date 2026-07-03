import nltk
import numpy as np
import inspect
from nltk.stem.porter import PorterStemmer

# Poprawka dla Python 3.11+ (obsługa starej biblioteki inspect)
if not hasattr(inspect, 'getargspec'):
    def _getargspec_wrapper(func):
        full_spec = inspect.getfullargspec(func)
        return full_spec.args, full_spec.varargs, full_spec.varkw, full_spec.defaults
    inspect.getargspec = _getargspec_wrapper

stemmer = PorterStemmer()

def tokenize(sentence):
    """Dzieli zdanie na listę słów (tokenizacja)."""
    return nltk.word_tokenize(sentence)

def stem(word):
    """Sprowadza słowo do jego formy podstawowej (stemming)."""
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    """
    Tworzy wektor binarny (Bag of Words):
    1 - jeśli słowo występuje w zdaniu, 0 - jeśli nie.
    """
    sentence_words = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1
    return bag
