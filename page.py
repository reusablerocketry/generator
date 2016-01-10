
import re

import config
import template

import log
import util

from path import Path
from md import Markdown

markdown_page_header_re = re.compile('^[a-zA-Z\-]+\s*:.*$')

################################################
# Page
################################################

class Page:

  def __init__(self, builder):
    self.template = ''
    self.builder = builder
    self.path = Path(builder)
    self.title = ''
    self.slug = ''

  # used to uniquely identifiy the Page in log output
  def get_unique_identifier(self):
    return self.get_slug()

  def get_slug(self):
    return self.slug or util.to_slug(self.get_title())

  # human-readable page title
  def get_title(self):
    return self.title or self.builder.languages.get('untitled-page')

  ########################
  # PATH
  ########################

  def get_output_path(self, filename=''):
    return self.path.get_output_path(filename)

  # sets up input/output paths
  def init_paths(self):
    self.path.output_root = self.get_slug()

  ########################
  # RENDERING
  ########################

  # used by render functions
  def get_arg(self, key):
    if key == 'page-title':
      return self.get_title()
    elif key == 'site-name':
      return self.builder.get_site_name()

  # run by the template while rendering; required_args is a list
  # of arguments that Page must provide
  def get_args(self, required_args):
    args = {}
    for key in required_args:
      
      value = self.get_arg(key)
      if value == None:
        value = '### ' + key + ' ###'
        log.warning('key "' + key + '" not found ', self.get_unique_identifier())
        
      args[key] = value

    return args

  # return the full page HTML
  def render_page_html(self):
    return self.builder.templates.render(config.template['page.html'], self)

  ########################
  # BUILDING
  ########################

  # renders and saves the HTML version of the file
  def build_html(self):
    log.progress_step('html')
    html = self.render_page_html()

    # main path
    output_path = self.get_output_path(config.html['index'])
    util.write_file(output_path, html, self.get_unique_identifier())

  def pre_build(self):
    pass
  
  def post_build(self):
    pass
    
  # builds all output formats
  def build(self):
    log.progress(self.get_unique_identifier())

    self.init_paths()
    
    self.pre_build()
    self.build_html()
    self.post_build()
    
    log.progress_done()

################################################
# MarkdownPage
################################################

# Each MarkdownPage has a title and zero or more authors.

class MarkdownPage(Page):

  def __init__(self, builder):
    super().__init__(builder)
    self.authors = []
    
  ########################
  # PATH
  ########################

  def get_input_path(self, filename=''):
    return self.path.get_input_path(filename)

  ########################
  # SETTERS
  ########################

  def set_title(self, title):
    self.title = title

  def add_author(self, author):
    self.authors.append(author)

  ########################
  # INPUT
  ########################

  def parse_header_line(self, key, value):
    if key == 'title':
      self.set_title(value)
    elif key == 'author':
      self.add_author(value)
    else:
      log.warning('unknown key "' + key + '"', self.get_unique_identifier())

  # parse input file
  def read_file(self):
    self.header = []
    
    f = util.open_file(self.get_input_path(), 'r', self.get_unique_identifier())
    
    while True:
      line = f.readline()
      
      # end of file
      if not line: break
      line = line.strip()
      
      # empty line
      if not line: continue

      # end of keys
      if not markdown_page_header_re.match(line): break

      key, value = [x.strip() for x in line.split(':', 1)]

      if value.endswith('\\'): # continuation
        value = value[:-1]
        while True:
          line = f.readline().strip()
          if not line: break
          if line.endswith('\\'):
            value += ' ' + line[:-1]
            continue
          value += ' ' + line
          break
            
      self.header.append([key, value])

    self.content = Markdown(self.builder, f.read())
    f.close()

    for line in self.header:
      self.parse_header_line(line[0], line[1])


  ########################
  # RENDERING
  ########################

  def get_arg(self, key):
    if key == 'page-contents':
      return self.render_html()
    return super().get_arg(key)
    
  def pre_build(self):
    self.read_file()
  
  def render_html(self):
    return self.content.get_html()

################################################
# Static Page
################################################

class StaticPage(MarkdownPage):

  def __init__(self, builder):
    super().__init__(builder)
    self.init_static_page()
    
  def init_paths(self):
    super().init_paths()
    self.path.input_root = config.path['static']

################################################
# Misc Static Pages
################################################

class AboutPage(StaticPage):

  def init_static_page(self):
    self.path.set_input_filename('about' + config.md['ext'])
    self.slug = 'about'
