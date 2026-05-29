__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os
import re

# SMRPG: dialogues occupy ids 1..4096 (block 1), battle dialogues start here.
SMRPG_BATTLE_ID_OFFSET = 4097

def parse_metadata(text: str) -> dict:
  matches = re.findall(r'(\w+)=([^\s\]]+)', text)
  return dict(matches)

def _parse_dump(file_path: str) -> dict:
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    current_id = None
    temp_text = []
    for line in f:
      if line.startswith('[ID='):
        if current_id is not None:
          buffer[current_id][0] = "".join(temp_text)[:-2]
        metadata = parse_metadata(line)
        current_id = metadata.get('ID')
        if current_id is not None:
          buffer[current_id] = ['', line.strip()]
          temp_text = []
      elif current_id is not None:
        temp_text.append(line)
    if current_id is not None:
      buffer[current_id][0] = "".join(temp_text)[:-2]
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

def _parse_smrpg_dump(file_path: str) -> dict:
  """Parse a Super Mario RPG dump exported in Lazy Shell format.

  Each line is `{INDEX}\\ttext`. The block and the id offset are derived from
  the filename: dialogues -> block 1 (id = index + 1), battleDialogues ->
  block 2 (id = index + 4097). The ref is emitted as metadata so the generic
  import loop can pick up ID and BLOCK.
  """
  is_battle = 'battle' in os.path.basename(file_path).lower()
  block = 2 if is_battle else 1
  id_offset = SMRPG_BATTLE_ID_OFFSET if is_battle else 1
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
      if '\t' not in line:
        continue
      ref_part, text = line.split('\t', 1)
      index = ref_part.strip().strip('{}')
      entry_id = int(index) + id_offset
      buffer[entry_id] = [text.rstrip('\r\n'), f'[ID={entry_id} BLOCK={block}]']
  return buffer

GAME_PARSERS = {
  'soe': _parse_soe_dump,
  'starocean': _parse_starocean_dump,
  'smrpg': _parse_smrpg_dump,
  'default': _parse_dump
}
