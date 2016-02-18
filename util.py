
import os
import re
import log
import math

def read_file(filename, requester):
  try:
    return open(filename, 'r').read()
  except FileNotFoundError:
    log.error('could not open "' + filename + '" for reading', requester=requester)

def open_file(filename, flags, requester):
  try:
    return open(filename, flags)
  except FileNotFoundError:
    log.error('could not open "' + filename + '" with flags "' + flags + '"', requester=requester)

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

def to_wiki(name):
  name = '_'.join(name.split()).title()
  name = re.sub('[^0-9a-zA-Z\_\.]+', '', name)
  return name

def andify(items, ander='and'):
  if len(items) == 0:
    return ''
  elif len(items) == 1:
    return items[0]
  elif len(items) == 2:
    return items[0] + ' ' + ander + ' ' + items[1]
  else:
    anded = ''
    for i in range(len(items) - 1):
      anded += items[i] + ', '
    anded += ander + ' ' + items[i-1]
    return anded

def boolean(s):
  s = s.lower()
  if s in ['true', '1', 'yes']: return True
  return False

def dv(isp, start, end):
  return isp * 9.81 * math.log(start / end)
      
def comma_int(number):
  return '{:,}'.format(int(number))

