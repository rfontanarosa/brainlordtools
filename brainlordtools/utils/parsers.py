__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import re

def parse_metadata(text: str) -> dict:
  matches = re.findall(r'(\w+)=([^\s\]]+)', text)
  return dict(matches)

def _parse_dump(file_path: str) -> dict:
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    current_id = None
    for line in f:
      if line.startswith('[ID='):
        metadata = parse_metadata(line)
        current_id = metadata.get('ID')
        if current_id is not None:
          buffer[current_id] = ['', line.strip()]
      elif current_id is not None:
        buffer[current_id][0] += line
  return buffer

def _parse_soe_dump(file_path: str) -> dict:
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    real_id = 1
    current_text = ""
    for line in f:
      if '<End>' in line:
        clean_text = current_text + line.replace('<End>', '')
        buffer[real_id] = [clean_text.strip(), ''] 
        real_id += 1
        current_text = ""
      else:
        current_text += line
  return buffer

def _parse_starocean_dump(file_path: str) -> dict:
  buff = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    current_id = 0
    iterator = iter(f)
    for line in iterator:
      if line.startswith('<HEADER '):
        current_id += 1
        next_line = next(iterator)
        buff[current_id] = ['', line + next_line.strip('\r\n')]
      elif line.startswith('<BLOCK '):
        current_id += 1
        buff[current_id] = ['', line.strip('\r\n')]
      else:
        buff[current_id][0] += line
  return buff

GAME_PARSERS = {
  'soe': _parse_soe_dump,
  'starocean': _parse_starocean_dump,
  'default': _parse_dump
}
