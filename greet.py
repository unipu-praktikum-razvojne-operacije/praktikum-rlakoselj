"""A tiny CLI tool that shows the command / subcommand / options pattern."""
import argparse
import sys


def cmd_hello(args: argparse.Namespace) -> int:
    greeting = f"Hello, {args.name}!"
    print(greeting.upper() if args.shout else greeting)
    return 0


def cmd_bye(args: argparse.Namespace) -> int:
    for _ in range(args.times):
        print(f"Goodbye, {args.name}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="greet", description="Greets people from the command line.")
    parser.add_argument("--version", action="version", version="greet 0.0.1")
    subcommands = parser.add_subparsers(dest="command", required=True)

    hello = subcommands.add_parser("hello", help="say hello")
    hello.add_argument("name", help="who to greet")
    hello.add_argument("-s", "--shout", action="store_true", help="print in upper case")
    hello.set_defaults(handler=cmd_hello)

    bye = subcommands.add_parser("bye", help="say goodbye")
    bye.add_argument("name", help="who to say goodbye to")
    bye.add_argument("-n", "--times", type=int, default=1, help="how many times (default: 1)")
    bye.set_defaults(handler=cmd_bye)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())