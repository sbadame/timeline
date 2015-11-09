# coding: utf-8

from collections import Counter
from textblob import TextBlob
import json

def parse(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    nouns = merge_counts(blob.np_counts, parse_nouns(blob))
    sentiment = {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
    return (nouns, sentiment)

def parse_nouns(blob):
  # Return a where nouns are the keys, values are the number of occurences.
  # POS Tagging reference: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
  return Counter([
    n.lower()
    for (n, pos) in blob.tags
    if pos.startswith('N') or pos == 'VBG'])

def merge_counts(dict1, dict2):
  # Combines to dictionaries, if a key exists in both, the value is their sum.
  merged = {}
  for key in {**dict1, **dict2}:
    if key in dict1 and key in dict2:
      merged[key] = dict1[key] + dict2[key]
    elif key in dict1:
      merged[key] = dict1[key]
    else:
      merged[key] = dict2[key]
  return merged
