import requests

api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
params = {
    'linkedin_profile_url': 'https://www.linkedin.com/in/muhammad-hasaan-423640217/',
}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)


import pdb

pdb.set_trace()