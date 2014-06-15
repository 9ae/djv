from KalturaImages import GetKS,API_BASE_URL
import requests

def update_tags(entry_id, tags):
    ks = GetKS()

    #get existing fields
    r = requests.get(API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks)
    data = r.json()
    old_tags = data['tags'].split(', ')
    old_tags = set(old_tags)
    new_tags = set(tags)

    join_tags = old_tags | new_tags
    update_tags = list(join_tags)


    ks = GetKS()
    url = API_BASE_URL+'service=media&action=update&format=1&ks='+ks
    params = {'entryId': entry_id,
              'mediaEntry:tags':','.join(update_tags)}
    resp = requests.post(url, data=params)
    j = resp.json()
    print j['tags']
