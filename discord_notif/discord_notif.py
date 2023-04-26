#!/usr/bin/env python
import json
import os
from datetime import datetime

import sai_logging as log
from discord_webhook import DiscordEmbed, DiscordWebhook


def _setup_log() -> log.Logger:
    path = "/var/log/discord_notify.log"
    try:
        logging = log.Logger(
            log_file_name=path,
            log_level=log.INFO,
        )
    except (PermissionError, FileNotFoundError):
        path = "./discord_notify.log"
        logging = log.Logger(
            log_file_name=path,
            log_level=log.INFO,
        )

    return logging


def _filter_message(message: str) -> str:
    import re

    return re.sub(r"\x1b\[[0-9;]*m", "", message)


def _get_url(option: str) -> str:
    with open("/etc/discord.json", "r") as f:
        urls: dict = json.load(f)
    try:
        return urls[option.lower()]
    except KeyError:
        raise KeyError(f"option {option} not found in /etc/discord.json")


def _build_webhook(option: str, file: str, pass_url: str) -> DiscordWebhook:
    if not pass_url:
        url = _get_url(option)
    else:
        url = pass_url
    webhook = DiscordWebhook(url=url, rate_limit_retry=True)
    if file:
        with open(file, "rb") as f:
            webhook.add_file(file=f.read(), filename=file)
    return webhook


def _build_embed(option: str, title: str, status: int, message: str) -> DiscordEmbed:
    if option != "alert":
        if status == 0:
            color = 65280  # green
            stat = "```diff\n+success```"
        elif not status:
            color = 8421504  # gray
            stat = None
        else:
            color = 16711680  # red
            stat = "```diff\n-failure```"
    else:
        color = 16776960
        stat = "alert"

    message_split = None
    if len(message) > 1024 and title != "login notification":
        message = message.replace("```bash", "").replace("```", "")
        # split message into multiple fields
        message_split = []
        counter = 0
        while len(message) > 0:
            message_split.append(
                {
                    "name": f"output ({counter})",
                    "value": "```bash\n" + message[:1012] + "```",
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
                    value = f"```json\n{value}\n```"
                except TypeError:
                    pass
            fields.append({"name": key, "value": value})
        fields.append(
            {
                "name": "time (cdt)",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
        )

    return DiscordEmbed(
        title=title,
        fields=fields,
        color=color,
        timestamp=datetime.now().astimezone().isoformat(),
    )


def _build_message(message: str) -> str:
    return f"```bash\n{message}\n```"


def _send_message(webhook: DiscordWebhook, embed: DiscordEmbed):
    webhook.add_embed(embed)
    return webhook.execute()


def send_message(
    message: str,
    option: str | None = None,
    status: int | None = None,
    title: str | None = None,
    file: str | None = None,
    filter: bool = False,
    url: str | None = None,
    logging: log.Logger | None = None,
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
        url {str} -- Url to send to discord webhook (default: {None})
        logging {log.Logger} -- Logger to use (default: {None})

    Returns:
        str -- Status of the message sent to discord webhook"""
    try:
        if not logging:
            logging = _setup_log()

        if url: 
            logging.info(f'Sending to discord webhook: "{url}"')
        elif option:
            logging.info(f'Sending to discord webhook: "{option}"')
        else:
            logging.error("no option selected and no url passed")
            raise ValueError("no option selected and no url passed")

        if file and not os.path.isfile(file):
            logging.error(f"File {file} does not exist")
            raise FileNotFoundError(f"File {file} does not exist")

        if not message:
            logging.error("No message to send to discord")
            raise ValueError("No message to send to discord")

        if filter:
            message = _filter_message(message)

        if title != "login notification":
            message = _build_message(message)
        webhook = _build_webhook(option, file, url)
        embed = _build_embed(option, title, status, message)
        send_status = _send_message(webhook, embed)

        if send_status.status_code == 200:
            logging.info(f"Message sent to discord webhook: {send_status}")
        elif send_status.status_code == 429:
            logging.error(f"Discord webhook rate limit reached: {send_status}")
        elif send_status.status_code == 400:
            logging.error(f"Discord webhook bad request: {send_status}")
        else:
            logging.error(f"Discord webhook error: {send_status}")

        return send_status
    except Exception as e:
        logging.error(f"error sending message to discord webhook -> {e}")
        raise e
