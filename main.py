import argparse
from revenue.processor import handle_source as revenue_handler
from gfmis.converter import handle_gfmis_dir as gfmis_handler

parser = argparse.ArgumentParser()
parser.add_argument("command", help="The command to run this program, e.g. revenue, gfmis")
parser.add_argument("--path", type=str, help="File or directory path to work on")
parser.add_argument('--db', action='store_true')
parser.add_argument('--print', action='store_true')


def main():
    args = parser.parse_args()
    if args.command == "revenue":
        path = args.path
        revenue_handler(path, args=args)
    if args.command == "gfmis":
        path = args.path
        gfmis_handler(path, args=args)
    else:
        print(args)


if __name__ == "__main__":
    main()
