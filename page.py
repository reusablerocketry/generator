
import config
import template

import log
import util

from path import Path

################################################
# Page
################################################

class Page:

  def __init__(self, builder):
    self.template = ''
    self.builder = builder
    self.path = Path(builder)

  # used to uniquely identifiy the Page in log output
  def get_local_identifier(self):
    return self.get_slug()

  def get_slug(self):
    return util.to_slug(self.get_title())

  # human-readable page title
  def get_title(self):
    return self.builder.languages.get('untitled-page')

  ########################
  # PATH
  ########################

  def get_output_path(self, filename=''):
    return self.path.get_output_path(filename)

  # sets up input/output paths
  def init_paths():
    log.error('classes that extend Page() should implement an init_paths() function')

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
        log.warning('key "' + key + '" not found ', self.get_local_identifier())
        
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
    util.write_file(output_path, html, self.get_local_identifier())
    
  # builds all output formats
  def build(self):
    log.progress(self.get_local_identifier())
    self.init_paths()
    
    self.build_html()
    
    log.progress_done()

################################################
# Static Page
################################################

class StaticPage(Page):

  def get_title(self):
    return self.builder.languages.get('untitled-static-page')
  
  def init_paths(self):
    self.path.output_root = self.get_slug()
  
  def render_html(self):
    return self.builder.templates.render('page.html', self)

################################################
# Misc Static Pages
################################################

class AboutPage(StaticPage):

  def get_arg(self, key):
    if key == 'page-contents':
      return 'foocontents'
    return super().get_arg(key)
    
  def get_title(self):
    return self.builder.languages.get('page-title-about')
  
