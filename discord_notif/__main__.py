#!/usr/bin/env python3
import sys

from .args import get_arguments
from .discord_notif import send_message


def _get_script_input() -> str:
    if not sys.stdin.isatty():
        temp_input = sys.stdin.read()
        if not temp_input:
            return None
        return temp_input if not temp_input[-1] == "\n" else temp_input[:-1]
    return None


def main() -> None:
    args = get_arguments()
    if args.version:
        import pkg_resources

        print(
            "discord_notif version:",
            pkg_resources.get_distribution("discord_notif").version,
        )
        sys.exit(0)
    if not args.message:
        message = _get_script_input()
        if not message:
            print("No message to send to discord")
            sys.exit(1)
    else:
        message = args.message
    try:
        send_message(
            message=message,
            option=args.option,
            status=args.status,
            title=args.title,
            file=args.file,
            filter=args.filter,
            url=args.url,
            logging=None,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
