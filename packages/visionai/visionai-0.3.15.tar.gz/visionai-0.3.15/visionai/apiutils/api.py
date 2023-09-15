import requests
from config import VISIONAI_API_URL
class Api():
    def __init__(self) -> None:
        pass


    def post(self,url: str, data: dict = None, headers: dict = None, timeout: int = 10):
        try:
            pass
        except Exception as e:
            pass

    def get(self,url: str, params: dict = None, headers: dict = None, timeout: int = 10):
        try:
            print("API URL: ", f'{VISIONAI_API_URL}{url}')
            return requests.get(f'{VISIONAI_API_URL}{url}', params=params, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)  
        except Exception as e:
            print ("Exception: ",e)

        
    def put(self,url: str, data: dict = None, headers: dict = None, timeout: int = 10):
        try:
            pass
        except Exception as e:
            pass

    def delete(self,url: str, data: dict = None, headers: dict = None, timeout: int = 10):
        try:
            pass
        except Exception as e:
            pass
    