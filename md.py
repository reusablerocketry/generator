
import markdown
import util
import log

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.util import etree

################################################
# IMAGE LISTINGS
################################################

class ImageExtension(Extension):
  
  def extendMarkdown(self, md, md_globals):
    
    treeprocessor = ImageTreeprocessor(md)
    md.treeprocessors['images'] = treeprocessor

class ImageTreeprocessor(Treeprocessor):
  
  def children(self, element):
    children = []

    for node in element:
      children.append(node)
      if len(node):
        children.extend(self.children(node))
    return children

  def run(self, root):
    self.markdown.images = []
    
    for element in self.children(root):
      if element.tag == 'img':
        self.markdown.images.append(element.attrib['src'])

################################################
# TERM LISTINGS
################################################

class LinkExtension(Extension):

  def extendMarkdown(self, md, md_globals):
    
    treeprocessor = LinkTreeprocessor(md)
    md.treeprocessors['links'] = treeprocessor

class LinkTreeprocessor(Treeprocessor):
  
  def children(self, element):
    children = []

    for node in element:
      children.append(node)
      if len(node):
        children.extend(self.children(node))
    return children

  def redirect_term(self, url):
    term = self.markdown.builder.get_term(util.to_slug(url))
    if term:
      return term.get_term_link()
    else:
      log.warning('redirecting nonexistent term "' + url + '" to Wikipedia', self.markdown.requester)
      return self.redirect_wikipedia(url)

  def redirect_wikipedia(self, url):
    return 'https://en.wikipedia.org/wiki/' + util.to_wiki(url)

  def redirect(self, element):
    href = element.attrib['href']
    both = href.split(':', 1)
    link_type = both[0]

    if len(both) == 1:
      url = element.text
    else:
      url = both[1]
      
    if link_type == 'term':
      href = self.redirect_term(url)
    elif link_type in ['wikipedia', 'wiki']:
      href = self.redirect_wikipedia(url)
      
    element.attrib['href'] = href
    
  def run(self, root):
    self.markdown.links = []
    
    for element in self.children(root):
      if element.tag == 'a':
        self.redirect(element)

################################################
# MARKDOWN
################################################

class Markdown:

  def __init__(self, builder, content='', requester=None):
    self.builder = builder

    self.requester = requester
    self.content = content
    self.md = None
    self.html = ''
    
    self.converted = False

  def set_content(self, content):
    self.content = content
    self.converted = False

  def convert(self):
    if self.converted: return
    self.converted = True
    
    self.md = markdown.Markdown(extensions=[ImageExtension(), LinkExtension()], output_format='html5')
    self.md.builder = self.builder
    self.md.requester = self.requester
    self.html = self.md.convert(self.content)

  def get_html(self):
    self.convert()
    return self.html
