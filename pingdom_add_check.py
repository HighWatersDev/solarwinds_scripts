import requests
import json
import argparse


url = "https://api.pingdom.com/api/3.1/checks"
with open('secrets/PINGDOM_API', 'r') as secret_file:
    token = secret_file.read()


def arguments():
    parser = argparse.ArgumentParser(
            description="This script will create a new Pingdom uptime check"
        )
    parser.add_argument("-w", "--site", default="Test", help="Website FQDN")
    parser.add_argument("-n", "--name", default="Test", help="Check title")
    parser.add_argument("-s", "--string", help="String to search on the webpage")
    parser.add_argument("-m", "--message", default="Test", help="Custom message to add to the check")
    parser.add_argument("-u", "--user", default="Test", help="Users to assign to the check")
    parsed_args = parser.parse_args()
    return parsed_args


def add_check(site, string, name, message, user_ids):

    body = json.dumps({
        'name': name,
        'type': 'http',
        'host': site,
        'resolution': 1,
        'sendnotificationwhendown': 6,
        'notifyagainevery': 0,
        'notifywhenbackup': True,
        'userids': user_ids,
        'encryption': True,
        'shouldcontain': string,
        'verify_certificate': True,
        'ssl_down_days_before': 7,
        'port': 443,
        'custom_message': message
    })

    headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {token}'
    }

    try:
        create_check = requests.post(url, headers=headers, data=body)
    except BaseException as err:
        raise SystemExit(err)


if __name__ == "__main__":

    args = arguments()
    user_ids = []
    for user_id in args.user:
        user_ids.append(user_id)
    add_check(args.site, args.string, args.name, args.message, user_ids)
