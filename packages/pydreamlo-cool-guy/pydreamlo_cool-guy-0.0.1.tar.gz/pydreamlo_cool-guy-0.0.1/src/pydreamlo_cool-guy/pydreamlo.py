import requests
class LeaderBoard:
    def __init__(self,dreamlo_url:str,dreamlo_public:str):
        self.dreamlo_url = dreamlo_url
        self.dreamlo_public_key_url = dreamlo_public
    def _send(self,url:str)->str:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Request failed with status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    def add(self,username:str,score:int,time:int = 0,text:str='') -> str:
        request_url = f"{self.dreamlo_url}/add/{username}/{score}/{time}/{text}"
        return self._send(request_url)
    def delete(self,username:str) -> str:
        request_url = f"{self.dreamlo_url}/delete/{username}"
        return self._send(request_url)
    def clear(self)->str:
        request_url = f"{self.dreamlo_url}/clear/"
        return self._send(request_url)
    def get(self,index:int = 0,upto:int = 0,rtype:str = 'json',sort:str='') -> str:
        param = {'a': '-seconds-asc', 'd': '-seconds'}.get(sort, '')
        request_url = f"{self.dreamlo_public_key_url}/{rtype}{param}/{index}/{upto}"
        return self._send(request_url)
    def get_new_sorted(self,index:int = 0,upto:int = 0,rtype:str = 'json'):
        request_url = f"{self.dreamlo_public_key_url}/{rtype}-date/{index}/{upto}"
        return self._send(request_url)
    def get_user(self,username:str,rtype:str='json'):
        request_url = f"{self.dreamlo_public_key_url}/{rtype}-get/{username}"
        return self._send(request_url)
