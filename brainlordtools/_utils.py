import argparse
import shutil

def copy_file(args):
    try:
        shutil.copy(args.source_file, args.dest_file)
        print(f"Successfully copied to {args.dest_file}")
    except Exception as e:
        print(f"Copy failed: {e}")

parser = argparse.ArgumentParser(description="Utilities")
parser.set_defaults(func=None)
subparsers = parser.add_subparsers(dest="command")
p_copy_file = subparsers.add_parser('file_copy', help='File COPY')
p_copy_file.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
p_copy_file.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
p_copy_file.set_defaults(func=copy_file)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
