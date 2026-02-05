__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse, deepl, boto3
from brainlordutils.utils import GAME_PARSERS

def amazon_translate_processor(args) -> None:
    source_dump_path = args.source
    destination_dump_path = args.destination
    game = args.game
    client = boto3.client('translate')
    parse_dump_func = GAME_PARSERS.get(game, GAME_PARSERS['default'])
    with open(destination_dump_path, 'a', encoding='utf-8') as f:
        dump = parse_dump_func(source_dump_path)
        for _, value in dump.items():
            text, ref = value
            translate_response = client.translate_text(
                Text=text,
                SourceLanguageCode='en',
                TargetLanguageCode='it',
                Settings={
                    'Formality': 'INFORMAL'
                }
            )
            translated_text = translate_response['TranslatedText']
            f.write(f"{ref}\r\n{translated_text}")

def deepl_translate_processor(args) -> None:
    source_dump_path = args.source
    destination_dump_path = args.destination
    translator = deepl.Translator(auth_key)
    try:
        translator.translate_document_from_filepath(
            source_dump_path,
            destination_dump_path,
            target_lang="IT",
            formality="more"
        )
    except deepl.DocumentTranslationException as error:
        doc_id = error.document_handle.id
        doc_key = error.document_handle.key
        print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
    except deepl.DeepLException as error:
        print(error)

parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
p_amazon_translate_dump = subparsers.add_parser('amazon', help='Translate a dump using Amazon service')
p_amazon_translate_dump.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
p_amazon_translate_dump.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
p_amazon_translate_dump.add_argument('-g', '--game', action='store', dest='game', required=False, help='Optional: Game ID(s) to use for custom parsing logic')
p_amazon_translate_dump.set_defaults(func=amazon_translate_processor)
p_deepl_translate_dump = subparsers.add_parser('deepl', help='Translate a dump using Deepl service')
p_deepl_translate_dump.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
p_deepl_translate_dump.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
p_deepl_translate_dump.set_defaults(func=deepl_translate_processor)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
