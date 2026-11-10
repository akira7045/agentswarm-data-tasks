import argparse
import re
import sys

TOKEN_RE = re.compile(r"[+-]?[0-9]{1,100}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ledger.py",
        description="Sum or count signed integer tokens.",
    )
    parser.add_argument(
        "--mode",
        choices=("sum", "count"),
        default="sum",
        help="sum the token values (default) or count valid tokens",
    )
    parser.add_argument(
        "tokens",
        nargs="*",
        metavar="TOKEN",
        help="integer token matching [+-]?[0-9]{1,100}",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "count":
        for token in args.tokens:
            if TOKEN_RE.fullmatch(token) is None:
                parser.error("invalid integer token: %r" % (token,))
        sys.stdout.write("%d\n" % len(args.tokens))
        return 0

    total = 0
    for token in args.tokens:
        if TOKEN_RE.fullmatch(token) is None:
            parser.error("invalid integer token: %r" % (token,))
        total += int(token)
    sys.stdout.write("%d\n" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
