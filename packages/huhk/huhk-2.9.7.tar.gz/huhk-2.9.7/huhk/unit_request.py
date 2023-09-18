import copy
import re
import requests
import json
import time
import urllib
import os
import hashlib
import sys

from huhk.unit_fun import FunBase
from requests import ReadTimeout, ConnectTimeout
from requests.exceptions import MissingSchema
from urllib.parse import urlencode
from huhk.unit_dict import Dict
from huhk.unit_logger import logger
from openpyxl.reader.excel import load_workbook
from huhk import admin_host, projects_path


class UnitRequest:
    def __init__(self, ZEST_ENV=None, APP_KEY=None, TIMEOUT=30000):
        self.ZEST_ENV = ZEST_ENV
        self.APP_KEY = APP_KEY
        self.TIMEOUT = TIMEOUT
        self.variable = self.get_variable()

    @staticmethod
    def get_url(url, kwargs):
        tmp = re.findall(r'\{.+}', url)
        if not tmp:
            return url
        url = url.replace(tmp[0], str(kwargs.get(tmp[0][1:-1]) or ""))
        url = url.split('{')[0]
        return url

    @staticmethod
    def unit_http_requester(method, url, params=None, data=None, headers=None, host=None, timeout=10000,
                            init_headers=None,
                            _route="", _files=None, **kwargs):
        if headers.get("headers"):
            _headers = init_headers or {}
            tmp = headers.pop("headers")
            _headers.update(headers)
            if isinstance(tmp, dict):
                _headers.update(tmp)
        else:
            _headers = init_headers or {}
            _headers.update(headers)

        if url[0] == '/' and host:
            if _route and _route[0] != '/':
                _route = '/' + _route
            url = host + _route + url
        if method.upper() == "GET":
            params = params or data
        logger.info("接口请求参数method: %s, url: %s" % (method, url))
        logger.info("接口请求参数headers: %s" % str(_headers))
        logger.info("接口请求参数params: %s" % str(params)) if params else logger.info(
            "接口请求参数data: %s" % str(data))
        if "//" not in url:
            assert False, "url没有域名"
        time_s = time.time()
        try:
            if method.upper() == "GET":
                res = requests.request(method, url, params=params, json=data, headers=_headers,
                                       timeout=timeout / 1000,
                                       verify=False, cookies=kwargs.get('cookies', None))
            elif "application/x-www-form-urlencoded" in str(_headers):
                data = urlencode(data)
                res = requests.request(method, url, data=data, headers=_headers, timeout=timeout / 1000,
                                       verify=False)
            elif "multipart/form-data" in str(_headers) and "file" in data.keys():
                file = str(data.pop("file"))
                try:
                    if not os.path.isfile(file):
                        try:
                            out = requests.get(admin_host + '/files/file/', params={"value": file})
                            if "filename=" in str(out.raw.headers):
                                file_name = urllib.parse.unquote(re.findall(r'filename=(.+?)\'', str(out.raw.headers))[0])
                                file = os.path.join(projects_path, "files", file_name)
                                with open(file, 'wb') as f:
                                    f.write(out.content)
                        except:
                            pass
                        if os.path.join("autotest", "codes") in sys.argv[1]:
                            file_dir = os.path.join(*sys.argv[1].split(os.sep)[:3], "files", file)
                            file_dir2 = os.path.join(*sys.argv[1].split(os.sep)[:3], file)
                        else:
                            file_dir = os.path.join(projects_path, "files", file)
                            file_dir2 = os.path.join(projects_path, file)

                        if os.path.isfile(file):
                            pass
                        elif os.path.isfile(file_dir):
                            file = os.path.join(file_dir)
                        elif os.path.isfile(file_dir2):
                            file = file_dir2
                        else:
                            # assert False, "对应的文件不存在"
                            pass
                except Exception as e:
                    logger.error(str(e))
                try:
                    if file and file != "None":
                        data.update({'md5': hashlib.md5('%d_%d'.encode() % (0, int(time.time()))).hexdigest(),
                                     'filesize': len(open(file, 'rb').read()), })
                        _files = {"file": (os.path.basename(file), open(file, 'rb'))} if file else {}
                    else:
                        data.update({'file': file})
                        _files = None
                    try:
                        del _headers['Content-Type']
                    except:
                        pass
                except Exception as e:
                    logger.error(str(e))
                res = requests.request(method, url, params=params, data=data, files=_files,
                                       headers=_headers, timeout=timeout / 1000, verify=False,
                                       cookies=kwargs.get('cookies'))

            else:
                res = requests.request(method, url, params=params, json=data, headers=_headers,
                                       timeout=timeout / 1000,
                                       verify=False, cookies=kwargs.get('cookies', None))
            run_time = time.time() - time_s
            logger.info("接口响应时间: %.3f秒" % run_time)
            res.run_time = run_time
            try:
                res.rsp = Dict(json.loads(res.text)) if res.text else res.text
            except:
                if "filename=" in str(res.raw.headers):
                    file_name = urllib.parse.unquote(re.findall(r'filename=(.+?)\'', str(res.raw.headers))[0])
                    if "xlsx" in file_name:
                        file_path = os.path.join(projects_path, "files", file_name)
                        FunBase.mkdir_file(file_path, is_py=False)
                        with open(file_path, 'wb') as f:
                            f.write(res.content)
                        wb = load_workbook(file_path)
                        ws = wb.active
                        rows = [[cell.value for cell in row] for row in ws]
                        try:
                            data = [{c1: c2 for c1, c2 in zip(rows[0], row)} for row in rows[1:]]
                        except:
                            data = []
                        os.remove(file_path)
                        res.rsp = Dict({"code": 0, "data": data, "filename": file_name, "rows": rows})
                    else:
                        res.rsp = res.text
                else:
                    res.rsp = res.text
            logger.info("接口返回http_code: %s" % res.status_code)
            logger.info("接口数据res: %s" % str(res.rsp))
            return res
        except ReadTimeout:
            assert False, "接口响应时间%.3f秒, 超过设置的时间%.3f秒" % (time.time() - time_s, timeout / 1000)
        except ConnectTimeout:
            assert False, "接口响应时间%.3f秒, 超过设置的时间%.3f秒" % (time.time() - time_s, timeout / 1000)
        except MissingSchema:
            assert False, "url不对，无域名"
        except Exception as e:
            print(e)
            assert False, "调用接口报错"

    def get_variable(self, app_key=None, env=None):
        try:
            app_key = app_key or self.APP_KEY
            env = env or self.ZEST_ENV
            project = requests.post(admin_host + '/variable/variable/',
                                    json={"app_key": app_key, "environment": env}).json()
            _variable = {}
            for v in project.get('variables', []):
                if v.get('type') == 0:
                    _variable[v.get('name')] = v.get('value')
                elif v.get('type') == 1:
                    _variable[v.get('name')] = json.loads(v.get('value'))
                elif v.get('type') == 2:
                    _variable[v.get('name')] = int(json.loads(v.get('value')))
            _variable["_token"] = project.get("token")
            return _variable
        except:
            return {}

    def init_headers(self, **kwargs):
        headers = {"Content-Type": "application/json"}
        _host = kwargs.get("_host", "HOST")
        host = self.variable.get(_host) if "//" not in _host else _host
        if host:
            headers.update({"referer": host})
        _token = kwargs.get("_token", "TOKEN")
        token = self.variable.get(_token) if len(_token) < 20 else _token
        if not token and self.variable.get("_token"):
            token = self.variable.get("_token").get(_token)
            if not token:
                token = self.variable.get("_token").get("token")
        if token:
            headers.update({"authorization": token})
        return headers

    def http_requester(self, *args, **kwargs):
        _host = kwargs.get("_host", "HOST")
        host = self.variable.get(_host) if "//" not in _host else _host
        return self.unit_http_requester(*args, host=host, timeout=self.TIMEOUT,
                                        init_headers=self.init_headers(**kwargs), **kwargs)

    @staticmethod
    def is_assert_code_true(res, _assert=True):
        code = [0, 200, "0000", "00000", "0", "200", "000"]
        code_name = ["success", "ok", True, "OK", "Ok"]
        assert_dict = {"code": code, "result": code_name, "msg": code_name, "success": code_name,
                       "resultCode": code, "returnCode": code}
        if _assert is True:
            if res.status_code != 200:
                return False, f"接口返回http.status_code等于{res.status_code}, 不等于200"
            elif isinstance(res.rsp, dict):
                if set(res.rsp.keys()) & set(assert_dict.keys()):
                    for k, v in assert_dict.items():
                        if res.rsp.get(k) in v:
                            return True, "成功"
                    return False, "code字段都不等于成功值"
                else:
                    return True, "成功"
            else:
                return True, "成功"
        else:
            if res.status_code == _assert:
                return True, "成功"
            elif isinstance(res.rsp, dict):
                if set(res.rsp.keys()) & set(assert_dict.keys()):
                    for k, v in assert_dict.items():
                        if res.rsp.get(k) == _assert:
                            return True, "成功"
                    return False, "code字段都不等于成功" + str(_assert)
                else:
                    return False, "无code字段"
            else:
                return False, "失败"

    @staticmethod
    def is_assert_compare_status(res):
        def get_rsp(rsp):
            rsp = copy.deepcopy(rsp)
            try:
                if isinstance(rsp, dict):
                    rsp = dict(rsp)
            finally:
                if isinstance(rsp, (list, tuple)) and rsp:
                    return rsp[:1]
                elif isinstance(rsp, dict):
                    out = {}
                    for key, value in rsp.items():
                        if len(str(key)) == 1:
                            key = "X"
                        out[key] = get_rsp(value)
                    return out
                elif isinstance(rsp, str):
                    return (rsp[:20] + "......" + rsp[-20:]) if len(rsp) > 50 else rsp
                else:
                    return rsp


        try:
            url = admin_host + "/apilog/add_api_log/"
            try:
                body = json.loads(res.request.body)
            except:
                body = str(res.request.body)
            try:
                req = get_rsp(res.rsp)
            except:
                req = str(res.rsp)

            data = {"url": res.url.split("?")[0], "method": res.request.method,
                    "headers": dict(get_rsp(res.request.headers) or {}), "req_time": res.run_time,
                    "req_code": str(res.status_code),
                    "req": req,
                    "data": body}
            out = requests.post(url, json=data)
            out = out.json()
            return out.get("compare_status"), out.get("compare_msg") or ""
        except Exception as e:
            return False, "调用校验接口失败" + str(e)


if __name__ == '__main__':
    data = {"rsp": {'code': 0, 'msg': '成功！', 'data': {'appId': "1"}},
            "status_code": 200,
            "url": 'https://app-manage.test.radar-ev.com/manageapi/admin/spa/getAppId',
            "request": {"body": {},
                        "headers": {"Content-Type": "application/json"},
                        "method": "GET",
                        "path_url": '/manageapi/admin/spa/getAppId',
                        "url": 'https://app-manage.test.radar-ev.com/manageapi/admin/spa/getAppId'},
            "run_time": 2.1}
    print(UnitRequest.is_assert_compare_status(Dict(data)))