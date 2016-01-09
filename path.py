
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

  def __init__(self, builder, input_filename='', output_filename='', input_root='', output_root=''):
    self.builder = builder
    
    self.input_filename = input_filename
    self.input_root = input_root
    
    self.output_filename = output_filename
    self.output_root = output_root

  # returns a duplicate of self
  def copy():
    return Path(self.builder, self.input_filename, self.output_filename, self.input_root, self.output_root)
        
  def get_input_path(self, filename=''):
    return os.path.join(self.builder.path['input'],
                        self.input_root,
                        filename or self.input_filename)

  def get_output_path(self, filename=''):
    return os.path.join(self.builder.path['output'],
                        self.output_root,
                        filename or self.output_filename)
