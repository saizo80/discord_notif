#!/usr/bin/env python3
import sys
import sai_logging as logging

from .args import get_arguments
from .discord_notif import send_message



def _get_script_input() -> str:
    if not sys.stdin.isatty():
        temp_input = sys.stdin.read()
        if not temp_input:
            return None
        return temp_input if not temp_input[-1] == "\n" else temp_input[:-1]
    return None

def _setup_log() -> logging.Logger:
    log = logging.Logger()
    return log


def main() -> None:
    args = get_arguments()
    if args.version:
        import pkg_resources

        print(
            "discord_notif version:",
            pkg_resources.get_distribution("discord_notif").version,
        )
        sys.exit(0)
    
    log = _setup_log()

    if not args.message:
        message = _get_script_input()
        if not message:
            log.error("no message provided")
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
            url=args.url,
            log=log,
        )
    except Exception as exc:
        log.error(exc)


if __name__ == "__main__":
    main()
