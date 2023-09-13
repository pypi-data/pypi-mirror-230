import sys

import requests
import os
import json
import logging
from pathlib import Path
from os.path import exists
import typer

if 'REMOTIVE_CLOUD_HTTP_LOGGING' in os.environ:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
global baseurl
base_url = "https://cloud.remotivelabs.com"

if 'REMOTIVE_CLOUD_BASE_URL' in os.environ:
    base_url = os.environ['REMOTIVE_CLOUD_BASE_URL']

# if 'REMOTIVE_CLOUD_AUTH_TOKEN' not in os.environ:
#    print('export REMOTIVE_CLOUD_AUTH_TOKEN=auth must be set')
#    exit(0)

# token = os.environ["REMOTIVE_CLOUD_AUTH_TOKEN"]
# headers = {"Authorization": "Bearer " + token}

headers = {}
org = ""


def ensure_auth_token():

    #if 'REMOTIVE_CLOUD_ORGANISATION' not in os.environ:
    #    print('You must first set the organisation id to use: export REMOTIVE_CLOUD_ORGANISATION=organisationUid')
    #    raise typer.Exit()
    global org
    #org = os.environ["REMOTIVE_CLOUD_ORGANISATION"]

    if not exists(str(Path.home()) + "/.config/.remotive/cloud.secret.token"):
        print("Access token not found, please login first")
        raise typer.Exit()

    f = open(str(Path.home()) + "/.config/.remotive/cloud.secret.token", "r")
    token = f.read()
    os.environ['REMOTIVE_CLOUD_AUTH_TOKEN'] = token
    global headers
    headers = {
        'Authorization': "Bearer " + token.strip(),
        'User-Agent': 'RemotiveCli 0.0.1alphax',
    }


def handle_get(url, params={},return_response: bool = False):
    ensure_auth_token()
    r = requests.get(f'{base_url}{url}', headers=headers, params=params)

    if return_response:
        return r

    if r.status_code == 200:
        print(json.dumps(r.json()))
    else:
        sys.stderr.write(f'Got status code: {r.status_code}\n')
        sys.stderr.write(r.text + "\n")
        typer.Exit(1)


def has_access(url, params={}):
    ensure_auth_token()
    r = requests.get(f'{base_url}{url}', headers=headers, params=params)
    if r.status_code == 401:
        return False
    else:
        return True


def handle_delete(url, params={}, quiet=False, success_msg="Successfully deleted"):
    ensure_auth_token()
    r = requests.delete(f'{base_url}{url}', headers=headers, params=params)
    if r.status_code == 200:
        if quiet == False:
            print(json.dumps(r.json()))
    if r.status_code == 204:
        if quiet == False:
            sys.stderr.write(f'{success_msg}\n')
    else:
        print(f'Got status code: {r.status_code}')
        print(r.text)
        typer.Exit(1)

def handle_post(url, body=None, params={}, return_response: bool = False):
    ensure_auth_token()
    headers["content-type"] = "application/json"
    r = requests.post(f'{base_url}{url}', headers=headers, params=params, data=body)

    if return_response:
        return r

    if r.status_code == 200:
        print(r.text)
        # print(json.dumps(r.json()))
    elif r.status_code == 204:
        print(r.status_code)
    else:
        print(f'Got status code: {r.status_code}')
        print(r.text)
        typer.Exit(1)

def handle_put(url, body=None, params={}, return_response: bool = False):
    ensure_auth_token()
    headers["content-type"] = "application/json"
    r = requests.put(f'{base_url}{url}', headers=headers, params=params, data=body)

    if return_response:
        return r

    if r.status_code == 200:
        print(r.text)
        # print(json.dumps(r.json()))
    elif r.status_code == 204:
        print(r.status_code)
    else:
        print(f'Got status code: {r.status_code}')
        print(r.text)
        typer.Exit(1)
