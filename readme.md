# Script to add contests on Clist to Google Calendar

## Setup

1. Clone repository

2. Add this to ~/.bashrc (or ~/.zshrc or whatever your shell config file is):

```bash
alias clist-gcal="bash /path/to/clist-gcal.sh"
```

3. Run `source ~/.bashrc` (or corresponding shell config file) or restart terminal

4. Command `clist-gcal` will be available globally

5. Run with `clist-gcal -i` to install dependencies

## Google Calendar API setup

1. Create your own google cloud project and enable google calendar api

2. Go to https://console.cloud.google.com/apis/credentials

3. Create credentials and download credentials.json

4. Put credentials.json in the same directory as clist-gcal.sh

## Clist API setup

1. Go to https://clist.by/

2. Create an account and get an API key from https://clist.by/api/v4/doc/

3. Create a .env file in the same directory as clist-gcal.sh and add your username and API key:

```bash
CLIST_USERNAME=<your_username>
CLIST_API_KEY=<your_api_key>
```

## Usage

```bash
clist-gcal
```
