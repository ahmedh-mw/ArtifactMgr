import os
import stat                 # retrieve os file stat
import sys                  # detect python version
import shutil               # os folder management
import getpass              # retrieve current user information
# from retry import retry     # retry feature
import hashlib              # clculate file_checksum
import multiprocessing      # support multiprocessing pool
import logging

logger = logging.getLogger()

###############################################################################
#            Listing 
###############################################################################
def list_folder_files(folder_path):
    """Recursively lists all files in a folder"""
    file_list = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_list.append(file_path)
    return file_list

###############################################################################
#            Permissions management 
###############################################################################
def remove_current_user_write_access(file_path):
    current_uid = getpass.getuser() if os.name == 'nt' else os.getuid()
    file_owner = getpass.getuser() if os.name == 'nt' else os.stat(file_path).st_uid
    current_file_mode = os.stat(file_path).st_mode
    if current_uid == file_owner:
        new_file_mode = current_file_mode & ~stat.S_IWUSR        # clear write by owner permission
    else:
        new_file_mode = current_file_mode & ~stat.S_IWOTH        # clear write by others permission
    os.chmod(file_path, new_file_mode)
    
def add_current_user_write_access(file_path):
    current_uid = getpass.getuser() if os.name == 'nt' else os.getuid()
    file_owner = getpass.getuser() if os.name == 'nt' else os.stat(file_path).st_uid
    current_file_mode = os.stat(file_path).st_mode
    if current_uid == file_owner:
        new_file_mode = current_file_mode | stat.S_IWUSR        # add owner write permission
    else:
        new_file_mode = current_file_mode | stat.S_IWOTH        # add others write permission
    os.chmod(file_path, new_file_mode)

def set_execute_flag(src_file):
    if(os.path.isfile(src_file)):
        logger.debug(f"Set Execute flag for: {src_file}")
        if os.name != 'nt':
            new_file_mode = os.stat(src_file).st_mode | stat.S_IXUSR | stat.S_IXOTH
            os.chmod(src_file, new_file_mode)
    else:
        logger.warning(f"Set Execute flag for, file not found: {src_file}")

def set_owner_write_permission(func, path, excinfo):
    os.chmod(path, stat.S_IWUSR)         # set owner write permission
    func(path)

def set_permissions_recursive(src_folder_path, permissions):
    for root, dirs, files in os.walk(src_folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            os.chmod(file_path, permissions)
###############################################################################
#            File/folder basic operations
############################################################################### 
def delete_file(file_path):
    if(os.path.isfile(file_path)):
        logger.debug(f"Deleting file: {file_path}")
        os.chmod(file_path, stat.S_IWUSR)
        os.remove(file_path)
    else:
        logger.debug(f"File not found: {file_path}")

def add_file(file_path, content, override=True):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if override or not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            logger.debug(f"Adding file: {file_path}")
            file.write(content)
    else:
        logger.debug(f"File already exists: {file_path}")

def delete_folder(directory_path):
    if(os.path.isdir(directory_path)):
        logger.debug(f"Deleting folder: {directory_path}")
        shutil.rmtree(directory_path, onerror=set_owner_write_permission)
    else:
        logger.debug(f"Folder not found: {directory_path}")

def create_folder(directory_path):
    if(os.path.isdir(directory_path)):
        logger.debug(f"Folder already exists: {directory_path}")
    else:
        logger.debug(f"Creating folder: {directory_path}")
        os.makedirs(directory_path, exist_ok=True)
        
def rename_folder(src, dest):
    if( os.path.exists(dest) ):
        logger.debug(f"Folder with the same name already exists: {dest}")
    else:
        if(os.path.isdir(src)):
            logger.info(f"Renaming folder.... from: {src} >>>>>> to: {dest}")
            os.rename(src, dest)
        else:
            logger.debug(f"Folder not found: {src}")

def move_merge_folder_content(src, dest):
    if(os.path.isdir(src)):
        logger.debug(f"Moving folder content.... from: {src} >>>>>> to: {dest}")
        for root, _, files in os.walk(src):
            relative_path = os.path.relpath(root, src)
            destinationFileDir = os.path.join(dest, relative_path)
            os.makedirs(destinationFileDir, exist_ok=True)
            for file in files:
                srcItem_path = os.path.join(root, file)
                destItem_path = os.path.join(destinationFileDir, file)
                if os.path.exists(destItem_path):
                    os.remove(destItem_path)
                shutil.move(srcItem_path, destItem_path)

def move_folder(src, dest):
    if(os.path.isdir(src)):
        logger.debug(f"Moving folder.... from: {src} >>>>>> to: {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
    else:
        logger.debug(f"Folder not found: {src}")

def copy_folder(src, dest):
    if(os.path.isdir(src)):
        logger.debug(f"Copying folder.... from: {src} >>>>>> to: {dest}")
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        logger.debug(f"Folder not found: {src}")

def copy_file(src, dest):
    if(os.path.isfile(src)):
        logger.debug(f"Copying file.... from: {src} >>>>>> to: {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)
    else:
        logger.debug(f"File not found: {src}")

def move_file(src, dest):
    if(os.path.isfile(src)):
        logger.debug(f"Moving file.... from: {src} >>>>>> to: {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
    else:
        logger.debug(f"File not found: {src}")
###############################################################################
#            File/folder advancaed operations
###############################################################################
def move_paths(src, dest, paths_list):
    for path in paths_list:
        src_full_path = os.path.join(src, path)
        dest_full_path = os.path.join(dest, path)
        if(os.path.isdir(src_full_path)):
            move_folder(src_full_path, dest_full_path)
        else:
            move_file(src_full_path, dest_full_path)

def copy_paths(src, dest, paths_list):
    for path in paths_list:
        src_full_path = os.path.join(src, path)
        dest_full_path = os.path.join(dest, path)
        if(os.path.isdir(src_full_path)):
            copy_folder(src_full_path, dest_full_path)
        elif (os.path.isfile(src_full_path)):
            copy_file(src_full_path, dest_full_path)

###############################################################################
#            Checksum functions 
###############################################################################
def file_checksum(file_path):
    """Calculates the SHA-256 checksum of a file"""
    if(os.path.isfile(file_path)):
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha1()      # Using SHA-1, this is the same hashing used in digital thread
            chunk = f.read(4096)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(1)
        return file_hash.hexdigest()
    else:
        return None

def get_checksum_list(files_list):
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    checksum_results = pool.map(file_checksum, files_list)
    pool.close()
    pool.join()
    checksum_list = {}
    for i in range(len(files_list)):
        checksum_list[files_list[i]] = checksum_results[i]
    return checksum_list