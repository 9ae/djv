from KalturaImages import GetKS,API_BASE_URL
import requests

def update_tags(entry_id, tags):
    ks = GetKS()
    url = API_BASE_URL+'service=media&action=update&format=1&ks='+ks
    params = {'entryId': entry_id,
              'mediaEntry:tags':','.join(tags)}
    resp = requests.post(url, data=params)
    j = resp.json()
    print j['tags']