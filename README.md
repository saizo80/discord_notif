# discord notif

an importable/executable script for sending embedded discord messages via webhook

## about

custom module for sending script output to a discord server.

used for sending cron script output and status.

## installation

if you have added git.saizo.gay to your pip index for either user or global (see package [instructions](https://git.saizo.gay/saizo/-/packages/pypi/discord-notif/)):

```bash
pip install discord_notif
```

if you have not then you will need to add it as an extra index in the install statement:

```bash
pip install --extra-index-url https://git.saizo.gay/api/packages/saizo/pypi/simple/ discord_notif
```

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

the script can also be called from the terminal. the functions are the same, but to see the argument flags use `discord_notif -h`

it will give this information:

```txt
usage: discord_notif [-h] [-o OPTION] [-f FILE] [--filter] [-m MESSAGE] [-s STATUS] [-t TITLE] [-u URL] [-V]

Send a message to discord

options:
  -h, --help            show this help message and exit
  -o OPTION, --option OPTION
                        Option to send to discord webhook
  -f FILE, --file FILE  File to send to discord webhook
  --filter              Filter the message to remove cli formatting
  -m MESSAGE, --message MESSAGE
                        Message to send to discord webhook
  -s STATUS, --status STATUS
                        Status of the script to send to discord webhook
  -t TITLE, --title TITLE
                        Title of the message to send to discord webhook
  -u URL, --url URL     URL of the webhook to send to
  -V, --version         Print version and exit
```

the message can be specified using the `-m` or `--message` flags, or it can be piped into the script from another script like `script1.sh | discord_notif`
