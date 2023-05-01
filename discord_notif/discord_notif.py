#!/usr/bin/env python3
import json
import os
from datetime import datetime

import sai_logging as logging
from discord_webhook import DiscordEmbed, DiscordWebhook

from .err import SendError


def _setup_log() -> logging.Logger:
    path = "/var/log/discord_notify.log"
    try:
        log = logging.Logger(
            log_file=path,
            log_stdout=False,
        )
    except (PermissionError, FileNotFoundError):
        path = "./discord_notify.log"
        log = logging.Logger(
            log_file=path,
            log_stdout=False,
        )
    return log


def _get_url(option: str) -> str:
    with open("/etc/discord.json", "r") as f:
        urls: dict = json.load(f)
    try:
        return urls[option.lower()]
    except KeyError as exc:
        raise KeyError(f"option {option} not found in /etc/discord.json") from exc


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
            stat = "```ansi\n\033[0;32msuccess\033[0m\n```"
        elif not status:
            color = 8421504  # gray
            stat = None
        else:
            color = 16711680  # red
            stat = "```ansi\n\033[31;20mfail\033[0m\n```"
    else:
        color = 16776960
        stat = "alert"

    message_split = None
    if len(message) > 1024 and title != "login notification":
        message = message.replace("```ansi", "").replace("```", "")
        # split message into multiple fields
        message_split = []
        counter = 0
        while len(message) > 0:
            message_split.append(
                {
                    "name": f"output ({counter})",
                    "value": "```ansi\n" + message[:1012] + "```",
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
    return f"```ansi\n{message}\n```"


def _send_message(webhook: DiscordWebhook, embed: DiscordEmbed):
    webhook.add_embed(embed)
    return webhook.execute()


def send_message(
    message: str,
    option: str | None = None,
    status: int | None = None,
    title: str | None = None,
    file: str | None = None,
    url: str | None = None,
    log: logging.Logger | None = None,
) -> str:
    """Send message to discord webhook

    `option` and `url` are mutually exclusive: if `url` is passed, `option` is ignored,
    however one of them **must** be given

    Arguments:
        :param message {str} -- Message to send to discord webhook
    Keyword Arguments:
        :param option {str} -- Option to send to discord webhook
        :param status {str} -- Status of the script to send to discord webhook (default: {None})
        :param title {str} -- Title of the message to send to discord webhook (default: {None})
        :param file {str} -- File to send to discord webhook (default: {None})
        :param url {str} -- Url to send to discord webhook (default: {None})
        :param logging {log.Logger} -- Logger to use (default: {None})

    Returns:
        str -- Status of the message sent to discord webhook"""
    try:
        if not log:
            log = _setup_log()

        if url:
            log.info(f'Sending to discord webhook: "{url}"')
        elif option:
            log.info(f'Sending to discord webhook: "{option}"')
        else:
            log.error("no option selected and no url passed")
            raise ValueError("no option selected and no url passed")

        if file and not os.path.isfile(file):
            log.error(f"File {file} does not exist")
            raise FileNotFoundError(f"File {file} does not exist")

        if not message:
            log.error("No message to send to discord")
            raise ValueError("No message to send to discord")

        if title != "login notification":
            message = _build_message(message)
        webhook = _build_webhook(option, file, url)
        embed = _build_embed(option, title, status, message)
        send_status = _send_message(webhook, embed)

        match send_status.status_code:
            case 200 | 204:
                log.info(f"Message sent to discord webhook: {send_status}")
            case 429:
                raise SendError("Discord webook rate limit reached", 429)
            case 400:
                raise SendError("Discord webhook bad request", 400)
            case _:
                raise SendError("Discord webhook error", send_status.status_code)

        return send_status
    except SendError as exc:
        log.error(f"{exc.code} -> {exc.message}")
        raise SendError(f'{exc.code} -> {exc.message}') from exc
    except Exception as exc:
        log.error(f"error sending message to discord webhook -> {exc}")
        raise Exception(f"error sending message to discord webhook -> {exc}") from exc
