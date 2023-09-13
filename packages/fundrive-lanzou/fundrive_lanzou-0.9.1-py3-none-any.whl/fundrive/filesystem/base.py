class FileSystem:
    def __init__(self, *args, **kwargs):
        pass

    def login(self, *args, **kwargs):
        pass

    def mkdir(self, path, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def get_file_list(self, *args, **kwargs):
        pass

    def get_dir_list(self, *args, **kwargs):
        pass

    def get_file_info(self, *args, **kwargs):
        pass

    def get_dir_info(self, *args, **kwargs):
        pass

    def download_file(self, dir_path="./cache", overwrite=False, *args, **kwargs):
        pass

    def download_dir(self, dir_path="./cache", overwrite=False, *args, **kwargs):
        pass

    def upload_file(self, file_path="./cache", overwrite=False, *args, **kwargs):
        pass

    def upload_dir(self, dir_path="./cache", overwrite=False, *args, **kwargs):
        pass
