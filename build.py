import os
import shutil
import stat
import sys


def copytree(src, dst):
    #for each directory in source
    for item in os.listdir(src):
        #get source dir, and new dest dir for folder
        source_dir = os.path.join(src, item)
        dest_dir = os.path.join(dst, item)

        #if dir is game
        if item == 'game' and os.path.isdir(source_dir):
            #copy
            shutil.copytree(source_dir, dest_dir, False, None)


def handleError(func, path, exc_info):
    '''
    Error handler function
    It will try to change file permission and call the calling function again,
    https://thispointer.com/python-how-to-delete-a-directory-recursively-using-shutil-rmtree/
    '''
    print('Handling Error for files in folder ', path)
    # Check if file access issue
    if not os.access(path, os.W_OK):
       # Try to change the permision of file
       os.chmod(path, stat.S_IWUSR)
       # call the calling function again
       func(path)

def deleteWorlds(dst):
    #get world dir
    world_dir = os.path.join(dst, 'game\\worlds')
    #for each file in world dir
    for file in os.listdir(world_dir):
        #get path
        item_path = os.path.join(world_dir, file)
        #if dir
        if os.path.isdir(item_path):
            #delete tree/dir
            shutil.rmtree(item_path, onerror=handleError)
        #if file
        elif os.path.isfile(item_path):
            #delete file
            os.remove(item_path)

#get command line args
args = sys.argv

try:
    #get destination path from args
    destination = args[1]
except:
    raise Exception("No destination directory given")

print("Copying game dir...")
copytree('.',destination)

print("Deleting worlds...")
deleteWorlds(destination)

print("Complete...")