from KalturaImages import GetKS,API_BASE_URL
import requests

def update_tags(entry_id, tags):
    ks = GetKS()

    #get existing fields
    get_url = API_BASE_URL+'service=media&action=get&format=1&entryId='+entry_id+'&ks='+ks
    r = requests.get(get_url)
    data = r.json()
    old_tags = data['tags']
    if len(tags)>0:
        new_tags = ', '.join(tags)
        if old_tags!=None and old_tags!='':
            new_tags = old_tags + ', ' +new_tags
        new_tags = new_tags.replace(', ', ',')
        print 'new tags = '+new_tags
        # ks = GetKS()
        url = API_BASE_URL+'service=media&action=update&format=1&ks='+ks
        params = {'entryId': entry_id,
                  'mediaEntry:tags':new_tags}
        resp = requests.post(url, data=params)
        j = resp.json()
        print j
        print 'result = '+j['tags']
    else:
        print 'no new tags to update'