__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, re

resources_path = '../resources/sd3'
dump_path = os.path.join(resources_path, 'magno')
empty_path = os.path.join(dump_path, 'empty')

fullpath1 = os.path.join(dump_path, 'Bank0_ita.txt')
fullpath2 = os.path.join(empty_path, 'Bank0_ita.txt')

with open(fullpath1, 'rb') as f1, open(fullpath2, 'w') as f2:
    for line in f1:
      if '<INI ' in line:
        f2.write(line)

fullpath1 = os.path.join(dump_path, 'Bank2_ita.txt')
fullpath2 = os.path.join(empty_path, 'Bank2_ita.txt')

with open(fullpath1, 'rb') as f1, open(fullpath2, 'w') as f2:
    for line in f1:
      if '<INI ' in line:
        f2.write(line)

fullpath1 = os.path.join(dump_path, 'Bank1_ita.txt')
fullpath2 = os.path.join(empty_path, 'Bank1_ita.txt')

with open(fullpath1, 'rb') as f1, open(fullpath2, 'w') as f2:
    for line in f1:
      if '<INI ' in line:
        f2.write(line)

fullpath1 = os.path.join(dump_path, 'Items_ita.txt')
fullpath2 = os.path.join(empty_path, 'Items_ita.txt')

with open(fullpath1, 'rb') as f1, open(fullpath2, 'w') as f2:
    for line in f1:
      if '<INI ' in line:
        f2.write(line)
      elif '<END>' in line:
        f2.write('a<END>')
        f2.write('\r')
        f2.write('\n')
        f2.write('\r')
        f2.write('\n')
