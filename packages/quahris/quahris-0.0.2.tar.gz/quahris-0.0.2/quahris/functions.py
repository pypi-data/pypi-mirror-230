import requests 
import urllib3
import xml.etree.ElementTree as ET
from itertools import islice
import pandas as pd

global cred

def qualys_cred(username, api_key):
    global cred
    cred = (username, api_key)

def listHostText():
    global cred
    headers = {
        'X-Requested-With': 'Curl',
    }
    url = f"https://qualysguard.qg4.apps.qualys.com//api/2.0/fo/asset/host/?action=list"
    response = requests.get(url, headers=headers, auth=cred)
    return response.text

#The parameter will be like this: qids, status=Active, show_asset_id, truncation_limit
#make sure to follow this order.
#If you dont want to give paramtere values, just use: None
#tags must be 1 or 0
#remember when you do show tags, you have to do the rest as well.
def listVm(qids, status, show_asset, trunc, show_tags, use_tags, tag_include_selec, tag_exclude_selec, tag_set, do_xml):
    global cred
    headers = {
        'X-Requested-With': 'Curl',
    }
    if qids != None:
        #url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status={status}&show_asset_id={show_asset}&truncation_limit={trunc}"
        url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}"
        if status != None:
            url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status={status}"
            if show_asset != None:
                url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status={status}&show_asset_id={show_asset}"
                if trunc != None:
                    url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status={status}&show_asset_id={show_asset}&truncation_limit={trunc}"
                    if show_tags != None:
                        url = f"https://qualysguard.qg4.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&status={status}&show_asset_id={show_asset}&truncation_limit={trunc}&show_tags={show_tags}&use_tags={use_tags}&tag_include_selector={tag_include_selec}&tag_exclude_selector={tag_exclude_selec}&tag_set_by={tag_set}"
    response = requests.get(url, headers=headers, auth=cred)
    if do_xml == False:
        return response.text
    else:
        return 



def friendprint():
    print("What's up man! Thanks for downloading my library\n\n--Chris Nam")