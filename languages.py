
import os
import util
import re

import log

################################################
# Language
################################################

class Language:

  def __init__(self, filename, language_root):
    self.language_root = language_root 
    self.filename = None
    
    self.keys = {}
    
    self.key_warnings = []
    
    self.set_filename(filename)

  # sets filename and reads the content, if necessary
  def set_filename(self, filename):
    if filename:
      self.filename = filename
      self.read()
    else:
      log.error('language has null filename')

  # gets the absolute path to the template file
  def get_filename(self):
    return os.path.join(self.language_root, self.filename)

  def get_language(self):
    return self.filename

  # reads the template file into self.contents
  def read(self):
    content = util.read_file(self.get_filename(), 'Language("' + self.get_filename() + '")')

    line_number = 0
    for line in content.split('\n'):
      line_number += 1
      line = line.strip()
      if not line:
        continue
      try:
        key, value = line.split(':', 1)
      except ValueError:
        log.warning('line ' + str(line_number) + ' is malformed', self.get_filename())
        continue
      self.keys[key] = value.strip()

  # returns the formatted version of self.content
  def get(self, key):
    if key not in self.keys and key not in self.key_warnings: # only annoy once
      log.warning('in ' + self.get_language() + ', key "' + key + '" does not exist')
      self.key_warnings.append(key)
    return self.keys.get(key, '! ' + key + ' !')

################################################
# Languages
################################################

class Languages:

  def __init__(self, language_root, default_language):
    self.languages = {}
    self.language_root = language_root
    self.default_language = default_language

  def set_default_language(self, language):
    self.default_language = language

  # returns the language, reading from disk if necessary
  def get_language(self, filename):
    if filename not in self.languages:
      self.languages[filename] = Language(filename=filename, language_root=self.language_root)
    return self.languages[filename]

  # returns the rendered version of the language
  def get(self, language, key=None):
    if not key:
      key = language
      language = self.default_language
    return self.get_language(language).get(key)
  
