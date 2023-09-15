import shutil
import zipfile
from pathlib import Path


def zip_dir(zip_file_name: str, dir_path: str):
    dir_path_object = Path(dir_path)
    assert dir_path_object.is_dir(), "dir_path should be a directory"
    shutil.make_archive(
        base_name=zip_file_name, 
        format='zip', 
        root_dir=str(dir_path_object.parent.resolve()), 
        base_dir=str(dir_path_object.name)
    )
    
def unzip_file(zip_file_path: str, dest_dir_path: str):
    zip_file_path_object = Path(zip_file_path).resolve()
    dest_dir_path_object = Path(dest_dir_path).resolve()
    
    assert zip_file_path_object.is_file(), "zip_file_path should be a file"
    assert dest_dir_path_object.is_dir(), "dest_dir_path should be a directory"
    
    with zipfile.ZipFile(str(zip_file_path_object), 'r') as zip_ref:
        zip_ref.extractall(str(dest_dir_path_object))
