
import re
import os

import config
import template

import log
import util

import htmlmin

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
    self.output_root = ''
    self.language = None

    self.parsed = False

  def get_string(self, key):
    return self.builder.languages.get(self.language, key)

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
    self.path.output_root = os.path.join(self.output_root, self.get_slug())

  ########################
  # SETTERS
  ########################

  def set_title(self, title):
    self.title = title

  def set_slug(self, slug):
    self.slug = slug

  ########################
  # RENDERING
  ########################

  def get_body_classes(self):
    return [self.get_slug()]

  # used by render functions
  def get_arg(self, key):
    if key == 'body-classes':
      return ' '.join(self.get_body_classes())
    elif key == 'page-title':
      return self.get_title()
    elif key == 'site-name':
      return self.builder.get_site_name()
    elif key == 'main-classes':
      return ''

  # return the full page HTML
  def render_page_html(self):
    return self.builder.templates.render('page.html', self)

  ########################
  # BUILDING
  ########################

  # renders and saves the HTML version of the file
  def build_html(self):
    log.progress_step('html')
    html = self.render_page_html()

    html = htmlmin.minify(html)

    # main path
    output_path = self.get_output_path(config.html['index'])
    util.write_file(output_path, html, self.get_unique_identifier())

  def parse(self):
    if self.parsed: return
    self.parsed = True
    self._parse()

  def _parse(self):
    self.init_paths()

  def pre_build(self):
    self.parse()
  
  def post_build(self):
    pass
    
  # builds all output formats
  def build(self):
    
    self.pre_build()
    
    log.progress(self.get_unique_identifier())

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
    
    self.synonyms = []
    
    self.authors = []
    self.output_root = ''
    
  ########################
  # PATH
  ########################

  def get_input_path(self, filename=''):
    return self.path.get_input_path(filename)

  ########################
  # SETTERS
  ########################

  def add_author(self, author):
    self.authors.append(author)

  def add_synonym(self, synonym):
    self.synonyms.append(synonym)

  ########################
  # INPUT
  ########################

  def parse_header_line(self, key, value):
    if key == 'title':
      self.set_title(value)
    elif key == 'author':
      self.add_author(value)
    elif key == 'slug':
      self.set_slug(value)
    elif key == 'synonym':
      self.add_synonym(value)
    else:
      return False
    return True

  # parse input file
  def read_file(self):
    self.header = []
    
    f = util.open_file(self.get_input_path(), 'r', self.get_unique_identifier())

    text = ''
    
    while True:
      line = f.readline()
      
      # end of file
      if not line: break
      line = line.strip()

      # empty line
      if not line: continue

      # end of keys
      if not markdown_page_header_re.match(line):
        text += line + '\n'
        break

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

    text += f.read()
    self.content = Markdown(self.builder, text)
    f.close()

    for line in self.header:
      if not self.parse_header_line(line[0], line[1]):
        log.warning('unknown key "' + line[0] + '"', self.get_unique_identifier())

  ########################
  # RENDERING
  ########################

  def get_authors(self):
    return self.authors

  def get_authors_html(self):
    authors = []
    for a in self.authors:
      authors.append(a.get_inline_html())
    return util.andify(authors)

  def get_body_classes(self):
    return super().get_body_classes() + ['markdown']

  def get_arg(self, key):
    if key == 'markdown-contents':
      return self.render_html()
    elif key == 'markdown-authors':
      if self.authors:
        return self.builder.languages.get(self.language, 'authors-before') + ' ' + self.get_authors_html()
      else:
        return ''
    elif key == 'markdown-title':
      return self.get_title()
    elif key == 'page-contents':
      return self.builder.templates.render('markdown.html', self)
    return super().get_arg(key)

  def get_authors(self):
    authors = []
    for a in self.authors:
      authors.append(self.builder.get_author(a))
    self.authors = authors
    
  def _parse(self):
    super()._parse()
    self.read_file()
    self.init_paths()
    
    self.get_authors()
  
  def render_html(self):
    return self.content.get_html()

################################################
# Static Page (i.e. about, 404)
################################################

class StaticPage(MarkdownPage):

  def __init__(self, builder):
    super().__init__(builder)
    self.init_static_page()
    
  def get_body_classes(self):
    return super().get_body_classes() + ['static']

  def init_paths(self):
    super().init_paths()
    self.path.input_root = config.input_path['static']

################################################
# Dynamic Page (i.e. author, page, term, etc.)
################################################

class DynamicPage(MarkdownPage):

  def __init__(self, builder, input_path):
    super().__init__(builder)
    self.path.set_input_path(input_path)
    
################################################
# Misc Static Pages
################################################

class AboutPage(StaticPage):

  def init_static_page(self):
    self.path.set_input_filename('about' + config.md['ext'])
    self.slug = 'about'
