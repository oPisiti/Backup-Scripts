#!/usr/bin/python3

import argparse
import os
import requests
import urllib.parse

def notify_me():
    # Parsing command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", required=True, help="Message to be sent", type=str)
    parser.add_argument("-f", help="File containing the bot's API and chat's id", type=str)
    args = parser.parse_args()

    # Attempting to read secrets file
    try:
        user_data = get_data(args.f) if args.f is not None else get_data()
    except KeyError as e:
        print(e)
        return
    except FileNotFoundError:
        print(f'Secrets file not found')
        return

    # Creating url
    message = urllib.parse.quote_plus(args.m)
    telegram_final_url = f"https://api.telegram.org/bot{user_data['API']}/sendMessage?chat_id={user_data['CHAT_ID']}&text={message}"

    # Sending request
    requests.post(telegram_final_url)


def get_data(file_name: str = "secrets.txt") -> dict:
    """
    Reads a file and returns the parsed arguments given keywords.
    Expected fields: "API", "CHAT_ID.
    Must be in format, one per line:
        - FIELD=Data
    """

    # Getting the full path to the file
    file_name = os.path.join(os.path.dirname(__file__), file_name) 

    EXPECTED_FIELDS = ("API", "CHAT_ID")

    with open(file_name, "r") as f:
        secrets = tuple(line.strip("\n") for line in f.readlines())

    user_data = {}

    # Getting API and chat id
    for line in secrets:
        try:
            field, data = line.split("=")
        except ValueError as e:
            raise KeyError(f"Line: '{line}' if not formatted in a supported fashion")
        
        user_data[field.strip()] = data.strip()

    # Checking for required fields
    if not set(EXPECTED_FIELDS).issubset(set(user_data.keys())): 
        raise KeyError(f"Required keys: {EXPECTED_FIELDS}. Got: {tuple(user_data.keys())}")

    return user_data


if __name__ == '__main__':
    notify_me()
