import os.path
import re

from huhk.case_project.project_base import ProjectBase
from huhk.unit_dict import Dict
from huhk.unit_fun import FunBase
from huhk import projects_path


class GetApi(ProjectBase):
    def __init__(self, name=None, app_key=None, yapi_url=None, yapi_token=None, yapi_json_file=None, swagger_url=None):
        super().__init__(name, app_key, yapi_url, yapi_token, yapi_json_file, swagger_url)

    def create_or_update_project(self, _update=False):
        """
        创建项目
        """
        # 创建项目目录
        self.set_file_path()
        # 获取已维护api方法接口列表
        self.get_this_fun_list()
        # 获取接口文档api接口列表
        self.get_api_list()
        # 添加api封装方法
        self.write_fun(_update=_update)

    def set_file_path(self):
        """创建项目框架"""
        FunBase.mkdir_file(self.path.values(), is_py=True)
        if not os.path.exists(os.path.join(self.path.service_dir, "__init__.py")) or \
                not FunBase.read_file(os.path.join(self.path.service_dir, "__init__.py")):
            FunBase.write_file(os.path.join(self.path.service_dir, "__init__.py"), value=self.get_init_value())
        if not os.path.exists(os.path.join(self.path.service_dir, f"{self.name}_fun.py")):
            FunBase.write_file(os.path.join(self.path.service_dir, f"{self.name}_fun.py"), value=self.get_fun_value())
        if not os.path.exists(os.path.join(self.path.service_dir, f"setting.json")):
            FunBase.write_file(os.path.join(self.path.service_dir, f"setting.json"), value="{}")
        if not os.path.exists(os.path.join(self.path.testcase_dir, f"conftest.py")):
            FunBase.write_file(os.path.join(self.path.testcase_dir, f"conftest.py"), value=self.get_conftest_value())

    def get_api_list(self):
        """根据api文档不同方式生成api文件"""
        if self.swagger_url:
            self.get_list_menu_swagger()
        elif self.yapi_url and self.yapi_token:
            self.get_list_menu()
        elif self.yapi_file_str or self.yapi_json_file:
            self.get_list_json()

    def write_fun(self, _update=False):
        if not self.this_fun_list.api and not self.api_list:
            self.api_list += [{'method': 'GET', 'title': '示例-get', 'path': '/demo/get', 'up_time': 1675665418},
                              {'method': 'POST', 'title': '示例-post', 'path': '/demo/post', 'up_time': 1675665418}]
        for row in self.api_list:
            self.write_api(row, _update=True)
        for fun_name in self.this_fun_list.api.keys():
            self.write_sql(fun_name, _update=_update)
            self.write_assert(fun_name, _update=_update)
            self.write_api_fun(fun_name, _update=_update)
            self.write_testcase(fun_name, _update=_update)

    def sub_hz(self, _id, _str):
        if re.findall(r'[^\da-zA-Z_\ (=,*):]', re.findall(r"def .*?\):", _str)[0]):
            api = self.get_api(_id)
            tmp2 = api.get('data', {}).get('req_params', [])
            for tmp3 in tmp2:
                name = tmp3.get('name', "")
                desc = tmp3.get('desc', "")
                if re.findall(r'[^\da-zA-Z_\ (=,*):]', name) and not re.findall(r'\W', desc):
                    _str = _str.replace(name, desc)
        if re.findall(r'[( ]async[,=)]', _str):
            for tmp in re.findall(r'[( ]async[,=)]', _str):
                tmp1 = str(tmp).replace('async', 'async1')
                _str = _str.replace(tmp, tmp1)
        return _str

    @staticmethod
    def get_testcase_path():
        testcase_path = GetApi.get_service_value("testcase_path")
        if not testcase_path or not os.path.exists(testcase_path):
            testcase_path = os.path.join(ProjectBase._get_project_dir(), "testcase")
            GetApi.set_service_value("testcase_path", testcase_path)
        return testcase_path

    @staticmethod
    def get_report_path():
        report_dir = os.path.join(ProjectBase._get_project_dir(), "report", FunBase.data_str())
        FunBase.mkdir_file(report_dir, is_py=False)
        report_path = os.path.join(report_dir, "%03d_%s" % (len(os.listdir(report_dir)) + 1, FunBase.time_str("%H%M%S")))
        FunBase.mkdir_file(report_path, is_py=False)
        return report_path

    @staticmethod
    def get_report_json(report_path=None):
        report_dir = report_path or GetApi.get_report_path()
        path = os.path.join(report_dir, "json")
        path2 = os.path.join(report_dir, "report_html")
        FunBase.mkdir_file([path, path2], is_py=False)
        return path, path2

    @staticmethod
    def get_key_name_list(path=None):
        out = Dict()
        path = path or projects_path
        for dirpath, dirnames, filenames in os.walk(path):
            if "apis" in dirnames and "asserts" in dirnames and "funs" in dirnames and "sqls" in dirnames \
                    and "__init__.py" in filenames:
                name = os.path.basename(dirpath)
                init_str = FunBase.read_file(os.path.join(dirpath, "__init__.py"))
                app_key = re.findall(r'\nAPP_KEY *= *[\'\"](.+)[\'\"]', init_str)
                app_key = app_key[0] if app_key else None
                if app_key:
                    out[name] = app_key
                    out[app_key] = name
                else:
                    out[name] = None
        if out:
            return out
        else:
            if os.path.exists(os.path.dirname(path)) and len(path) > 5:
                return GetApi.get_key_name_list(os.path.dirname(path))
        return out

    @staticmethod
    def get_running_path(path=None, testcase_dir=None):
        testcase_dir = testcase_dir or GetApi.get_testcase_path()
        if testcase_dir and path:
            path_list = [i for i in re.split(r"/|\\\\|\\", path) if i]
            for dirpath, dirnames, filenames in os.walk(testcase_dir):
                if path_list[0] in dirnames or path_list[0] in filenames:
                    if os.path.exists(os.path.join(dirpath, *path_list)):
                        return os.path.join(dirpath, *path_list)
                    elif len(path_list) > 1:
                        return GetApi.get_running_path(os.path.join(*path_list[1:]), os.path.join(dirpath, path_list[0]))
        return None


if __name__ == '__main__':
    ga = GetApi()
    print(ga.get_running_path("yhzx/web/drop"))