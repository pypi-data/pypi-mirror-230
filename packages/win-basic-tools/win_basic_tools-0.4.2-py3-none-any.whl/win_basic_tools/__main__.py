import sys

from .__init__ import Ls

args = sys.argv[1:]

# notice useless parameters
if len(args) > 2:
    print(f'Ignored {args[2:]} arg(s)')
    args = args[:2]
if len(args) == 2 and not args[0].startswith('-'):
    print('Try: python -m win_basic_tools -acilm path')

Ls(*args).echo(0)
