import json
import requests


linkedin_api_key =  'LOkC-q7SjAV8ihl9DC7bCQ'
linkedin_url = 'https://www.linkedin.com/in/pasinha/'   
headers = {'Authorization': 'Bearer ' + linkedin_api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'

# Add more parameter options
NotImplemented

params = {

    'linkedin_profile_url': linkedin_url,

}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)


print(response)
import pdb
pdb.set_trace()