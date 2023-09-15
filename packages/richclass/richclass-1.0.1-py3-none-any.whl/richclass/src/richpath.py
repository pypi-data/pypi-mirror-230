from enum import Enum, auto as enumAuto
from pathlib import Path
from logging import Logger

class RichPathType(Enum):
    DIRECTORY = enumAuto()
    FILE = enumAuto()

class RichPath:

    def detect(self) -> bool:

        # Error check presence of directory / file
        if self.path_str is not None:
            
            if self.type == RichPathType.DIRECTORY:
                if not self.path_obj.is_dir():
                    self.present = False
                    if self.required:
                        if self.logging_en:
                            self.logger.error(f"Required directory missing at: {self.path_str}")
                        raise FileNotFoundError(f"Required directory missing at: {self.path_str}")
                    else:
                        if self.logging_en:
                            self.logger.warning(f"Directory missing at: {self.path_str}")
                else:
                    self.present = True
                
            elif self.type == RichPathType.FILE:
                if not self.path_obj.is_file():
                    self.present = False
                    if self.required:
                        if self.logging_en:
                            self.logger.error(f"Required directory missing at: {self.path_str}")
                        raise FileNotFoundError(f"Required directory missing at: {self.path_str}")
                    else:
                        if self.logging_en:
                            self.logger.warning(f"Directory missing at: {self.path_str}")
                else:
                    self.present = True

        return self.present
    
    def update_path_str(self, new_path_str : str) -> bool:
        self.path_str = new_path_str
        self.path_obj = Path(new_path_str)

        if self.logging_en:
            self.logger.debug(f"path_str update: , {self.path_str}, {self.path_obj}")

        self.detect()

    def update_path_obj(self, new_path_obj : Path) -> bool:
        self.path_obj = new_path_obj
        self.path_str = str(new_path_obj)

        if self.logging_en:
            self.logger.debug(f"path_obj update: , {self.path_str}, {self.path_obj}")

        self.detect()

    def __init__(self, type : RichPathType, path_obj : Path = None, path_str : str = None, req : bool = False, logger : Logger = None):
        
        self.logging_en = True if logger is not None else False
        self.type = type
        self.logger = logger
        self.required = req

        err_message = ""
        # Error check PathType input
        if self.type.__class__ is not RichPathType:
            err_message = "Path type must be of RichPathType class enum object"
        elif self.type not in RichPathType:
            err_message = "Path type enum value is not in RichPathType class enum object"

        if err_message != "":
            err_message = f"Incorrect path type defined: {self.type}, err: {err_message}"
            if self.logging_en:
                self.logger.critical(err_message)
            raise TypeError(err_message)
        
        # Set path string and Path object
        if path_obj is not None:
            self.update_path_obj(path_obj)
        elif path_str is not None:
            self.update_path_str(path_str)
        else:
            self.update_path_str("")

        if self.logging_en:
            self.logger.debug(f"PathElement object initialized: {str(self)}")
    
    def __str__(self) -> str:
        return f"{self.__class__} object, path {self.path_str}, present: {self.present}"