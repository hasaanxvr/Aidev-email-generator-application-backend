import requests

api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/profile/email'
params = {
    'linkedin_profile_url': 'https://www.linkedin.com/in/fateh-ali-aamir/',
    'callback_url': 'https://webhook.site/5195d655-5c96-412d-a8fd-77a537aa6aca',
}
response = requests.get(api_endpoint,
                        params=params,
                        headers=headers)
