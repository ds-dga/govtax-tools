import argparse
from revenue.processor import handle_source as revenue_handler

parser = argparse.ArgumentParser()
parser.add_argument("command", help="The command to run this program, e.g. revenue")
parser.add_argument("--path", type=str, help="File or directory path to work on")
parser.add_argument(
    "--print", action=argparse.BooleanOptionalAction, help="Print output to stdout"
)
parser.add_argument(
    "--db", action=argparse.BooleanOptionalAction, help="Save output to database"
)


def main():
    args = parser.parse_args()
    if args.command == "revenue":
        path = args.path
        revenue_handler(path, args=args)
    else:
        print(args)


if __name__ == "__main__":
    main()
