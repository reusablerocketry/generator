
import markdown

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
# MARKDOWN
################################################

class Markdown:

  def __init__(self, builder, content=''):
    self.builder = builder
    
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
    
    self.md = markdown.Markdown(extensions=[ImageExtension()], output_format='html5')
    self.html = self.md.convert(self.content)

  def get_html(self):
    self.convert()
    return self.html
