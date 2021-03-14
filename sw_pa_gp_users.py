import os
from os.path import join, dirname
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
from orionsdk import SwisClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
sw_user = os.getenv("SW_USER")
password = os.getenv("SW_PASS")
payload = {}
verify = False
if not verify:
    requests.packages.urllib3.disable_warnings()


def get_key():
    key_urls = [os.getenv("NI_KEY_URL"), os.getenv("DC_KEY_URL")]
    pa_keys = []
    if key_urls is not None:
        for item in key_urls:
            key_url = item
            key_headers = {}
            try:
                key_response = requests.request("GET", key_url, headers=key_headers, data=payload)
                key_root = ET.fromstring(key_response.content)
                for child in key_root.iter('*'):
                    if child.tag == 'key':
                        pa_keys.append(child.text)
            except BaseException as err:
                raise SystemExit(err)
    return pa_keys


def get_number_users(pa_keys):
    dc_url = os.getenv("DC_URL")
    ni_url = os.getenv("NI_URL")
    total_users = 0
    dc_users = 0
    ni_users = 0
    for key in pa_keys:
        headers = {'X-PAN-KEY': key}
        try:
            dc_response = requests.request("GET", dc_url, headers=headers, data=payload)
            root = ET.fromstring(dc_response.content)
            for child in root.iter('*'):
                if child.tag == 'TotalCurrentUsers':
                    print(child.text)
                    dc_users = dc_users + int(child.text)
                    total_users = total_users + int(child.text)
        except BaseException as err:
            raise SystemExit(err)
        try:
            ni_response = requests.request("GET", ni_url, headers=headers, data=payload)
            root = ET.fromstring(ni_response.content)
            for child in root.iter('*'):
                if child.tag == 'TotalCurrentUsers':
                    print(child.text)
                    ni_users = ni_users + int(child.text)
                    total_users = total_users + int(child.text)
        except BaseException as err:
            raise SystemExit(err)
    print(ni_users, dc_users, (ni_users + dc_users))
    return ni_users, dc_users


def update_sw_cp(ni_users, dc_users):
    npm_server = os.getenv("NPM_SERVER")
    orion_user = os.getenv("ORION_USER")
    orion_pass = os.getenv("ORION_PASS")
    nodes = ['', '']
    try:
        for fqdn in nodes:
            swis = SwisClient(npm_server, orion_user, orion_pass)
            node_id = swis.query("SELECT n.NodeID FROM Orion.Nodes n WHERE DNS = '{0}'".format(fqdn))
            if node_id['results'] == []:
                pass
            else:
                nodeID = node_id['results'][0]['NodeID']
                uri_query = swis.query("SELECT Uri FROM Orion.Nodes WHERE NodeID='{0}'".format(nodeID))
                node_uri = uri_query['results'][0]['Uri']
                if fqdn == "":
                    swis.update(node_uri + '/CustomProperties', gp_users='{0}'.format(ni_users))
                elif fqdn == "":
                    swis.update(node_uri + '/CustomProperties', gp_users='{0}'.format(dc_users))
    except BaseException as err:
        raise SystemExit(err)
    return True


def main():
    t1 = get_number_users(get_key())
    update_sw_cp(t1[0], t1[1])


if __name__ == '__main__':
    main()
