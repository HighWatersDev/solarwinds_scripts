import requests
import json
from orionsdk import SwisClient
import logging
import datetime


with open ('secrets/ORION_USER', 'r') as user_file:
    username = user_file.read()
with open ('secrets/ORION_PASS', 'r') as pass_file:
    password = pass_file.read()
npm_server = ""


verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()


def set_local_volume_cp():
    query = "SELECT vl.Caption, vcp.Uri, vcp.VolumeID, ncp.ServiceArea, vl.NodeID \
            FROM Orion.VolumesCustomProperties as vcp \
            JOIN Orion.Volumes vl ON vcp.VolumeID = vl.VolumeID \
            JOIN Orion.NodesCustomProperties ncp ON vl.NodeID = ncp.NodeID \
            JOIN Orion.Nodes nc ON ncp.NodeID = nc.NodeID \
            WHERE (vl.Type LIKE '%Fixed%' OR vl.Type LIKE '%Mount%' OR vl.Type LIKE '%Network%')

    swis = SwisClient(npm_server, username, password)
    try:
        result = swis.query(query)
        for item in result['results']:
            uri = item['Uri']
            volume_name = item['Caption']
            service_area = item['ServiceArea']
            print("Volume Name: ", volume_name, "ServiceArea: ", service_area)
            try:
                swis.update(uri, ServiceArea=service_area)
            except:
                logging.error("Unable to update custom property", exc_info=True)
    except:
        logging.error("Unable to execute query on Solarwinds", exc_info=True)


def set_application_cp():
    query = "SELECT apm.Name, apm.DisplayName, apm.Uri, apm.NodeID, apm.FullyQualifiedName, ncp.ServiceArea, nc.Caption \
             FROM Orion.APM.Application as apm \
             JOIN Orion.NodesCustomProperties ncp ON apm.NodeID = ncp.NodeID \
             JOIN Orion.Nodes nc ON ncp.NodeID = nc.NodeID

    swis = SwisClient(npm_server, username, password)
    try:
        result = swis.query(query)
        for item in result['results']:
            uri = item['Uri']
            app_name = item['Name']
            service_area = item['ServiceArea']
            print("App Name: ", app_name, "ServiceArea: ", service_area)
            try:
                swis.update(uri + '/CustomProperties', ServiceArea=service_area)
            except:
                logging.error("Unable to update custom property", exc_info=True)
    except:
        logging.error("Unable to execute query on Solarwinds", exc_info=True)


if __name__ == "__main__":
    time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M")
    logging.basicConfig(level=logging.INFO,
                        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
                        filename="sw_sync_cp.log" + time
                        )

    
if __name__ == "__main__":
    set_application_cp()
    set_local_volume_cp()
