import requests
import json
from abc import ABC, abstractmethod

class UserDataRetrievalStrategy(ABC):
    @abstractmethod
    def get_user_data(self) -> str:
        pass



class LinkedInDataRetrievalStrategy(UserDataRetrievalStrategy):
    def __init__(self, linkedin_url: str):
        self.linkedin_url = linkedin_url
        self.api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'

    def get_user_data(self) -> str:
        headers = {'Authorization': 'Bearer ' + self.api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        
        params = {
            'linkedin_profile_url': self.linkedin_url,
        }
        response = requests.get(api_endpoint, params=params, headers=headers)

        if response.status_code != 200:
            return None
        
        data = json.dumps(response.json(), indent=4)
        return data
    

class NameCompanyDataRetrievalStrategy(UserDataRetrievalStrategy):
    def __init__(self, first_name: str, company: str, last_name: str, location: str, title: str, enrich_profile='enrich' ):
        self.first_name = first_name
        self.company = company
        self.last_name = last_name
        self.location = location
        self.title = title
        self.enrich_profile=enrich_profile
        self.api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
        
    def get_user_data(self):
        headers = {'Authorization': 'Bearer ' + self.api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/profile/resolve'
        params = {
            'company_domain': self.company,
            'first_name': self.first_name,
            'similarity_checks': 'yes',
            'enrich_profile': self.last_name,
            'location': self.location,
            'title': self.title,
            'last_name': self.last_name,
            'enrich_profile': self.enrich_profile
        }
        response = requests.get(api_endpoint,
                                params=params,
                                headers=headers)
        
        if response.status_code != 200:
            return None
        
        data = json.dumps(response.json(), indent=4)
        return data
    
    

class EmailDataRetrievalStrategy(UserDataRetrievalStrategy):
    
    def __init__(self, email:str):
        self.email = email
        self.api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
    
    def get_user_data(self):
        headers = {'Authorization': 'Bearer ' + self.api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/linkedin/profile/resolve/email'
        params = {
        'email': self.email,
        'lookup_depth': 'deep',
        }
        
        response = requests.get(api_endpoint,
                                params=params,
                                headers=headers)
        
        if response.status_code != 200:
            return None
        
        data = json.dumps(response.json(), indent=4)
        return data