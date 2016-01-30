
import os

# input_path:
# config.input + input_root + input_filename

# output_path:
# config.output + output_root + output_filename

# final_path:
# '/' + output_root + '/'

# final_path(domain):
# config.domain + final_path

class Path:

  def __init__(self, builder,
               input_filename='', output_filename='',
               input_root='', output_root='',
               input_ext='', output_ext=''):
    
    self.builder = builder
    
    self.input_filename = input_filename
    self.input_root = input_root
    self.input_ext = input_ext
    
    self.output_filename = output_filename
    self.output_root = output_root
    self.output_ext = output_ext

  ########################
  # SET FILENAMES
  ########################
    
  def set_input_filename(self, filename):
    self.input_filename = os.path.splitext(filename)[0]
    self.input_ext = os.path.splitext(filename)[1]
    
  def set_output_filename(self, filename):
    self.output_filename = os.path.splitext(filename)[0]
    self.output_ext = os.path.splitext(filename)[1]

  ########################
  # SET PATHS
  ########################
    
  def set_input_path(self, path):
    split = os.path.split(path)
    self.input_root = split[0]
    self.set_input_filename(split[1])
    
  def set_output_path(self, path):
    split = os.path.split(path)
    self.output_root = split[0]
    self.set_output_filename(split[1])
    
  # returns a duplicate of self
  def copy():
    return Path(self.builder,
                self.input_filename, self.output_filename,
                self.input_root, self.output_root,
                self.input_ext, self.output_ext)
        
  def get_input_path(self, filename=''):
    return os.path.join(self.builder.path['input'],
                        self.input_root,
                        (filename or self.input_filename) + self.input_ext)

  def get_output_path(self, filename=''):
    return os.path.join(self.builder.path['output'],
                        self.output_root,
                        (filename or self.output_filename) + self.output_ext)
  
  def get_link_path(self, filename=''):
    return '/' + os.path.join(self.output_root,
                              (filename or self.output_filename) + self.output_ext)
