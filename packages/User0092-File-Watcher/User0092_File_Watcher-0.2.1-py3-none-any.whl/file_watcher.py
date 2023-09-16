import asyncio
import typing
import time
import os


class FileEventWatcherException(Exception):
    pass


class FileEventWatcher:
    """
    callback_args (str)
        The callback arguments must be sorted in the order they are used in the callback.
        Multiple arguments are separated by "&": "%fp & %fn" (Spaces are allowed, not necessary)
        Valid arguments:
            %f  -> returns the full name of the file (name.extension)
            %fp -> inserts the file path
            %fn -> inserts the file name
            %fe -> inserts the file extension
            %fr -> inserts the file root
        
        defaults to ""
    """
    def __init__(self, directory: str, *, callback: typing.Callable, callback_args: str = "", sleep_time: float=1, include_sub_directories: bool = False, loop = None):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise FileEventWatcherException(f"File does not exist or is not a directory. {directory}")
        
        cb_args: list = list()
        for arg in callback_args.replace(" ", "").split("&"):
            if arg not in {"f", "%fp", "%fn", "%fe", "%fr"}:
                raise FileEventWatcherException(f"Invalid callback argument {arg}.")
            cb_args.append(arg)
        
        self.directory: str = os.path.abspath(directory)
        self.callback: typing.Callable = callback
        self.sleep_time: float = sleep_time
        self.include_sub_directories: bool = include_sub_directories
        self.loop = loop or asyncio.new_event_loop()
        self.last_check = time.time()
        self.callback_args: tuple = tuple(cb_args)
        self.ignore_files: list = ["desktop.ini"]
    
    def watch(self):
        self.loop.run_until_complete(self._watcher())
    
    def list_files(self, directory: str) -> set:
        files = set()
        
        for file in os.listdir(directory):
            if file in self.ignore_files:
                continue

            path = os.path.join(directory, file)

            if os.path.isdir(path):
                for file in self.list_files(path):
                    files.add(file)
            else:
                if os.path.getmtime(path) <= self.last_check:
                    continue
                files.add(path)
        
        return files
    
    def get_file_info(self, file: str) -> dict:
        file_path = file.replace("\\", "/")
        file = file_path.split("/")[-1]
        file_name = ".".join(file.split(".")[:-1])

        if file.count(".") > 0:
            extension = file.split(".")[-1]
        else:
            extension = ""
        
        root = "/".join(file_path.split("/")[:-1])

        return {
            "file_path": file_path,
            "file": file,
            "file_name": file_name,
            "extension": extension,
            "root": root
        }
    
    def send_callback(self, file: str) -> None:
        values = self.get_file_info(file)
                    
        args_to_value = {
            r"%f": values["file"],
            r"%fp": values["file_path"],
            r"%fn": values["file_name"],
            r"%fe": values["extension"],
            r"%fr":values["root"]
        }
        
        args: list = list()
        for argument in self.callback_args:
            args.append(args_to_value[argument])
            
        self.callback(*args)

    async def _watcher(self):
        while True:
            files = self.list_files(self.directory)
            self.last_check = time.time()
            
            if len(files) > 0:
                for file in files:
                    self.send_callback(file)
            
            await asyncio.sleep(self.sleep_time)

"""
Example:

def c(*args) -> None:
    print(args)

FileEventWatcher("./", callback=c, callback_args="%fp & %fn & %fe & %fr").watch()
"""
