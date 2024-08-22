import requests

api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/credit-balance'
response = requests.get(api_endpoint,
                        headers=headers)


print(response.content)