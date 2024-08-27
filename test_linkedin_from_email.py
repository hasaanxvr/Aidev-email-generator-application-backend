import requests

api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/profile/resolve/email'
params = {
    'email': 'ahmedayub@yahoo.com',
    'lookup_depth': 'deep',
  
}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)



import pdb
pdb.set_trace()