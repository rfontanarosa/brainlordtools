__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from brainlordtools.rhutils.parsers import GAME_PARSERS

def diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game) -> None:
    parse_dump_func = GAME_PARSERS.get(game, GAME_PARSERS['default'])
    entries1 = parse_dump_func(source1_dump_path)
    entries2 = parse_dump_func(source2_dump_path)
    with open(destination_dump_path, 'w', encoding='utf-8') as f:
        for entry_id, (text2, ref2) in entries2.items():
            text1, _ = entries1.get(entry_id, (None, None))
            if text1 is None or text1 != text2:
                f.write(f"{ref2}\r\n{text2}")
