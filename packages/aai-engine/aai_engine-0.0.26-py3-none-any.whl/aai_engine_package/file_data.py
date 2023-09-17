"""FileData class"""

class FileData():
    """
    FileData class that reads and accesses data from a set of supported files.
    For example a csv style excel can be easily read an accessed.
    """
    def __init__(self, file_path, file_format):
        self.file_path = file_path
        self.file_format = file_format
