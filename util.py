
import os
import re
import log

def read_file(filename, requester):
  try:
    return open(filename, 'r').read()
  except FileNotFoundError:
    log.error('could not open "' + filename + '" for reading', requester=requester)

def write_file(filename, contents, requester):
  os.makedirs(os.path.normpath(os.path.dirname(filename)), exist_ok=True)
  open(filename, 'w').write(contents)
  # log.error('could not open "' + filename + '" for reading', requester=requester)

def to_slug(name, maxlength=100):
  name = '-'.join(name.split()).lower()
  name = re.sub('[^0-9a-zA-Z\-]+', '', name)
  name = name[:maxlength]
  if len(name) == maxlength: name += '-'
  return name

