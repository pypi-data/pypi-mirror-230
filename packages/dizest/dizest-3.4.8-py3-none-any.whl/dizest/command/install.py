from argh import arg, expects_obj
import os
import dizest
import season
import shutil
import git
import datetime

PATH_DIZEST_LIB = os.path.dirname(os.path.dirname(__file__))
PATH_BUNDLE = os.path.join(PATH_DIZEST_LIB, "bundle")
PATH_WORKING_DIR = os.getcwd()

@arg('dirname', default=None, help="dizest dirname")
def install(dirname):
    fs = dizest.util.os.storage(PATH_WORKING_DIR)
    if fs.exists(dirname):
        print("already exist directory")
        return

    if len(dirname) < 3:
        print("dirname must be at least 3 characters")
    
    fs.copy(PATH_BUNDLE, dirname)
    print(f"dizest installed at `{dirname}`")

def upgrade():
    fs = dizest.util.os.storage(PATH_WORKING_DIR)
    if fs.exists("project") == False:
        print("dizest not installed")
        return

    fs.remove("project")
    fs.copy(os.path.join(PATH_BUNDLE, "project"), "project")

    print("dizest upgraded")
