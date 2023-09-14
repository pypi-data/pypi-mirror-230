from .auth import Auth
from .public import Public
from .admin import Admin
from .fs import Fs


class AsyncClient(Admin, Fs, Auth):
    def __init__(self, usr: str, pwd: str, url: str = "http://127.0.0.1", port: str = "5244", otp = None) -> None:
        self.otp = otp
        super().__init__(usr, pwd, url, port)
        self.public = Public(url, port)


    async def close(self):
        await self.session.close()


    


            

    


    
    

    
        


        

    

      