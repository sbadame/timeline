# coding: utf-8

from collections import Counter
from textblob import TextBlob
import json

def parse(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    nouns = list(set(blob.noun_phrases + parse_nouns(blob)))
    sentiment = {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity}
    return (nouns, sentiment)

def parse_nouns(blob):
  # Return a where nouns are the keys, values are the number of occurences.
  return Counter([
    n.lower()
    for (n, pos) in blob.tags
    if pos.startswith('N')])
