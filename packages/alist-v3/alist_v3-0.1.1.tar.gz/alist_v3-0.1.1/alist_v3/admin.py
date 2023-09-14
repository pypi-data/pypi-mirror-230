from .fs import Fs

class Admin(Fs):
    """FOR ADMIN MANAGE USERS"""

    def __init__(self, usr: str, pwd: str, url: str = "http://127.0.0.1", port: int = 5244):
        super().__init__(usr, pwd, url, port)

    async def get_list_usr(self) -> dict:
        """
        description: Get the list of the users

        params: None

        return: dict
        """

        path = "/api/admin/user/list"
        headers = {"Authorization": self.auth}

        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def get_usr(self) -> dict:
        """
        description: Get the information of the user

        params: None

        return: dict
        """

        path = "/api/admin/user/get"
        headers = {"Authorization": self.auth}

        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            return await resp.json()
        

    async def post_create_usr(self, username: str, password: str, base_path: str, role: int, permission: int, disable: bool, sso_id: str = None) -> dict:
        """
        description: Create a user

        params:
            username: str - The username of the user
            password: str - The password of the user
            base_path: str - The base path of the user
            role: int - The role of the user
            permission: int - The permission of the user
            disable: bool - Disable the user
            sso_id: str - The sso id of the user

        return: dict
        """

        path = "/api/admin/user/create"
        headers = {"Authorization": self.auth}
        body = {"username": username, "password": password, "base_path": base_path, "role": role, "permission": permission, "disable": disable, "sso_id": sso_id}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_update_usr(self, username: str, password: str, base_path: str, role: int, permission: int, disable: bool, sso_id: str = None) -> dict:
        """
        description: Update a user

        params:
            username: str - The username of the user
            password: str - The password of the user
            base_path: str - The base path of the user
            role: int - The role of the user
            permission: int - The permission of the user
            disable: bool - Disable the user
            sso_id: str - The sso id of the user

        return: dict
        """

        path = "/api/admin/user/update"
        headers = {"Authorization": self.auth}
        body = {"username": username, "password": password, "base_path": base_path, "role": role, "permission": permission, "disable": disable, "sso_id": sso_id}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_cancel_2fa(self, id: int) -> dict:
        """
        description: Cancel the 2fa of a user

        params:
            id: int - The id of the user

        return: dict
        """

        path = "/api/admin/user/cancel_2fa"
        headers = {"Authorization": self.auth}
        body = {"id": id}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_delete_usr(self, id: int) -> dict:
        """
        description: Delete a user

        params:
            id: int - The id of the user

        return: dict
        """

        path = "/api/admin/user/delete"
        headers = {"Authorization": self.auth}
        body = {"id": id}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_del_cache(self, username: str) -> dict:
        """
        description: Delete the cache of a user

        params:
            username: str - The username of the user

        return: dict
        """

        path = "/api/admin/user/del_cache"
        headers = {"Authorization": self.auth}
        body = {"username": username}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        


    """FOR ADMIN MANAGE META"""

    async def get_meta_list(self, page: str = None, per_page: str = None) -> dict:
        """
        description: Get the list of the meta

        params:
            page: str - The page of the list
            per_page: str - The number of meta per page

        return: dict
        """

        path = "/api/admin/meta/list"
        headers = {"Authorization": self.auth}
        if page and per_page:
            query = {"page": 1, "per_page": 10}
        else:
            query = None
            
        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            return await resp.json()
        

    async def get_meta(self, id: int) -> dict:
        """
        description: Get the information of a meta

        params:
            id: int - The id of the meta

        return: dict
        """

        path = "/api/admin/meta/get"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            return await resp.json()
        

    async def post_create_meta(self, id: int, fspath: str, password: str, p_sub: bool, write: bool, w_sub: bool, readme: str, hide: bool = False, h_sub: bool = False, r_sub: bool = True) -> dict:
        """
        description: Create a meta

        params:
            id: int - The id of the meta
            fspath: str - The path of the directory
            password: str - The password of the directory
            p_sub: bool - The permission of the sub directories
            write: bool - The permission of the files
            w_sub: bool - The permission of the sub files
            readme: str - The readme of the directory
            hide: bool - Hide the directory
            h_sub: bool - Hide the sub directories
            r_sub: bool - Hide the sub files

        return: dict
        """

        path = "/api/admin/meta/create"
        headers = {"Authorization": self.auth}
        body = {"id": id, "fspath": fspath, "password": password, "p_sub": p_sub, "write": write, "w_sub": w_sub, "readme": readme, "hide": hide, "h_sub": h_sub, "r_sub": r_sub}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_update_meta(self, id: int, fspath: str, password: str, p_sub: bool, write: bool, w_sub: bool, readme: str, hide: bool = False, h_sub: bool = False, r_sub: bool = True) -> dict:
        """
        description: Update a meta

        params:
            id: int - The id of the meta
            fspath: str - The path of the directory
            password: str - The password of the directory
            p_sub: bool - The permission of the sub directories
            write: bool - The permission of the files
            w_sub: bool - The permission of the sub files
            readme: str - The readme of the directory
            hide: bool - Hide the directory
            h_sub: bool - Hide the sub directories
            r_sub: bool - Hide the sub files

        return: dict
        """

        path = "/api/admin/meta/update"
        headers = {"Authorization": self.auth}
        body = {"id": id, "fspath": fspath, "password": password, "p_sub": p_sub, "write": write, "w_sub": w_sub, "readme": readme, "hide": hide, "h_sub": h_sub, "r_sub": r_sub}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            return await resp.json()
        

    async def post_delete_meta(self, id: int) -> dict:
        """
        description: Delete a meta

        params:
            id: int - The id of the meta

        return: dict
        """

        path = "/api/admin/meta/delete"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.post(f"{self.url}{path}", headers=headers, params=query) as resp:
            return await resp.json()
        


    """FOR ADMIN MANAGE DRIVER"""


    async def get_list_driver(self) -> dict:
        """
        description: Get the list of the drivers

        params: None

        return: dict
        """

        path = "/api/admin/driver/list"
        headers = {"Authorization": self.auth}

        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            return await resp.json()
        

    
    async def get_driver_names(self) -> dict:
        """
        description: Get the names of the drivers

        params: None

        return: dict
        """

        path = "/api/admin/driver/names"
        headers = {"Authorization": self.auth}

        async with self.session.get(f"{self.url}{path}", headers=headers) as resp:
            return await resp.json()
        

    
    async def get_driver_info(self, driver: str) -> dict:
        """
        description: Get the information of a driver

        params:
            driver: str - The name of the driver

        return: dict
        """

        path = "/api/admin/driver/info"
        headers = {"Authorization": self.auth}
        query = {"driver": driver}

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            return await resp.json()
        


    """FOR ADMIN MANAGE STORAGE"""


    async def get_list_storage(self, page: str = None, per_page: str = None) -> dict:
        """
        description: Get the list of the storage

        params:
            page: str - The page of the list
            per_page: str - The number of storage per page

        return: dict
        """

        path = "/api/admin/storage/list"
        headers = {"Authorization": self.auth}
        if page and per_page:
            query = {"page": 1, "per_page": 10}
        else:
            query = None

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            return await resp.json()
        

    async def post_enable_storage(self, id: int) -> dict:
        """
        description: Enable a storage

        params:
            id: int - The id of the storage

        return: dict
        """

        path = "/api/admin/storage/enable"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.post(f"{self.url}{path}", params=query, headers=headers) as resp:
            return await resp.json()
        

    async def post_disable_storage(self, id: int) -> dict:
        """
        description: Disable a storage

        params:
            id: int - The id of the storage

        return: dict
        """

        path = "/api/admin/storage/disable"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.post(f"{self.url}{path}", params=query, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def create_storage(self, name: str, mount_path: str, driver: str, order: int, remark: str = "", cache_expiration: int = 30, web_proxy: bool = False, webdav_policy: str = "native_proxy", down_proxy_url: str = "", enable_sign: bool = False, extract_folder: str = "front", order_by: str = "name", order_direction: str = "asc", addition: str = None) -> dict:
        """
        description: Create a storage

        params:
            name: str - The name of the storage
            mount_path: str - The mount path of the storage
            driver: str - The driver of the storage
            order: int - The order of the storage
            remark: str - The remark of the storage
            cache_expiration: int - The cache expiration of the storage
            web_proxy: bool - Enable the web proxy of the storage
            webdav_policy: str - The webdav policy of the storage
            down_proxy_url: str - The download proxy url of the storage
            enable_sign: bool - Enable the sign of the storage
            extract_folder: str - The extract folder of the storage
            order_by: str - The order by of the storage
            order_direction: str - The order direction of the storage
            addition: str - The addition of the storage

        return: dict
        """

        path = "/api/admin/storage/create"
        headers = {"Authorization": self.auth}
        body = {"name": name, "mount_path": mount_path, "driver": driver, "order": order, "remark": remark, "cache_expiration": cache_expiration, "web_proxy": web_proxy, "webdav_policy": webdav_policy, "down_proxy_url": down_proxy_url, "enable_sign": enable_sign, "extract_folder": extract_folder, "order_by": order_by, "order_direction": order_direction, "addition": addition}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def get_storage_info(self, id: int) -> dict:
        """
        description: Get the information of a storage

        params:
            id: int - The id of the storage

        return: dict
        """

        path = "/api/admin/storage/info"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def delete_storage(self, id: int) -> dict:
        """
        description: Delete a storage

        params:
            id: int - The id of the storage

        return: dict
        """

        path = "/api/admin/storage/delete"
        headers = {"Authorization": self.auth}
        query = {"id": id}

        async with self.session.post(f"{self.url}{path}", headers=headers, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def load_all_storage(self) -> dict:
        """
        description: Load all the storage

        params: None

        return: dict
        """

        path = "/api/admin/storage/load_all"
        headers = {"Authorization": self.auth}

        async with self.session.post(f"{self.url}{path}", headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


    """FOR ADMIN MANAGE SETTINGS"""


    async def get_settings(self, groups: str = None, group: str = None) -> dict:
        """
        description: Get the settings

        params:
            groups: str - 5,0-其它设置, 包括aria2和令牌等
            group: str - 1-站点; 2-样式; 3-预览; 4-全局; 7-单点登录

        return: dict
        """

        path = "/api/admin/settings"
        headers = {"Authorization": self.auth}
        if groups:
            query = {"groups": groups}
        elif group:
            query = {"group": group}
        else:
            query = None

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def get_setting(self, key: str = None, keys: str = None) -> dict:
        """
        description: Get the setting

        params:
            key: str - The key of the setting

        return: dict
        """

        path = "/api/admin/setting"
        headers = {"Authorization": self.auth}
        if key:
            query = {"key": key}
        elif keys:
            query = {"keys": keys}
        else:
            query = None

        async with self.session.get(f"{self.url}{path}", headers=headers, params=query) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def save_setting(self, settings: list[dict]) -> dict:
        """
        description: Save the setting

        params:
            settings: list[dict] - The list of the settings

        return: dict
        """

        path = "/api/admin/setting/save"
        headers = {"Authorization": self.auth}
        body = {"settings": settings}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

