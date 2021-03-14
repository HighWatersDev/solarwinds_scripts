import requests
from requests.auth import HTTPBasicAuth
from requests import HTTPError
import json
from orionsdk import SwisClient
import math


with open('secrets/ORION_URL', 'r') as orion_url_file:
    npm_server = orion_url_file.read()
with open('secrets/ORION_USER', 'r') as orion_user_file:
    username = orion_user_file.read()
with open('secrets/ORION_PASS', 'r') as orion_pass_file:
    password = orion_pass_file.read()
with open('secrets/NA_USER', 'r') as na_user_file:
    na_user = na_user_file.read()
with open('secrets/NA_PASS', 'r') as na_pass_file:
    na_pass = na_pass_file.read()
with open('secrets/NA_URL', 'r') as na_url_file:
    na_url = na_url_file.read()
    

verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()


def set_volume_cp():
    query = "SELECT SRM_V.Caption, SRM_V.Uri, SRM_V.VServers.Caption as [VServer] \
             FROM Orion.SRM.Volumes SRM_V JOIN Orion.SRM.VolumeCustomProperties vcp ON SRM_V.VolumeID = vcp.VolumeID"
    swis = SwisClient(npm_server, username, password)
    try:
        volumes_uri = swis.query(query)
    except:
        raise SystemExit
    try:
        with requests.Session() as s:
            s.auth = HTTPBasicAuth(na_user, na_pass)

            vol = s.get(f'https://{na_url}/api/datacenter/storage/volumes',
                        verify=False)
            print(vol)
            print(json.loads(vol.content))
            num_records = vol.json()['total_records']
            vol = s.get(f'https://{na_url}/api/datacenter/storage/volumes?max_records={str(num_records)}&order_by=name', verify=False)
            response = json.loads(vol.content)
    except HTTPError as err:
        raise SystemExit(err)
    for vol1 in response['records']:
        volume_svm = vol1['svm']['name']
        volume_name = vol1['name']
        volume_autosize_mode = vol1['autosize']['mode']
        volume_autosize_max = vol1['autosize']['maximum']
        for volume in volumes_uri['results']:
            uri = volume['Uri']
            svm = volume['VServer']
            name = volume['Caption']
            if volume_name == name and volume_svm == svm:
                if volume_autosize_mode == 'off':
                    try:
                        print("Updating ", name, " to false")
                        swis.update(uri + '/CustomProperties', autogrow_enabled='false')
                    except:
                        pass
                elif 'grow' in volume_autosize_mode:
                    try:
                        size_name = ("B", "KB", "MB", "GB", "TB")
                        i = int(math.floor(math.log(volume_autosize_max, 1024)))
                        p = math.pow(1024, i)
                        s = round(volume_autosize_max / p, 2)
                        volume_autosize_readable = str(s) + str(size_name[i])
                        print("Updating ", name, " to true")
                        swis.update(uri + '/CustomProperties', autogrow_enabled='true')
                        swis.update(uri + '/CustomProperties', autogrow_size='{0}'.format(volume_autosize_max))
                        swis.update(uri + '/CustomProperties', autogrow_size_readable='{0}'.format(volume_autosize_readable))
                    except:
                        pass


if __name__ == "__main__":
    set_volume_cp()
