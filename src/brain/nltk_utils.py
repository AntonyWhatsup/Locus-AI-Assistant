import nltk
import numpy as np
import inspect
from nltk.stem.porter import PorterStemmer

# Fix for Python 3.11+ (handling old inspect library)
if not hasattr(inspect, 'getargspec'):
    def _getargspec_wrapper(func):
        full_spec = inspect.getfullargspec(func)
        return full_spec.args, full_spec.varargs, full_spec.varkw, full_spec.defaults
    inspect.getargspec = _getargspec_wrapper

stemmer = PorterStemmer()

def tokenize(sentence):
    """Splits a sentence into a list of words (tokenization)."""
    return nltk.word_tokenize(sentence)

def stem(word):
    """Reduces a word to its base form (stemming)."""
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    """
    Creates a binary vector (Bag of Words):
    1 - if word is present in sentence, 0 - if not.
    """
    sentence_words = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1
    return bag
