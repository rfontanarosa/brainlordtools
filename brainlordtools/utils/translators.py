__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import boto3
import deepl

from brainlordutils.utils import GAME_PARSERS

def amazon_translate_processor(source_dump_path, destination_dump_path, game) -> None:
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

def deepl_translate_processor(source_dump_path, destination_dump_path, auth_key) -> None:
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
