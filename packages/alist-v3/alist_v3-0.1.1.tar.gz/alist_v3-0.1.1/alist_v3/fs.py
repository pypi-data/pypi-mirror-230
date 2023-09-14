from .auth import Auth, aiohttp
import os

class Fs(Auth):
    """ABOUT FS"""

    def __init__(self, usr: str, pwd: str, url: str = "http://127.0.0.1", port: int = 5244):
        super().__init__(usr, pwd, url, port)


    async def post_mkdir(self, fspath: str) -> dict:
        """
        description: Create a directory

        params: 
            fspath: str - The path of the directory to create

        return: dict
        """

        path = "/api/fs/mkdir"
        headers = {"Authorization": self.auth}
        body = {"path": fspath}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_rename(self, name, fspath) -> dict:
        """
        description: Rename a file or a directory
        
        params:
            name: str - The new name of the file or directory
            fspath: str - The path of the file or directory to rename

        return: dict
        """

        path = "/api/fs/rename"
        headers = {"Authorization": self.auth}
        body = {"name": name, "path": fspath}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def put_from(self, fspath: str) -> dict:
        """
        description: Upload a file from a path

        params:
            fspath: str - The path of the file to upload

        return: dict
        """

        path = "/api/fs/from"
        url = f"{self.url}{path}"
        headers = {
            "Authorization": self.auth,
            "Content-Type": "multipart/form-data",
            "File-Path": fspath,
            "Content-Length": str(os.path.getsize(fspath))
        }
        data = aiohttp.FormData()
        data.add_field("file", open(fspath, "rb"))
        async with self.session.put(url, headers=headers, data=data) as resp:
            resp.raise_for_status()
            response_text = await resp.text()
            return response_text
        

    async def post_list(self, fspath: str, password: str = None, page: int = None, per_page: int = None, refresh: bool = None) -> dict:
        """
        description: List the files of a directory
        
        params:
            fspath: str - The path of the directory to list
            password: str - The password of the directory
            page: int - The page of the list
            per_page: int - The number of files per page
            refresh: bool - Refresh the list

        return: dict
        """

        path = "/api/fs/list"
        headers = {"Authorization": self.auth}
        body = {"path": fspath, "password": password, "page": page, "per_page": per_page, "refresh": refresh}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_fsmsg(self, fspath: str = None, password: str = None) -> dict:
        """
        description: Get the message of a directory

        params:
            path: str - The path of the directory
            password: str - The password of the directory

        return: dict
        """ 

        path = "/api/fs/get"
        headers = {"Authorization": self.auth}
        body = {"path": fspath, "password": password}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_rearch(self, parent: str, keyword: str, scope: int, page: int, per_page: int, password: str = None) -> dict:
        """
        description: Search a file or a directory

        params:
            parent: str - The path of the parent directory
            keyword: str - The keyword to search
            scope: int - The scope of the search
            page: int - The page of the search
            per_page: int - The number of files per page
            password: str - The password of the directory

        return: dict
        """

        path = "/api/fs/search"
        headers = {"Authorization": self.auth}
        body = {"parent": parent, "keyword": keyword, "scope": scope, "page": page, "per_page": per_page, "password": password}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_dirs(self, fspath: str, password: str = None, force_root: bool = False) -> dict:
        """
        description: Get the directories of a directory

        params:
            fspath: str - The path of the directory
            password: str - The password of the directory
            force_root: bool - Force to get the root directories

        return: dict
        """

        path = "/api/fs/dirs"
        headers = {"Authorization": self.auth}
        body = {"path": fspath, "password": password, "force_root": force_root}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_batch_rename(self, src_dir: str, rename_obj: list[dict]) -> dict:
        """
        description: Batch rename files or directories

        params:
            src_dir: str - The path of the directory
            rename_obj: list[dict] - The list of the rename objects

        return: dict

        example:
            rename_obj = [{
                        "src_name": "test.txt",
                        "new_name": "aaas2.txt"
                        },]
        """

        path = "/api/fs/batch/rename"
        headers = {"Authorization": self.auth}
        body = {"src_dir": src_dir, "rename_obj": rename_obj}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_move(self, src_dir: str, dst_dir: str, names: list[str]) -> dict:
        """
        description: Move a file or a directory

        params:
            src_dir: str - The path of the source directory
            dst_dir: str - The path of the destination directory
            names: list[str] - The list of the names of the files or directories to move

        return: dict
        """

        path = "/api/fs/move"
        headers = {"Authorization": self.auth}
        body = {"src_dir": src_dir, "dst_dir": dst_dir, "names": names}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def post_recursive_move(self, src_dir: str, dst_dir: str) -> dict:
        """
        description: Move a directory recursively

        params:
            src_dir: str - The path of the source directory
            dst_dir: str - The path of the destination directory

        return: dict
        """

        path = "/api/fs/recursive_move"
        headers = {"Authorization": self.auth}
        body = {"src_dir": src_dir, "dst_dir": dst_dir}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_copy(self, src_dir: str, dst_dir: str, names: list[str]) -> dict:
        """
        description: Copy a file or a directory

        params:
            src_dir: str - The path of the source directory
            dst_dir: str - The path of the destination directory
            names: list[str] - The list of the names of the files or directories to copy

        return: dict
        """

        path = "/api/fs/copy"
        headers = {"Authorization": self.auth}
        body = {"src_dir": src_dir, "dst_dir": dst_dir, "names": names}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_remove(self, dir: str, names: list[str]) -> dict:
        """
        description: Remove a file or a directory

        params:
            dir: str - The path of the directory
            names: list[str] - The list of the names of the files or directories to remove

        return: dict
        """

        path = "/api/fs/remove"
        headers = {"Authorization": self.auth}
        body = {"path": dir, "names": names}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    
    async def post_remove_empty_directory(self, src_dir: str) -> dict:
        """
        description: Remove an empty directory

        params:
            dir: str - The path of the directory

        return: dict
        """

        path = "/api/fs/remove_empty_directory"
        headers = {"Authorization": self.auth}
        body = {"path": src_dir}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_add_aria2(self, urls: list[str], path: str) -> dict:
        """
        description: Add a download task to aria2

        params:
            urls: list[str] - The list of the urls to download
            path: str - The path of the directory to download

        return: dict
        """

        path = "/api/fs/add_aria2"
        headers = {"Authorization": self.auth}
        body = {"urls": urls, "path": path}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()
        

    async def post_add_qbit(self, urls: list[str], path: str) -> dict:
        """
        description: Add a download task to qBittorrent

        params:
            urls: list[str] - The list of the urls to download
            path: str - The path of the directory to download

        return: dict
        """

        path = "/api/fs/add_qbit"
        headers = {"Authorization": self.auth}
        body = {"urls": urls, "path": path}

        async with self.session.post(f"{self.url}{path}", json=body, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    