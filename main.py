import argparse
from revenue.processor import handle_source as revenue_handler

parser = argparse.ArgumentParser()
parser.add_argument("command", help="The command to run this program, e.g. revenue")
parser.add_argument("--path", type=str, help="File or directory path to work on")


def main():
    args = parser.parse_args()
    if args.command == "revenue":
        path = args.path
        revenue_handler(path)
    else:
        print(args)


if __name__ == "__main__":
    main()