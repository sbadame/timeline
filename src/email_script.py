# coding: utf-8
# Using https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

from collections import namedtuple

import datetime as datetime_lib
import glob
import itertools
import email as email_lib
import imaplib
import json
import quopri
import sys
import time
import os
import hashlib

def log(*objs):
    print("LOG: ", *objs, file=sys.stderr)

def get_filename_iter(filename):
  yield filename
  i = map(str, itertools.count(1))
  while True:
      yield filename + i.__next__()

def get_file_md5(path):
  hasher = hashlib.md5()
  with open(path, 'rb') as file:
    buf = file.read(65536)
    while len(buf) > 0:
      hasher.update(buf)
      buf = file.read(65536)
  return hasher.digest()

def get_bytes_md5(bytes_list):
  hasher = hashlib.md5()
  hasher.update(bytes_list)
  return hasher.digest()

def get_directory_hashes(path):
  return {get_file_md5(f):f  for f in glob.glob(path + '/*')}

Entry = namedtuple('Entry', ['datetime', 'who', 'text', 'image'])

def main():
  image_folder = '../images'
  if not os.path.isdir(image_folder):
    os.mkdir(image_folder)
  directory_hashes = get_directory_hashes(image_folder)
  owned_images = set()
  log("initial directory hashes: " + str(directory_hashes))

  config = json.loads(open('../configs/config.json', 'r').read().strip())
  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(config['login'], config['password'])
  mail.select('"[Gmail]/All Mail"')
  email_uids = mail.uid('search', None, '(HEADER Subject "%s")' % config['subject'])[1][0].split()
  message_set = ','.join([e.decode('utf-8') for e in email_uids])

  # RFC822 means download everything and make multi part work... super slow.
  log("fetching emails")
  result, data = mail.uid('fetch', message_set, '(RFC822)')
  log("done fetching emails")

  parsed_emails = [
    email_lib.message_from_bytes(raw_bytes)
    for (_, raw_bytes) in data[::2]] # Every second element is just a deliminator.

  log("parsing response")
  entries = []
  for e in parsed_emails:
    text = ''
    email_image_name = ''
    for part in e.walk():
      if 'from' in part:
        who = part.get('from')
      if 'received' in part:
        date = part.get('received').split(';')[1].strip()
        datetime = email_lib.utils.parsedate(date)[:6] # datetime doesn't JSON.
      if not part.is_multipart():
        if part.get_content_type() == 'text/html':
          text += part.get_payload()
        if part.get_content_type() == 'image/jpeg':
          image_name = image_folder + '/' + part.get_filename()
          if image_name not in owned_images:
            email_image_name = image_name
            owned_images.add(email_image_name)
          payload = part.get_payload(decode=True)
          payload_hash = get_bytes_md5(payload)
          if payload_hash in directory_hashes:
            log('ignoring %s, it matches a file' % part.get_filename())
          else:
            filenames = get_filename_iter(image_name)
            filename = filenames.__next__()
            while os.path.isfile(filename):
              filename = filenames.__next__()
            with open(filename, 'wb') as f:
              f.write(payload)
            directory_hashes[payload_hash] = filename
            log('Adding to cache: {%s : %s}' % (str(payload_hash), filename))
    text = quopri.decodestring(text).decode('UTF-8').replace(u"\u00a0", " ")
    entries.append(Entry(datetime, who, text, email_image_name))
  log("done parsing response")

  jsonables = [
    {field: entry.__dict__[field] for field in Entry._fields}
    for entry in entries]

  log("dumping json")
  return json.dumps(jsonables, indent=2)

if __name__ == "__main__":
  print(main())
