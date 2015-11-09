# /usr/bin/env python3.5
# coding: utf-8

"""Massage email output into useful json.

Usage: massage.py [-i FILE] [-p parsers]...

  -i <file>, --input=file          What file to parse. [default: email_script.json]
  -p <parsers>, --parsers=parsers  Which parsers to use. [default: all]
"""

from bs4 import BeautifulSoup
from docopt import docopt

import calendar
import json
import re
import drive
import nlp
import sys

all_parsers = ['nlp', 'drive']
days_of_the_week = '(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)'
months_of_the_year = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)'
quote_pattern = re.compile('On %s, %s' % (days_of_the_week, months_of_the_year), re.IGNORECASE)

fix_punctuation = lambda text : re.sub(r'([\.\?\!:])([^\s\.\?\!:])', r'\1 \2', text)
fix_dollars = lambda text: re.sub(r'([^\s\$])\$', r'\1 $', text)
fix_numbers = lambda text: re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)

def log(*objs):
    print("LOG: ", *objs, file=sys.stderr)

def filter_quote_text(text):
  quote_pattern_found = quote_pattern.search(text)
  if quote_pattern_found:
      text = text[:quote_pattern_found.start()]
  return text

def add_space_after_punctuation(text):
    def get_replacement(match):
      if match.group(0).startswith('http'):
          return match.group(0)
      else:
          return match.group(2) + ' ' + match.group(3)
    return re.sub(r'(https?://[^\s]+)|([\.\?!])([^\s\.])', get_replacement, text)

def massage_json(email, parsers):
  soup = BeautifulSoup(email['text'], 'html.parser')
  if soup.blockquote:
    soup.blockquote.extract()

  if 'drive' in parsers:
    files = drive.parse_files(soup)
    if files:
      email['files'] = files
    else:
      email['files'] = []

  email['tables'] = [str(t) for t in soup.find_all('table')]
  text = soup.get_text()

  text = filter_quote_text(text)
  text = text.strip()
  text = fix_punctuation(text)
  text = fix_numbers(text)
  text = fix_dollars(text)

  if 'nlp' in parsers:
    nouns, sentiment = nlp.parse(text)
    if nouns:
      email['nouns'] = nouns
    else:
      email['nouns'] = []

    email['sentiment'] = sentiment

  email['text'] = text
  email['links'] = [
    {'text': a.text, 'href': a.get('href')}
    for a in soup.find_all('a')
    if not a.get('href').startswith('mailto')]
  if email['image']:
    email['images'] = [email['image']]
  else:
    email['images'] = []
  return email

def main(arguments):
  data = open(arguments['--input']).read()
  parsed_json = json.loads(data)
  parsers = all_parsers if 'all' in arguments['--parsers'] else arguments['--parsers']
  massaged_json = [massage_json(e, parsers) for e in parsed_json]
  return json.dumps(massaged_json, indent=2)

if __name__ == "__main__":
  arguments = docopt(__doc__)
  log("Running with args: " + str(arguments))
  print(main(arguments))
