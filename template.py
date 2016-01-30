
import os
import util
import re

import log

format_match_re = re.compile('\{([a-zA-Z\-_\.]+)\}')

################################################
# Template
################################################

class Template:

  def __init__(self, filename=None, template_root=''):
    self.filename = None
    self.template_root = template_root

    self.set_filename(filename)

  # sets filename and reads the content, if necessary
  def set_filename(self, filename):
    if filename:
      self.filename = filename
      self.read()
    else:
      log.error('template has null filename')

  # gets the absolute path to the template file
  def get_filename(self):
    return os.path.join(self.template_root, self.filename)

  # reads the template file into self.contents
  def read(self):
    self.content = util.read_file(self.get_filename(), 'Template')

  # returns a list of arguments that the formatter must provide values for
  def get_required_args(self):
    return re.findall(format_match_re, self.content)

  def get_args(self, formatter, required_args, overrides={}):
    args = {}
    for key in required_args:
      value = formatter.get_arg(key)
      if value == None:
        if key in overrides:
          args[key] = overrides[key]
          continue
        log.warning('key "' + key + '" not found ', formatter.get_unique_identifier())
      args[key] = value
    return args
  
  # returns the formatted version of self.content
  def render(self, formatter, overrides={}):
    if not self.content:
      log.error('template cannot render without content')
    args = self.get_args(formatter, self.get_required_args(), overrides)
    return self.content.format(**args)

################################################
# Templates
################################################

class Templates:

  def __init__(self, template_root):
    self.templates = {}
    self.template_root = template_root

  # returns the template, reading from disk if necessary
  def get_template(self, filename):
    if filename not in self.templates:
      self.templates[filename] = Template(filename=filename, template_root=self.template_root)
    return self.templates[filename]

  # returns the rendered version of the template
  def render(self, filename, formatter, overrides={}):
    return self.get_template(filename).render(formatter, overrides)
