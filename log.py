
in_progress = False

# clear progress
def cp():
  if in_progress:
    print('')

def rq(requester=''):
  cp()
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

# progress
# foobar... html... json... done.

def progress(name):
  cp()
  progress = True
  print('   ' + name + '... ', end='')
  
def progress_step(step):
  print(step + '... ', end='')
  
def progress_done():
  progress = False
  print('done.')
