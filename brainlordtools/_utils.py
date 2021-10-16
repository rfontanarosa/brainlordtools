import shutil

def file_copy(args):
    source_file = args.source_file
    dest_file = args.dest_file
    shutil.copy(source_file, dest_file)

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
file_copy_parser = subparsers.add_parser('file_copy', help='File COPY')
file_copy_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
file_copy_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
file_copy_parser.set_defaults(func=file_copy)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
