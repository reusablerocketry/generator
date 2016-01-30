
import config
import template

import log
import util

from page import DynamicPage

################################################
# AuthorPage
################################################

class AuthorPage(DynamicPage):

  def __init__(self, builder, input_path):
    super().__init__(builder, input_path)
    self.output_root = self.builder.languages.get(self.language, 'page-author-slug')

    self.name = None

  def get_title(self):
    return self.name or self.builder.languages.get('unnamed-author')
  
  def get_arg(self, key):
    if key == 'markdown-title':
      return self.name
    elif key == 'author-name':
      return self.name
    elif key == 'author-link':
      return self.path.get_link_path()
    return super().get_arg(key)

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return False
    elif key == 'name':
      self.name = value
    elif key in ['email', 'reddit', 'twitter']:
      pass
    else:
      return False
    return True
      
  def get_inline_html(self):
    return self.builder.templates.render('author-inline.html', self)
    
