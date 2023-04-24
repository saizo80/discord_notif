# discord notif

an importable/executable script for sending embedded discord messages via webhook

## about

custom module for sending script output to a discord server.

used for sending cron script output and status.

## installation

`pip install git+https://git.saizo.gay/saizo/discord_notif`

## use

```python
from discord_notif import send_message

status = send_message(
    message='message to send', # required
    option='option', # optional
    status=0, # optional
    title='embed title', # optional
    file='/path/to/attached/file', # optional
    filter=False, # optional
    url='discord webhook url', # optional
)


print(status)
```

while `option` and `url` are both optional, **at least** one should be passed. url takes precedence over option

this draws from a json file at `/etc/discord.json` which should look like

```json
{
    "cron": "url",
    "test": "url",
    "option...": "url"
}
```

## terminal use

the script can also be called from the terminal. the functions are the same, but to see the argument flags use `discord_notif.py -h`

it will give this information:

```txt
usage: discord_notif.py [-h] [-o {cron,alert,signout,test}] [-f FILE] [--filter] [-l LOG] [-m MESSAGE] [-s STATUS] [-t TITLE] [-u URL]

Send a message to discord

optional arguments:
  -h, --help            show this help message and exit
  -o {cron,alert,signout,test}, --option {cron,alert,signout,test}
                        Option to send to discord webhook
  -f FILE, --file FILE  File to send to discord webhook
  --filter              Filter the message to remove cli formatting
  -l LOG, --log LOG     Log file to print output to
  -m MESSAGE, --message MESSAGE
                        Message to send to discord webhook
  -s STATUS, --status STATUS
                        Status of the script to send to discord webhook
  -t TITLE, --title TITLE
                        Title of the message to send to discord webhook
  -u URL, --url URL     URL of the webhook to send to
```

the message can be specified using the `-m` or `--message` flags, or it can be piped into the script from another script like `script1.sh | discord_notif.py`
