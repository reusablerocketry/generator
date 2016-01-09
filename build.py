#!/usr/bin/python3

import os

import log

from page import Page, AboutPage
from template import Templates
import config

from languages import Languages

class Builder:

  def __init__(self,
               languages_path='languages',
               templates_path='templates',
               input_path    ='input',
               output_path   ='output',
               
               language='en-us'):
    self.path = {}
    self.path['languages'] = languages_path
    self.path['templates'] = templates_path
    self.path['input']     = input_path
    self.path['output']    = output_path

    self.language = language
    self.languages = Languages(self.path['languages'], language)
    
  def get_site_name(self):
    return self.languages.get('site-name')

  def build_about(self):
    p = AboutPage(self)
    p.build()
  
  def build(self, language=None):
    self.templates = Templates(self.path['templates'])
    self.languages.set_default_language(language or self.language)

    self.build_about()
    
if __name__ == '__main__':
  b = Builder(language='en-us')
  b.build()
