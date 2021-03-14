import requests
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv
from orionsdk import SwisClient

verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SNOW_USER = os.getenv('SNOW_USER')
SNOW_PASSWORD = os.getenv('SNOW_PASSWORD')
NPM = ""
ORION_USER = os.getenv('ORION_USER')
ORION_PASS = os.getenv('ORION_PASS')

URL = 'https://<instance>.service-now.com/api/now/v1/table/incident?'
headers = {"Content-Type": "application/json", "Accept": "application/json"}


def sw_report():
    query = "select distinct top 10 ac.Name as [Alert Name] \
            ,count(ah.message) as [Alert Count 30 days] \
            ,today.[Alert count] as [Alert Count 24 hours] \
            ,EntityCaption as [Trigger Object] \
            ,RelatedNodeCaption as [Parent Node] \
            ,tolocal(max(ah.TimeStamp)) as [Most Recent Trigger] \
            FROM Orion.AlertHistory ah \
            join Orion.AlertObjects ao on ao.alertobjectid=ah.alertobjectid \
            join Orion.AlertConfigurations ac on ac.alertid=ao.alertid \
            join Orion.Actions a on a.actionid=ah.actionid \
            left JOIN ( \
            select distinct ac.Name as AlertName \
            ,'https://<URL>/Orion/NetPerfMon/ActiveAlertDetails.aspx?NetObject=AAT:' \
            +ToString(AlertObjectID) as [_linkfor_Name] \
            ,count(ah.message) as [Alert Count] \
            ,EntityCaption as [Trigger Object] \
            ,RelatedNodeCaption as [Parent Node] \
            ,RelatedNodeDetailsUrl as [_linkfor_Parent Node] \
            ,tolocal(max(ah.TimeStamp)) as [Most Recent Trigger] \
            FROM Orion.AlertHistory ah \
            join Orion.AlertObjects ao on ao.alertobjectid=ah.alertobjectid \
            join Orion.AlertConfigurations ac on ac.alertid=ao.alertid \
            join Orion.Actions a on a.actionid=ah.actionid \
            WHERE \
            hourdiff(ah.timestamp,GETUTCDATE())<24 \
            and ah.timestamp < getutcdate() \
            and ac.name not like '%last poll time is 15 minutes old%' \
            group by name,  [Trigger Object], [Parent Node] \
            ) today on today.[_linkfor_Name] = 'https://<URL>/Orion/NetPerfMon/ActiveAlertDetails.aspx?NetObject=AAT:' \
            +ToString(AlertObjectID) \
            WHERE \
            daydiff(ah.timestamp,GETUTCDATE())<30 \
            and ah.timestamp < getutcdate() \
            and ac.name not like '%last poll time is 15 minutes old%' \
            group by name,  [Trigger Object], [Parent Node] \
            order by [Alert Count 30 days] desc"
 
    swis = SwisClient(NPM, ORION_USER, ORION_PASS, verify=False)
    get_report = swis.query(query)
    details_info = []
    for line in get_report['results']:
        details_info.append(str(line))
    return details_info


def create_incident():
    details_info = sw_report()
    desc = '\n'.join(details_info)
    incident_data = {'short_description': 'Solarwinds Top 10 alerts',
                     'description': desc,
                     'contact_type': 'Email',
                     'caller_id': '###',
                     'opened_by': '###',
                     'assignment_group': '###',
                     'priority': 4,
                     'impact': 3,
                     'u_affected_user': '###',
                     'business_service': '###',
                     'category': 'Monitoring'}
    create_inc = requests.post(URL, auth=(SNOW_USER, SNOW_PASSWORD), headers=headers,
                               data=json.dumps(incident_data))
    print(json.loads(create_inc.content))


if __name__ == "__main__":
    sw_report()
    create_incident()
