import httpx
import string
import random
from .Classes.user import User
from .Classes.package import Package
from .Classes.coupon import Coupon
from .Classes.sysinfo import SysInfo

class HolaClient:
    def __init__(self, api_url, api_key):
        """
        Initializes a new instance of the HolaClient class.

        Args:
            api_url (str): The API base URL.
            api_key (str): The API key for authentication.
        """
        self.api_url = api_url
        # Check if api_url ends with /
        if self.api_url.endswith('/'):
            self.api_url = self.api_url[:-1]
        self.api_key = api_key

    def user_info(self, hcid):
        """
        Fetches user info from the API.

        Args:
            hcid (int): HCID of the user.

        Returns:
            User: An instance of the User class.
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
        Fetches the user HCID using a Discord ID.

        Args:
            id (int): Discord ID of the user.

        Returns:
            HCID (int).
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
        Fetches the package of a user from the API.

        Args:
            hcid (int): HCID of the user.

        Returns:
            Package Name (str).
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
                # Returns the user's package
                data = response.json()
                return data['package']

    def set_coins(self, hcid: int, coins: int):
        """
        Sets the number of coins for a user.

        Args:
            hcid (int): HCID of the user.
            coins (int): Number of coins to set.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
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
        """
        Adds coins to a user's account.

        Args:
            hcid (int): HCID of the user.
            coins (int): Number of coins to add.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
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
        """
        Removes coins from a user's account.

        Args:
            hcid (int): HCID of the user.
            coins (int): Number of coins to remove.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
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
        """
        Creates a coupon with specified attributes.

        Args:
            coins (int): Number of coins for the coupon.
            ram (int): Amount of RAM for the coupon.
            disk (int): Amount of disk space for the coupon.
            cpu (int): Number of CPU cores for the coupon.
            servers (int): Number of servers for the coupon.
            backups (int): Number of backups for the coupon.
            allocation (int): Allocation value for the coupon.
            database (int): Number of databases for the coupon.
            uses (int): Number of uses for the coupon.
            code (str, optional): Coupon code. If not provided, a random code will be generated.

        Returns:
            Coupon: An instance of the Coupon class representing the created coupon.
        """
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
                        return Coupon(coins, ram, disk, cpu, servers, backups, allocation, database, uses, code)
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
        """
        Revokes a coupon with the specified code.

        Args:
            code (str): Coupon code.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
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

    def set_package(self, id, package):
        """
        Sets the package for a user.

        Args:
            id: ID of the user.
            package (str): Name of the package to set for the user.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
        if not self.api_key or not self.api_key:
            raise Exception('api_url and api_key must be set')
        url = f"{self.api_url}/api/setplan"
        headers = {'Authorization': self.api_key}
        payload = {
            'user': id,
            'package': package
        }
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

    def sys_info(self):
        """
        Fetches system information from the API.

        Returns:
            SysInfo: An instance of the SysInfo class containing system information.
        """
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')
        headers = {"Authorization": self.api_key}
        try:
            with httpx.Client() as client:
                total_disk = client.get(f"{self.api_url}/api/total/disk", headers=headers).json()['disk']
                total_ram = client.get(f"{self.api_url}/api/total/ram", headers=headers).json()['ram']
                used_disk = client.get(f"{self.api_url}/api/used/disk", headers=headers).json()['disk']
                used_ram = client.get(f"{self.api_url}/api/used/ram", headers=headers).json()['ram']
                return SysInfo(total_ram, total_disk, used_ram, used_disk)
        except httpx.RequestError as e:
            raise Exception(f'Error making the API request: {str(e)}')

    def set_resources(self, user, ram=None, disk=None, cpu=None, servers=None, backups=None, allocations=None, databases=None):
        """
        Sets resources for a user.

        Args:
            user: User identifier.
            ram (int, optional): Amount of RAM to set.
            disk (int, optional): Amount of disk space to set.
            cpu (int, optional): Number of CPU cores to set.
            servers (int, optional): Number of servers to set.
            backups (int, optional): Number of backups to set.
            allocations (int, optional): Allocation value to set.
            databases (int, optional): Number of databases to set.

        Returns:
            bool: True if the operation is successful, else raises an exception.
        """
        if not self.api_url or not self.api_key:
            raise Exception('api_url and api_key must be set')

        url = f"{self.api_url}/api/setresources"
        headers = {'Authorization': self.api_key}
        payload = {
            'user': user,
            'ram': ram,
            'disk': disk,
            'cpu': cpu,
            'servers': servers,
            'backups': backups,
            'allocations': allocations,
            'databases': databases
        }

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
