import pymsteams as pymsteams
import requests
import json
from datetime import datetime, timedelta


with open('secrets/API_KEY', 'r') as api_key_file:
    api_key = api_key_file.read()

payload = {}
headers = {
  'Authorization': f'Bearer {api_key}'
}

try:
    url = "https://api.pingdom.com/api/3.1/checks"
    response = requests.get(url, headers=headers, data=payload)
    result = json.loads(response.content)
    check_ids = []
    for i in result['checks']:
        check_ids.append(i['id'])
except BaseException as err:
    raise SystemExit(err)

to_time = int(datetime.timestamp(datetime.now()))
from_time = int(datetime.timestamp(datetime.now())) - 28800
down_count = 0
for check_id in check_ids:
    try:
        statuses_url = f"https://api.pingdom.com/api/3.1/summary.outage/{check_id}?from={from_time}&order=asc&to={to_time}"
        response2 = requests.get(statuses_url, headers=headers, data=payload)
        result2 = json.loads(response2.content)
        for j in result2['summary']['states']:
            if j['status'] == 'down':
                down_count += 1
    except BaseException as err:
        raise SystemExit(err)

try:
    tms_url = "https://api.pingdom.com/api/3.1/tms/check"
    response3 = requests.get(tms_url, headers=headers, data=payload)
    result3 = json.loads(response3.content)
    tms_ids = []
    for i in result3['checks']:
        tms_ids.append(i['id'])
except BaseException as err:
    raise SystemExit(err)

import datetime

try:
    from_time_3339 = (datetime.datetime.utcnow() - timedelta(hours=8)).isoformat("T") + "Z"
    tms_status = f"https://api.pingdom.com/api/3.1/tms/check/report/status?from={from_time_3339}"
    response4 = requests.get(tms_status, headers=headers, data=payload)
    result4 = json.loads(response4.content)

    tms_down = 0
    for s in result4['report']:
        for w in s['states']:
            if w['status'] == 'down':
                tms_down += 1
except BaseException as err:
    raise SystemExit(err)

text = f"Pingdom alerts count: uptime = {down_count}; transaction = {tms_down}"
try:
    teams_connector = pymsteams.connectorcard("https://outlook.office.com/webhook/###", verify=False)
    teams_connector.text(text)
    teams_connector.send()
except BaseException as err:
    raise SystemExit(err)
