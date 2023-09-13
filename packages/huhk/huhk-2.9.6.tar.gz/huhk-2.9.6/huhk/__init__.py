import os
import sys
if sys.platform == 'win32':
    admin_host = "http://47.96.124.102/api"
else:
    admin_host = "http://127.0.0.1/api"
# admin_host = "http://127.0.0.1:8000/api"

projects_path = os.getcwd()
file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)
allure_bat = os.path.join(dir_path, "allure-2.23.1", "bin", "allure.bat")

projects_path_list = projects_path.split(os.path.sep)
if "site-packages" in projects_path_list and "huhk" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("site-packages") - 2])
elif "service" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("service")])
elif "testcase" in projects_path_list:
    projects_path = os.path.join(*projects_path_list[:projects_path_list.index("testcase")])
projects_path = projects_path.replace(":", ":\\")

