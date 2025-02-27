#!/bin/bash

install=false

while getopts ":i" opt; do
  case $opt in
    i)
      install=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

cd "$( dirname "${BASH_SOURCE[0]}" )"

python3 -m venv ./venv

source ./venv/bin/activate

if [ "$install" = true ]; then
  pip install requests dotenv google-api-python-client google-auth-oauthlib google-auth-httplib2
fi

chmod +x ./clist-gcal.py

./clist-gcal.py

deactivate