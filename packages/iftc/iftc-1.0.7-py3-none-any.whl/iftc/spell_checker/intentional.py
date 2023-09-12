import json
import numpy as np
import pandas as pd
import re
import os

from iftc import ift_config
from .text_processor import text_normalize
from nltk.util import ngrams


class Intentional:
  def __init__(self):
    self.bi_acronyms = self._load_data(ift_config.bi_acronyms_path)
    self.uni_acronyms = self._load_data(ift_config.uni_acronyms_path)
    # self.knowledge_base = self._load_data(ift_config.knowledge_base_path)

  def _load_data(self, file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
    return data

  def _remove_word(self, ignore: str, words: list, ngram=1):

    if ngram == 2:
      return list(filter(lambda a: a != ignore, words))
    else:
      text = ' '.join(words)
      result = text.replace(ignore, '').split()
      return result

  def _filter_candidate(self, unigrams, bigrams):
    uni_candidate = []
    bi_candidate = []

    # for e in self.knowledge_base:
    #   for bi_word in bigrams:
    #     if bi_word in e['Instances']:
    #       bi_candidate.append({'origin': e['Origin'], 'acronym': bi_word})
    #       bigrams = self._remove_word(bi_word, bigrams, 2)
    #       unigrams = self._remove_word(bi_word, unigrams, 1)

    for e in self.bi_acronyms:
      for bi_word in bigrams:
        if bi_word in e['Instances']:
          bi_candidate.append({'origin': e['Origin'], 'acronym': bi_word})
          bigrams = self._remove_word(bi_word, bigrams, 2)
          unigrams = self._remove_word(bi_word, unigrams, 1)

    # for e in self.knowledge_base:
    #   for uni_word in unigrams:
    #     if uni_word in e['Instances']:
    #       uni_candidate.append({'origin': e['Origin'], 'acronym': uni_word})
    #       unigrams = self._remove_word(uni_word, unigrams, 1)

    for e in self.uni_acronyms:
      for uni_word in unigrams:
        if uni_word in e['Instances']:
          uni_candidate.append({'origin': e['Origin'], 'acronym': uni_word})
          unigrams = self._remove_word(uni_word, unigrams, 1)

    return uni_candidate, bi_candidate

  def _word_correction(self, uni_candidate, bi_candidate, message):
    corrected_text = []

    text = text_normalize(message)
    #text = message.lower()
    bi_candidate = {each['origin']: each for each in bi_candidate}.values()
    uni_candidate = {each['origin']: each for each in uni_candidate}.values()
    for cdd in bi_candidate:
      text = text.replace(
          cdd['acronym'], ift_config.M_START+cdd['origin']+ift_config.M_END)

    words = text.split()
    inner = False

    for w in words:
      if ift_config.M_START in w:
        corrected_text.append(w)
        inner = True
      elif ift_config.M_END in w:
        corrected_text.append(w)
        inner = False
      elif inner:
        corrected_text.append(w)
      else:
        add = True
        for cdd in uni_candidate:
          if cdd['acronym'] == w:
            corrected_text.append(
                ift_config.M_START+cdd['origin']+ift_config.M_END)
            add = False
            break
        if add:
          corrected_text.append(w)

    return ' '.join(corrected_text)

  def spelling_correction(self, message: str):
    try:
      words = text_normalize(message).split()
      unigrams = words
      bigrams = [w[0]+' '+w[1] for w in list(ngrams(words, 2))]

      uni_candidate, bi_candidate = self._filter_candidate(unigrams, bigrams)
      corrected_text = self._word_correction(
          uni_candidate, bi_candidate, message)
      #print('origin: {} | correction: {}'.format(message, corrected_text))
      return corrected_text
    except Exception as e:
      print(e)
      return message, []
