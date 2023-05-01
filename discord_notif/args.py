import argparse
import json


def _get_options() -> str:
    with open("/etc/discord.json", "r") as f:
        options: dict = json.load(f)
    return f'{{{", ".join(options.keys())}}}'


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a message to discord")
    try:
        options = _get_options()
    except:
        options = ""
    parser.add_argument(
        "-o",
        "--option",
        help=f"Option to send to discord webhook {options}",
        required=False,
        type=str,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="File to send to discord webhook",
        required=False,
        type=str,
        default=None,
    )
    parser.add_argument(
        "-m",
        "--message",
        help="Message to send to discord webhook",
        required=False,
        type=str,
    )
    parser.add_argument(
        "-s",
        "--status",
        help="Status of the script to send to discord webhook",
        required=False,
        type=int,
        default=None,
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Title of the message to send to discord webhook",
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "-u",
        "--url",
        help="URL of the webhook to send to",
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "-l",
        "--log",
        help="log file to output to",
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Print version and exit",
        required=False,
        action="store_true",
        default=False,
    )
    return parser.parse_args()
