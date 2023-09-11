import os
import re
import sys

import click

from huhk import allure_bat
from huhk.case_project.version import version as _version
from huhk.init_project import GetApi


def get_version():
    k = str(GetApi.get_service_value("this_key"))
    v = str(GetApi.get_service_value("this_name"))
    out_str = f"版本：{_version}\n--key：{k}\n--name：{v}"
    return out_str


def set_key_name(key, name):
    if key and name:
        GetApi.set_service_value("this_key", key)
        GetApi.set_service_value("this_name", name)
    elif key or name:
        key_list = GetApi.get_key_name_list()
        if key:
            GetApi.set_service_value("this_key", key)
            if key_list.get(key):
                GetApi.set_service_value("this_name", key_list.get(key))
        else:
            if key_list.get(name):
                GetApi.set_service_value("this_key", key_list.get(name))
            GetApi.set_service_value("this_name", name)
    return True


def install_project(app_key, name=None):
    ga = GetApi(name=name, app_key=app_key)
    ga.create_or_update_project()
    set_key_name(app_key, name)
    return "项目创建成功"


def update_project(app_key=None, name=None):
    set_key_name(app_key, name)
    app_key = GetApi.get_service_value("this_key")
    name = GetApi.get_service_value("this_name")
    if not app_key and not name:
        return "项目未指定，请指定参数-k/-n"
    else:
        ga = GetApi(name=name, app_key=app_key)
        ga.create_or_update_project()
        return "项目更新成功"


def fun_project(app_key=None, name=None, fun_url=None, method=None):
    set_key_name(app_key, name)
    app_key = GetApi.get_service_value("this_key")
    name = GetApi.get_service_value("this_name")
    if not app_key and not name:
        return "项目未指定，请指定参数-k/-n"
    else:
        ga = GetApi(name=name, app_key=app_key)
        methods = {1: "GET", 2: "POST", 3: "PUT", 4: "DELETE",
                   5: "HEAD", 6: "OPTIONS", 7: "PATCH", 8: "CONNECT"}
        while not method:
            method = input("输入方法类型（回车默认：get）：")
            if method == "":
                method = "GET"
            elif method.isdigit() and int(method) < 9:
                method = methods[int(method)]
            elif method.upper() in methods.values():
                method = method.upper()
            else:
                print(f"""输入类型错误，请重新输入：{methods}""")
                method = None
        if method == "POST":
            headers_list = {0: {"Content-Type": "application/json"},
                            1: {"Content-Type": "application/x-www-form-urlenc"},
                            2: {"Content-Type": "multipart/form-data"},
                            3: {"Content-Type": "text/xml"}}
            while not headers:
                headers = input("输入post请求类型（回车默认：application/json）：")
                if method == "":
                    headers = headers_list[0]
                elif method.isdigit() and int(method) < 4:
                    headers = headers_list[int(method)]
                else:
                    try:
                        headers = eval(headers)
                    except:
                        print(f"""输入类型错误，请重新输入\n""")
                        headers = None

        return "方法添加/更新成功"


def running_testcase(running, case_path=None, report_path=None):
    running_path_list = []
    for cases in running:
        for case in re.split(r'[，,;；\s]+', cases):
            running_path = GetApi.get_running_path(case, case_path)
            if running_path:
                running_path_list.append(running_path)
            else:
                if case:
                    print(f"用例文件\"{case}\"不存在")
    if running_path_list:
        report_path, report_html = GetApi.get_report_json(report_path)
        running_setting = ["-s", "-v", "--alluredir", report_path, "-p", "no:warnings", "--cache-clear",
                              "--reruns=1", "--reruns-delay=1", "--instafail", "--tb=line"]
        cmd_str = "%s -m pytest %s" % (sys.executable, " ".join(running_path_list + running_setting))
        print(cmd_str)
        os.system(cmd_str)

        if sys.platform == "win32":
            cmd_str = f"call {allure_bat} generate {report_path} -c -o {report_html}"
        else:
            cmd_str = f"allure generate {report_path} -c -o {report_html}"
        print(cmd_str)
        os.system(cmd_str)
        if not case_path and not report_path and sys.platform == "win32":
            os.system(f"call {allure_bat} open {report_html}")
        return "执行用例完成"
    else:
        return "无可执行用例文件"


if __name__ == '__main__':
    install_project('fd4f904b-086b-4b6d-9da7-aa6d0c9238f9')
#     running_testcase(["""ddzx/web
# ddzx/api
# yhzx/web
# mdzx/web/top
# app_a/order/mainorder/test_order_mainorder_pagelist.py
# app_a/order/mainorder/test_order_mainorder_download.py
# app_a/order/mainorder/test_order_mainorder_detail.py
# app_a/order/testdrive
# app_a/goods/ordermain
# app_a/goods/testdrive"""],
#                      case_path=r"D:\projects\python_test\ardar_test\autotest\codes\1\testcase",
#                      report_path=r"D:\projects\python_test\ardar_test\static\media\report\50")