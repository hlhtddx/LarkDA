import os

# A mapping of the subcommand name to the class that implements it.
all_commands = {}

my_dir = os.path.dirname(__file__)
for py in os.listdir(my_dir):
  if py in ('__init__.py', 'command.py'):
    continue

  if py.endswith('.py'):
    name = py[:-3]

    clsn = name.capitalize()
    while clsn.find('_') > 0:
      h = clsn.index('_')
      clsn = clsn[0:h] + clsn[h + 1:].capitalize()

    mod = __import__(__name__,
                     globals(),
                     locals(),
                     ['%s' % name])
    mod = getattr(mod, name)
    try:
      cmd = getattr(mod, clsn)
    except AttributeError:
      raise SyntaxError('%s/%s does not define class %s' % (
          __name__, py, clsn))

    name = name.replace('_', '-')
    cmd.NAME = name
    all_commands[name] = cmd
