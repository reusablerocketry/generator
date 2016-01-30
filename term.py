
import config
import template

import log
import util

from page import DynamicPage

class Term:

  def __init__(self, page):
    self.term_page = page
    self.term_type = None
    self.builder = page.builder

    self.manufacturers = []
    self.rockets = []
    self.spacecraft = []
    self.stages = []

  def get_unique_identifier(self):
    return self.term_page.get_unique_identifier()

  def get_name(self):
    return self.term_page.get_title()

  ########################
  #
  ########################

  def add_manufacturer(self, company):
    self.manufacturers.append(company)

  def parse_header_line(self, key, value):
    if key == 'manufacturer':
      self.add_manufacturer(value)
    else:
      return False
    return True

  ########################
  # THINGS
  ########################

  # given a list of slugs, returns the thing
  def get_things(self, slugs, name, thing_type):
    things = []
    for slug in slugs:
      thing = self.builder.get_term(slug)
      if not thing:
        log.warning(name + ' "' + slug + '" not found', self.term_page.get_unique_identifier())
        continue
      if not thing.term:
        log.warning(name + ' "' + slug + '" has no term information', self.term_page.get_unique_identifier())
        continue
      if type(thing.term) is not thing_type:
        log.warning('page "' + slug + '" is not of type ' + name, self.term_page.get_unique_identifier())
        continue
      things.append(thing)
    return things

  def get_manufacturers(self):
    self.manufacturers = self.get_things(self.manufacturers, 'manufacturer', CompanyTerm)

  def parse(self):
    self.get_manufacturers()

  ########################
  # ARGS
  ########################

  def get_arg(self, key):
    if key == 'term-name':
      return self.get_name()
    elif key == 'term-link':
      return self.term_page.path.get_link_path()
    elif key == 'term-sidebar-contents':
      return self.get_sidebar_html()
    
  # run by the template while rendering; required_args is a list
  # of arguments that Page must provide

  ########################
  # SIDEBAR HTML
  ########################

  def get_sidebar_list(self, things, thing_name):
    if not things:
      return ''
    
    title = self.term_page.get_string('term-type-' + thing_name)
    if len(things) > 1:
      title = self.term_page.get_string('term-type-' + thing_name + '-plural')
    
    args = {}
    args['sidebar-list-title'] = title
    args['sidebar-list-classes'] = thing_name
    args['sidebar-list-items'] = ''.join([x.term.get_sidebar_item() for x in things])
    
    return self.builder.templates.render('term-sidebar-list.html', self, args)

  def get_sidebar_html(self):
    return self.get_sidebar_list(self.manufacturers, 'manufacturer')

  def get_sidebar_item(self):
    return self.get_name()

class VehicleTerm(Term):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'vehicle'

class RocketTerm(VehicleTerm):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'rocket'

class CompanyTerm(Term):
  
  def __init__(self, page):
    super().__init__(page)
    self.term_type = 'company'
    self.founding_date = None

  def get_arg(self, key):
    if key == 'company-name':
      return self.get_name()
    elif key == 'company-founding-date':
      return self.founding_date or self.term_page.get_string('term-type-company-founding-date-unknown')
    return super().get_arg(key)

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'founding-date':
      self.founding_date = value
    else:
      return False
    return True

  def get_sidebar_item(self):
    return self.builder.templates.render('term-sidebar-item-company.html', self)

################################################
# TermPage
################################################

class TermPage(DynamicPage):

  def __init__(self, builder, input_path):
    super().__init__(builder, input_path)
    self.output_root = self.builder.languages.get(self.language, 'page-term-slug')
    
    self.term = None

  ########################

  def get_term_sidebar_html(self):
    return self.term.get_sidebar_html()

  ########################


  def get_arg(self, key):
    if key == 'term-name':
      return self.title
    elif key == 'term-link':
      return self.path.get_link_path()
    elif key == 'term-sidebar-contents':
      return self.get_term_sidebar_html()
    elif key == 'markdown-contents':
      if self.term:
        return self.builder.templates.render('term-sidebar.html', self) + self.render_html()
      else:
        log.warning('no term information', self.get_unique_identifier())
        return self.render_html()
    return super().get_arg(key)

  def _parse(self):
    super()._parse()

    if self.term:
      self.term.parse()

  def set_term_type(self, term_type):
    if term_type == 'rocket':
      self.term = RocketTerm(self)
    elif term_type == 'company':
      self.term = CompanyTerm(self)
    else:
      log.w('unknown term type "' + term_type + '"', self.get_unique_identifier())

  def parse_header_line(self, key, value):
    if super().parse_header_line(key, value):
      return True
    elif key == 'type':
      self.set_term_type(value)
    elif self.term:
      return self.term.parse_header_line(key, value)
    else:
      return False
    return True
      
  def get_inline_html(self):
    return self.builder.templates.render('term-inline.html', self)
    
  def get_term_link(self):
    return self.path.get_link_path()
    
