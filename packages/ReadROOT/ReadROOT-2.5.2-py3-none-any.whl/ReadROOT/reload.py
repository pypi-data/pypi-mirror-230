from datetime import datetime
import time, shutil, os
version_date = datetime.now().strftime('%Y/%m/%d')
version_number = "2.5.2"

with open("READme.md", "r") as f:
    read_me = f.readlines()

with open("setup.py", "r") as f:
    setup = f.readlines()

with open("read_root_gui_v2.py", "r") as f:
    guiv2 = f.readlines()

with open("__init__.py", "r") as f:
    init = f.readlines()

read_me_version_date = f"**Current version date :** {version_date}\n"
# read_me_version_number = f"**Version =** {version_number}\n"
read_me[2] = read_me_version_date
# read_me[4] = read_me_version_number

setup[0] = f'__version__ = "{version_number}"\n'

guiv2[2] = f"# Current version date : {version_date}\n"
guiv2[3] = f"# Version = {version_number}\n"

init[6] = f"__version__ = '{version_number}'\n"

with open("READme.md", "w") as f:
    f.writelines(read_me)    

with open("setup.py", "w") as f:
    f.writelines(setup)

with open("read_root_gui_v2.py", "w") as f:
    f.writelines(guiv2)

with open("__init__.py", "w") as f:
    f.writelines(init)

dirs_to_del = ["dist","build","ReadROOT.egg-info"]
for item in os.listdir():
    if item in dirs_to_del:
        shutil.rmtree(item)
