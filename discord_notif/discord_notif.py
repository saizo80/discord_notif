#!/usr/bin/env python3
from typing import Tuple
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from datetime import datetime
import sys
import argparse
import sai_logging as log
import json


def __get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a message to discord")
    parser.add_argument(
        "-o",
        "--option",
        help="Option to send to discord webhook",
        required=False,
        choices=["cron", "alert", "signout", "test"],
    )
    parser.add_argument(
        "-f", "--file", help="File to send to discord webhook", required=False
    )
    parser.add_argument(
        "--filter",
        help="Filter the message to remove cli formatting",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Log file to print output to",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-m",
        "--message",
        help="Message to send to discord webhook",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--status",
        help="Status of the script to send to discord webhook",
        required=False,
        type=int,
        default=None
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Title of the message to send to discord webhook",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-u",
        "--url",
        help="URL of the webhook to send to",
        required=False,
        default=None,
        type=str,
    )
    return parser.parse_args()


def __get_script_input() -> str:
    if not sys.stdin.isatty():
        temp_input = sys.stdin.read()
        if not temp_input:
            return None
        return temp_input if not temp_input[-1] == "\n" else temp_input[:-1]
    return None


def __setup_log() -> None:
    path = "/var/log/discord_notify.log"
    global logging
    try:
        logging = log.Logger(
            log_file_name=path,
            log_level=log.INFO,
        )
    except PermissionError:
        path = "./discord_notify.log"
        logging = log.Logger(
            log_file_name=path,
            log_level=log.INFO,
        )
    except FileNotFoundError:
        path = "./discord_notify.log"
        logging = log.Logger(
            log_file_name=path,
            log_level=log.INFO,
        )


def __filter_message(message: str) -> Tuple[str, str]:
    import re

    original_message = message
    return (re.sub(r"\x1b\[[0-9;]*m", "", message), original_message)


def __get_url(option: str) -> str:
    with open("/etc/discord.json", "r") as f:
        urls: dict = json.load(f)
    if option == "cron":
        return urls.get("discord_cron_url")
    elif option == "alert":
        return urls.get("discord_alert_url")
    elif option == "signout":
        return urls.get("discord_signout_url")
    elif option == "test":
        return urls.get("discord_test_url")
    else:
        logging.error("No option selected")
        sys.exit(1)


def __build_webhook(option: str, file: str, pass_url: str) -> DiscordWebhook:
    if not pass_url:
        url = __get_url(option)
    else:
        url = pass_url
    webhook = DiscordWebhook(url=url, rate_limit_retry=True)
    if file:
        with open(file, "rb") as f:
            webhook.add_file(file=f.read(), filename=file)
    return webhook


def __build_embed(option: str, title: str, status: int, message: str) -> DiscordEmbed:
    if option != "alert":
        if status == 0:
            color = 65280 #green
            stat = "```diff\n+success```"
        elif not status:
            color = 8421504 #gray
            stat = None
        else:
            color = 16711680 #red
            stat = "```diff\n-failure```"
    else:
        color = 16776960
        stat = "alert"
    
    message_split = None
    if len(message) > 1024 and title != "login notification":
        message = message.replace('```bash', '').replace('```', '')
        # split message into multiple fields
        message_split = []
        counter = 0
        while len(message) > 0:
            message_split.append(
                {
                    "name": f"output ({counter})",
                    "value": '```bash\n' + message[:1012] + '```',
                }
            )
            message = message[1012:]
            counter += 1

    title = title if title else option
    if title != "login notification":
        if message_split is None:
            fields = [
                {
                    "name": "output",
                    "value": message,
                },
                {
                    "name": "time (cdt)",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
            ]
        else:
            fields = message_split
            fields.append(
                {
                    "name": "time (cdt)",
                    "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                }
            )
        if stat is not None and stat != "alert":
            fields.insert(-1, {"name": "status", "value": stat})
    else:
        message_json = json.loads(message)
        fields = []
        for key, value in message_json.items():
            if key != "ipinfolink":
                try:
                    value = json.dumps(value, indent=2)
                    value = f'```json\n{value}\n```'
                except TypeError:
                    pass
            fields.append({"name": key, "value": value})
        fields.append({"name": "time (cdt)", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})

    return DiscordEmbed(
        title=title,
        fields=fields,
        color=color,
        timestamp=datetime.now().astimezone().isoformat(),
    )


def __build_message(message: str) -> str:
    return f"```bash\n{message}\n```"


def __send_message(webhook: DiscordWebhook, embed: DiscordEmbed):
    webhook.add_embed(embed)
    return webhook.execute()


def send_message(
    message: str,
    option: str,
    status: int = None,
    title: str = None,
    file: str = None,
    filter: bool = False,
    url: str = None,
) -> str:
    """Send message to discord webhook
    Arguments:
        message {str} -- Message to send to discord webhook
        option {str} -- Option to send to discord webhook (choices: cron, alert, signout, test)
    Keyword Arguments:
        status {str} -- Status of the script to send to discord webhook (default: {None})
        title {str} -- Title of the message to send to discord webhook (default: {None})
        file {str} -- File to send to discord webhook (default: {None})
        filter {bool} -- Filter message to remove color (default: {False})

    Returns:
        str -- Status of the message sent to discord webhook"""
    __setup_log()
    logging.info(f'Sending to discord webhook: "{option}"')
    if not option:
        logging.error("No option selected")
        raise ValueError("No option selected")

    if file and not os.path.isfile(file):
        logging.error(f"File {file} does not exist")
        raise FileNotFoundError(f"File {file} does not exist")

    if not message:
        logging.error("No message to send to discord")
        raise ValueError("No message to send to discord")

    if filter:
        (message, original_message) = __filter_message(message)

    if title != "login notification":
        message = __build_message(message)
    webhook = __build_webhook(option, file, url)
    embed = __build_embed(option, title, status, message)
    send_status = __send_message(webhook, embed)

    if send_status.status_code == 200:
        logging.info(f"Message sent to discord webhook: {send_status}")
    elif send_status.status_code == 429:
        logging.error(f"Discord webhook rate limit reached: {send_status}")
    elif send_status.status_code == 400:
        logging.error(f"Discord webhook bad request: {send_status}")
    else:
        logging.error(f"Discord webhook error: {send_status}")

    return send_status


def main() -> None:
    args = __get_arguments()
    __setup_log()
    if args.file and not os.path.isfile(args.file):
        logging.error(f"File {args.file} does not exist")
        sys.exit(1)

    script_input = __get_script_input()
    if not script_input and not args.message:
        logging.error("No message to send to discord")
        sys.exit(1)
    message = script_input if not args.message else args.message

    if args.filter:
        (message, original_message) = __filter_message(message)
        filtered = True
    else:
        filtered = False

    if args.title != "login notification":
        message = __build_message(message)

    webhook = __build_webhook(args.option, args.file, args.url)
    embed = __build_embed(args.option, args.title, args.status, message)
    send_status = __send_message(webhook, embed)

    if send_status.status_code == 200:
        logging.info(f"Message sent to discord webhook: {send_status}")
    elif send_status.status_code == 429:
        logging.error(f"Discord webhook rate limit reached: {send_status}")
    elif send_status.status_code == 400:
        logging.error(f"Discord webhook bad request: {send_status}")
    else:
        logging.error(f"Discord webhook error: {send_status}")
    


if __name__ == "__main__":
    main()
