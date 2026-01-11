import nltk
import numpy as np
import inspect

# ==========================================
# ФІКС ДЛЯ PYTHON 3.13 + PYMORPHY2
# ==========================================
# Бібліотека pymorphy2 використовує видалену функцію inspect.getargspec.
# Вона очікує 4 значення, а нова getfullargspec повертає 7.
# Ми робимо обгортку, щоб обрізати зайве.
if not hasattr(inspect, 'getargspec'):
    def _getargspec_wrapper(func):
        full_spec = inspect.getfullargspec(func)
        return full_spec.args, full_spec.varargs, full_spec.varkw, full_spec.defaults
    
    inspect.getargspec = _getargspec_wrapper
# ==========================================

import pymorphy2

# Ініціалізація аналізатора для української мови
morph = pymorphy2.MorphAnalyzer(lang='uk')

def tokenize(sentence):
    return nltk.word_tokenize(sentence)

def stem(word):
    """
    Знаходимо початкову форму слова (лему).
    Наприклад: "хрому" -> "хром", "файли" -> "файл"
    """
    p = morph.parse(word.lower())[0]
    return p.normal_form

def bag_of_words(tokenized_sentence, words):
    # Приводимо кожне слово речення до початкової форми
    sentence_words = [stem(word) for word in tokenized_sentence]
    
    # Створюємо масив (мішок слів)
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1
    return bag