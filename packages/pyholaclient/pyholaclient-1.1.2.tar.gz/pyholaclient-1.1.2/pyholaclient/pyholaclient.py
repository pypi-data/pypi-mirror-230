import httpx
import string
import random
from .Classes.user import User
from .Classes.package import Package
from .Classes.coupon import Coupon


class HolaClient:
    def __init__(self, api_url, api_key):
        """
        Path: holaclient/holaclient.py     
        """
        self.api_url = api_url
        # Check if api_url end with /
        if self.api_url.endswith('/'):
            self.api_url = self.api_url[:-1]
        self.api_key = api_key
    def user_info(self, hcid):
        """
        Fetches user info from the API
        Params:
        hcid (int): hcid of the user
        Returns:

        """
        # Check if api_url and api_key are set
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/api/userinfo/{hcid}"
        headers = {'Authorization': f"{self.api_key}"}
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 301:
                # Returns if the API key is invalid
                raise Exception('Invalid API Key!')
            elif response.status_code == 400:
                # Returns when the HCID is invalid
                raise Exception('HCID is Invalid or Not Found')
            elif response.status_code == 200:
                # Returns the user with class User
                return User(response.json(), Package(response.json()['package'], response.json()['extra']))
    
    def user_hcid(self, id: int):
        """
        Fetches the user HCID using a Discord ID
        Params:
        id (int): Discord ID of the user
        Returns:
        HCID: int
        """
        if not self.api_key or not self.api_url:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/users/id/get/hcid/{id}"
        headers = {'Authorization': f"{self.api_key}"}
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 301:
                # Returns if the API key is invalid
                raise Exception('Invalid API Key!')
            elif response.status_code == 400:
                # Returns when the HCID is invalid
                raise Exception('HCID is Invalid or Not Found')
            elif response.status_code == 200:
                # Returns the user with class User
                data = response.json()
                if data["success"]:
                    return data['id']
                else:
                    raise Exception('HCID is Invalid or Not Found')
            

    def user_package(self, hcid):
        """
        Fetches package of a user from the API
        Params:
        hcid (int): hcid of the user
        Returns:
        Package Name: str
        """
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/api/package/?user={hcid}"
        headers = {'Authorization': f"{self.api_key}"}
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 301:
                # Returns if the API key is invalid
                raise Exception('Invalid API Key!')
            elif response.status_code == 400:
                # Returns when the HCID is invalid
                raise Exception('HCID is Invalid or Not Found')
            elif response.status_code == 200:
                # Returns the user with class User
                data = response.json()
                return data['package']
            
    def set_coins(self, hcid: int, coins: int):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')

        url = f"{self.api_url}/api/application/coins/set"
        headers = {'Authorization': self.api_key}
        payload = {'user': hcid, 'coins': coins}

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return True
                    else:
                        raise Exception('API request was not successful')
                elif response.status_code == 400:
                    raise Exception('HCID is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')

    def add_coins(self, hcid: int, coins: int):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')

        url = f"{self.api_url}/api/application/coins/add"
        headers = {'Authorization': self.api_key}
        payload = {'user': hcid, 'coins': coins}

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return True
                    else:
                        raise Exception('API request was not successful')
                elif response.status_code == 400:
                    raise Exception('HCID is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')
    def remove_coins(self, hcid: int, coins: int):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        
        url = f"{self.api_url}/api/application/coins/remove"
        headers = {'Authorization': self.api_key}
        payload = {'user': hcid, 'coins': coins}

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return True
                    else:
                        raise Exception('API request was not successful')
                elif response.status_code == 400:
                    raise Exception('HCID is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')

    def create_coupon(self, coins: int, ram: int, disk: int, cpu: int, servers: int, backups: int, allocation: int, database: int, uses: int, code: str = None):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        if not code:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        url = f"{self.api_url}/api/createcoupon/"
        headers = {'Authorization': self.api_key}
        payload = {
            'coins': coins,
            'ram': ram,
            'disk': disk,
            'cpu': cpu,
            'servers': servers,
            'backups': backups,
            'allocation': allocation,
            'database': database,
            'uses': uses,
            'code': code
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return Coupon(coins, ram, disk, cpu, servers, backups, allocation, database,uses, code)
                    else:
                        raise Exception(data.get('status'))
                elif response.status_code == 400:
                    raise Exception('HCID is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')


    def revoke_coupon(self, code: str):
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        if not code:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        url = f"{self.api_url}/api/revokecoupon/"
        headers = {'Authorization': self.api_key}
        payload = {
            'code': code
        }

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return True
                    else:
                        raise Exception(data.get('status'))
                elif response.status_code == 400:
                    raise Exception('HCID is Invalid or Not Found')
                elif response.status_code == 401:
                    raise Exception('Unauthorized: Check your API key')
                else:
                    raise Exception(f'Unexpected status code: {response.status_code}')
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')