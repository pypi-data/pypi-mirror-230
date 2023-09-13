from huhk import projects_path, admin_host
from huhk.unit_dict import Dict
from huhk.unit_data import size_names, page_names, before_names, end_names, page_and_size


class ProjectInIt:
    def __init__(self, name=None, app_key=None, yapi_url=None, yapi_token=None, yapi_json_file=None, swagger_url=None):
        """api_type: 0时，value是swagger的api，json的url
                     1时，value值为yapi项目token,
                     2时，value是yapi下载的json文件名，文件放在file目录下,
                     3时，value是yapi的yapi-swagger.json
           name:项目名称，空时默认当前py文件所在文件名上级目录
        """
        self.path = Dict()
        self.path.dir = projects_path
        self.app_key = app_key
        self.name = name
        self.name2 = None
        self.name3 = ""
        self.yapi_url = yapi_url
        self.yapi_token = yapi_token
        self.yapi_json_file = yapi_json_file
        self.swagger_url = swagger_url
        self.url = admin_host
        self.yapi_file_str = None
        self.size_names = size_names
        self.page_names = page_names
        self.before = before_names
        self.end = end_names
        self.page_and_size = page_and_size
        self.this_file_list = Dict({"apis": []})
        self.this_fun_list = Dict()
        self.api_list = Dict()
        self.base_path = ""
