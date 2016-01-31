#!/usr/bin/python3

import os

import log

from page import Page, AboutPage, ListPage, HomePage
from author import AuthorPage
from term import *
from template import Templates
import config

from languages import Languages

class Builder:

  def __init__(self,
               languages_path='languages',
               templates_path='templates',
               input_path    ='input',
               output_path   ='output',
               css_path      ='css',
               
               language='en-us'):
    self.path = {}
    
    self.path['languages'] = languages_path
    self.path['templates'] = templates_path
    self.path['input']     = input_path
    self.path['output']    = output_path
    self.path['css']       = css_path

    self.language = language
    self.languages = Languages(self.path['languages'], language)

    self.authors = []
    self.pages = []
    self.terms = []

    self.get_authors()
    self.get_pages()
    self.get_terms()
    
    self.get_synonyms()

  def get_file_list(self, root, ext='md'):
    root = os.path.join(self.path['input'], root)
    filenames = [os.path.join(root, f) for root, dirs, files in os.walk(root) for f in files]
    filenames = [x for x in filenames if os.path.splitext(x)[1][1:] == ext]

    if self.path['input']:
      filenames = [x[len(self.path['input']):].lstrip('/') for x in filenames]
      
    return filenames

  def get_site_name(self):
    return self.languages.get('site-name')

  ########################
  # GET PAGES
  ########################
    
  def get_authors(self):
    authors = self.get_file_list(config.input_path['authors'])
    for a in authors:
      self.authors.append(AuthorPage(self, a))
    self.parse_authors()

  def get_pages(self):
    articles = self.get_file_list(config.input_path['articles'])
    media = self.get_file_list(config.input_path['media'])
    for p in articles + media:
      self.pages.append(PagePage(self, p))
      
    self.parse_pages()

  def get_terms(self):
    terms = self.get_file_list(config.input_path['terms'])
    for t in terms:
      self.terms.append(TermPage(self, t))
      
    self.parse_terms()

  def get_synonyms(self):
    self.synonyms = {}
    for p in self.terms + self.pages:
      synonyms = p.get_synonyms()
      for x in synonyms:
        self.synonyms[p.get_slug()] = x

  def parse_authors(self):
    for a in self.authors:
      a.parse()

  def parse_pages(self):
    for p in self.pages:
      p.parse()
      
    for p in self.pages:
      p.collect()

  def parse_terms(self):
    for t in self.terms:
      t.parse()
      
    for t in self.terms:
      t.collect()

    for t in self.terms:
      t.post_collect()

  def get_author(self, slug):
    for a in self.authors:
      if a.get_slug() == slug:
        return a
    return None

  def get_term(self, slug):
    for t in self.terms:
      if t.refers_to(slug):
        return t
    return None

  ########################
  # BUILD
  ########################

  def build_authors(self):
    for p in self.authors:
      p.build()
  
  def build_about(self):
    p = AboutPage(self)
    p.build()

  def build_home(self):
    p = HomePage(self)
    p.build()

  def build_stylesheet(self):
    os.system('sassc ' + os.path.join(self.path['css'], 'style.scss') + ' ' + os.path.join(self.path['output'], 'style.css'))
  
  def build_logo(self):
    os.system('cp logo/ ' + self.path['output'] + ' -r')

  def build_terms(self):
    for t in self.terms:
      t.build()

  def build_list(self, name, pages, output_root=None):
    if not output_root: output_root = name
    output_root = self.languages.get('list-' + output_root + '-output-root')
    page = ListPage(self, pages, output_root)
    page.set_title(self.languages.get('list-' + name + '-title'))
    page.set_slug(self.languages.get('list-' + name + '-slug'))
    page.build()
  
  def build_terms_list(self):
    self.build_list('terms', self.terms)

    self.build_list('companies', [x for x in self.terms if type(x.get_term()) is CompanyTerm])
    self.build_list('engines', [x for x in self.terms if type(x.get_term()) is EngineTerm])
    self.build_list('rockets', [x for x in self.terms if type(x.get_term()) is RocketTerm])
    self.build_list('spacecraft', [x for x in self.terms if type(x.get_term()) is SpacecraftTerm])
  
  def build_pages_list(self):
    self.build_list('pages', self.pages)
    
  def build_articles_list(self):
    self.build_list('articles', self.pages)
    
  def build_media_list(self):
    self.build_list('media', self.pages)
    
  def build(self, language=None):
    self.templates = Templates(self.path['templates'])
    self.languages.set_default_language(language or self.language)

    self.build_about()
    self.build_authors()
    
    self.build_terms()
    
    self.build_stylesheet()
    
    self.build_logo()
    
    self.build_home()

    self.build_pages_list()
    self.build_articles_list()
    self.build_media_list()
    
    self.build_terms_list()
    
if __name__ == '__main__':
  b = Builder(language='en-us')
  b.build()
