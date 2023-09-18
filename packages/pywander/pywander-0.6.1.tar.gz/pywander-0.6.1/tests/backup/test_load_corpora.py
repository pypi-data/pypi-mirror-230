#!/usr/bin/env python
# -*-coding:utf-8-*-


from pywander.nlp.corpus import laozi
from simple_nltk import FreqDist
from pywander.nlp.chinese_stop_words import STOP_WORDS
from pywander.nlp.utils import is_empty_string



def test_load_corpora():
    t = FreqDist(
        [i for i in laozi if (i not in STOP_WORDS and not is_empty_string(i))])

    assert t.most_common(50)[0][0] == '不'
