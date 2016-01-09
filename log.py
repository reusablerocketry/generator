
in_progress = False

# clear progress
def cp():
  global in_progress
  if in_progress:
    print('')
    in_progress = False

def rq(requester=''):
  if requester:
    return ' (requested by "' + requester + '")'
  return ''

def error(message, requester=''):
  cp()
  print('!! ' + message + rq(requester))
  exit()

def warning(message, requester=''):
  cp()
  print('!  ' + message + rq(requester))

def info(message, requester=''):
  cp()
  print('-  ' + message + rq(requester))

# progress
# foobar... html... json... done.

def progress(name):
  global in_progress
  cp()
  in_progress = True
  print('   ' + name + '... ', end='')
  
def progress_step(step):
  print(step + '... ', end='')
  
def progress_done():
  global in_progress
  in_progress = False
  print('done.')
