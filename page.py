
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

    self.abbreviation = None

    self.parsed = False

    self.synonyms = []
    
  def get_synonyms(self):
    return self.synonyms

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

  def get_abbreviation(self):
    return self.abbreviation or self.get_title()

  ########################
  # PATH
  ########################

  def get_output_path(self, filename=''):
    return self.path.get_output_path(filename)

  def get_input_path(self, filename=''):
    return self.path.get_input_path(filename)

  # sets up input/output paths
  def init_paths(self):
    self.path.output_root = os.path.join(self.output_root, self.get_slug())

  ########################
  # SETTERS
  ########################

  def set_title(self, title):
    self.title = title

  def set_abbreviation(self, abbreviation):
    self.add_synonym(abbreviation)
    self.abbreviation = abbreviation

  def set_slug(self, slug):
    self.slug = util.to_slug(slug)

  def refers_to(self, slug):
    if util.to_slug(self.get_title()) == slug: return True
    if self.get_slug() == slug: return True
    if slug in [util.to_slug(s) for s in self.synonyms]: return True
    return False

  def add_synonym(self, synonym):
    self.synonyms.append(synonym)

  def get_link_path(self):
    return self.path.get_link_path()

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
    elif key == 'page-abbreviation':
      return self.get_abbreviation()
    elif key == 'page-link':
      return self.get_link_path()
    elif key == 'site-name':
      return self.builder.get_site_name()
    elif key == 'page-synonyms':
      if self.synonyms:
        return self.builder.templates.render('page-synonyms.html', self)
      return ''
    elif key == 'page-synonyms-list':
      lang_string = 'page-synonyms'
      if len(self.synonyms) > 1:
        lang_string = 'page-synonyms-plural'
      return self.get_string(lang_string).format(util.andify(self.synonyms, 'or'))
    elif key == 'main-classes':
      return ''

  # return the full page HTML
  def render_page_html(self):
    return self.builder.templates.render('page.html', self)

  def render_list_html(self):
    return self.builder.templates.render('list-item.html', self)

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
    
    self.authors = []
    self.output_root = ''
    
  ########################
  # SETTERS
  ########################

  def add_author(self, author):
    self.authors.append(author)

  ########################
  # INPUT
  ########################

  def parse_header_line(self, key, value):
    if key == 'title':
      self.set_title(value)
    elif key == 'comment':
      pass
    elif key == 'abbreviation':
      self.set_abbreviation(value)
    elif key == 'author':
      self.add_author(value)
    elif key == 'synonym':
      self.add_synonym(value)
    elif key == 'slug':
      self.set_slug(value)
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

      if line.startswith('//'): continue
      if line.startswith('#'): continue

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

    for line in self.header:
      if not self.parse_header_line(line[0], line[1]):
        log.warning('unknown key "' + line[0] + '"', self.get_unique_identifier())

    text += f.read()
    self.content = Markdown(self.builder, text, self.get_unique_identifier())
    f.close()

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
    
class HomePage(StaticPage):

  def init_static_page(self):
    self.path.set_input_filename('home' + config.md['ext'])
    self.slug = ''
    
  def init_paths(self):
    super().init_paths()
    self.path.output_root = ''
    
################################################
# Misc Static Pages
################################################

class ListPage(Page):

  def __init__(self, builder, pages, output_root=''):
    super().__init__(builder)

    self.pages = pages

    self.pages.sort(key=lambda a: a.get_title())

    self.output_root = output_root
    
  def get_body_classes(self):
    return super().get_body_classes() + ['list']

  def get_list_contents(self):
    items = []
    for page in self.pages:
      items.append(page.render_list_html())
    if not items:
      return self.builder.templates.render('list-empty.html', self)
    return ''.join(items)

  def get_arg(self, key):
    if key == 'list-contents':
      return self.get_list_contents()
    elif key == 'page-contents':
      return self.builder.templates.render('list.html', self)
    else:
      return super().get_arg(key)
