import os
import re
import sys

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


def fun_project(app_key=None, name=None):
    set_key_name(app_key, name)
    app_key = GetApi.get_service_value("this_key")
    name = GetApi.get_service_value("this_name")
    if not app_key and not name:
        return "项目未指定，请指定参数-k/-n"
    else:
        ga = GetApi(name=name, app_key=app_key)
        while True:
            url = input("请输入url（带参数默认get）：")
            if url.strip():
                row = ga.get_api_old(url)
                url = row.path
                api_tag = row.title.split(":")[0].strip() if ":" in row.title else ""
                api_name = row.title.split(":")[-1].strip() if row.title else ""
                break
        if "?" in url:
            method = "GET"
        else:
            methods = {1: "GET", 2: "POST", 3: "PUT", 4: "DELETE",
                       5: "HEAD", 6: "OPTIONS", 7: "PATCH", 8: "CONNECT"}
            print("method枚举：" + str(methods))
            while True:
                method = input(f"输入方法类型（回车默认：{row.method or 'GET'}）：")
                if not method.strip():
                    method = row.method or 'GET'
                elif method.isdigit() and int(method) < 9:
                    method = methods.get(int(method))
                elif method.upper() in methods.values():
                    method = method.upper()
                else:
                    method = None
                if method:
                    break
        if method in ("POST", "PUT"):
            headers_list = {1: {"Content-Type": "application/json"},
                            2: {"Content-Type": "application/x-www-form-urlenc"},
                            3: {"Content-Type": "multipart/form-data"},
                            4: {"Content-Type": "text/xml"}}
            print("Content-Type枚举：" + str(headers_list))
            while True:
                headers = input(f"输入post请求类型（回车默认：{row.headers or 'application/json'}）：")
                if not headers.strip():
                    headers = row.headers or headers_list[1]
                elif method.isdigit() and int(headers) < 4:
                    headers = headers_list.get(int(headers))
                else:
                    try:
                        headers = eval(headers)
                        if isinstance(headers, dict):
                            break
                    except:
                        headers = None
                if headers:
                    break
        else:
            headers = {}

        if "?" not in url:
            data = input("输入请求参数（回车默认：无参数）：")
        else:
            data = url.split("?", 1)[1]

        while True:
            api_tag1 = input(f"输入：二级模块（回车默认：{api_tag}）：")
            if not api_tag1.strip():
                api_tag1 = api_tag
            if api_tag1.strip():
                break
        while True:
            api_name1 = input(f"输入：接口描述（回车默认：{api_name}）：")
            if not api_name1.strip():
                api_name1 = api_name
            if api_name1.strip():
                break
        name = api_tag1 + ": " + api_name1
        if row:
            while True:
                add_type = input("选择本次更新(回车默认1)：1：全覆盖更新，2：追加参数更新，3：增量覆盖")
                if add_type.strip() in ("1", "2", "3", ""):
                    add_type = add_type.strip() or "1"
                    break
        else:
            add_type = "1"
        if add_type == "1":
            ga.write_api_cover(url, method=method, data=data, headers=headers, name=name)
        elif add_type == "2":
            ga.write_api_add(url, method=method, data=data, headers=headers, name=name)
        elif add_type == "3":
            ga.write_api_cover_add(url, method=method, data=data, headers=headers, name=name)
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
    # install_project('fd4f904b-086b-4b6d-9da7-aa6d0c9238f9')
    fun_project(name="nrzx")
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