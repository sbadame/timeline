import os
import re
import requests
import functools
import sys

from string import Template

KEY_PATH = '../configs/drive.key'
URL_TEMPLATE = Template('https://www.googleapis.com/drive/v2/files/${id}?fields=alternateLink%2CthumbnailLink%2Ctitle&key=${key}')

@functools.lru_cache(maxsize=1)
def get_api_key():
  if os.path.isfile(KEY_PATH):
    print('LOG: loading google drive key')
    return open(KEY_PATH, 'r').read().strip()
  else:
    print('LOG: ' + KEY_PATH + ' is missing, Google drive parsing is disabled', file=sys.stderr)
    return False

def parse_files(soup):
  key = get_api_key()
  if not key:
    return
  results = []
  for a in soup.find_all('a'):
    if not a.has_attr('href'):
      continue
    m = re.search(r'drive.google.com/file/d/([^/]+)', a.get('href'))
    if m:
      file_id = m.group(1)
      r = requests.get(URL_TEMPLATE.substitute(id=file_id,key=key))
      if r.status_code == 200:
        results.append(r.json())
  return results
