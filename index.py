import requests
import json
import threading
import pandas as pd
import numpy
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote

global Durl, Furl, ip_port, token, API_port, callback_port
Durl = 'http://localhost:9998/MyQQHTTPAPI'
Furl = 'http://localhost:9999/MyQQHTTPAPI'
ip_port = ('http://localhost:9999/MyQQHTTPAPI', 9999)
token = 666
API_port = 9998
callback_port = 9999


class Robot:  # 调用api类
    def __init__(self, function, token, params):
        self.function = function
        self.token = token
        self.params = params

    def POST_DO(self):
        data = {
            'function': self.function,
            'token': self.token,
            'params': self.params
        }
        Data = json.dumps(data)
        return requests.post(url=Durl, data=Data, verify=False).text


class MSG_callback(BaseHTTPRequestHandler):  # 回调类
    def handler(self):
        self.wfile.write(self.rfile.readline())

    def do_GET(self):
        data = {
            'result_code': '',
            'result_desc': 'Success',
            'timestamp': '',
            'data': {}
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        req_datas = self.rfile.read(int(self.headers['content-length']))
        recv_json = json.loads(req_datas)
        # print(recv_json)
        names = globals()
        names['%s_msg' % (str(recv_json['MQ_robot']))] = recv_json['MQ_msg']
        data = {
            'result_code': '',
            'result_desc': 'Success',
            'timestamp': '',
            'data': {}
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        if echo_mode:
            print(unquote(recv_json['MQ_msg']))
            Info_processing(recv_json)


class Pycode:  # 功能类
    def __init__(self, recv_json):
        self.recv_json = recv_json

    def Query_not_filled(self):  # 查询未填表人员,仅支持excel文档且
        pass

    def Random_person(self):  # 随机选人
        pass

    def Gather(self):  # 收集图片，并打包保存至服务器内
        pass

    def Timed_task(self):  # 定时任务
        pass

    def Colck_msg(self, xueyuan, zhuanye, banji):  # 查看打卡信息，需要教师的登录信息
        url = 'http://zhcx.scitc.com.cn/weixin/HealthTj_Student.php?YearName=2020&DepartName='+xueyuan+'&SpeciName='+zhuanye+'&ClassName='+ banji
        print(url)
        header = {
            'host': 'zhcx.scitc.com.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.16(0x18001030) NetType/WIFI Language/zh_CN',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'http://zhcx.scitc.com.cn/weixin/HealthTj_Student.php',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Cookie': '记得改这里',
            'X-Requested-With': 'com.tencent.mm',
            'Connection': 'close'
        }

        resp = requests.post(url, headers=header)
        index = pd.read_html(resp.text)[3]
        resp.close()
        data_array = numpy.array(index)
        data = []
        for i in data_array:
            try:
                if numpy.isnan(i[3]):
                    data.append(i[1])
            except:
                pass
        if len(data):
            return data
        else:
            return "均打卡完成"


def Info_processing(recv_json):  # 消息处理函数
    if unquote(recv_json['MQ_msg']) == '菜单':
        data = {
            'c1': '3574515911',
            'c2': 1,
            'c3': '',
            'c4': '2270545457',
            'c5': '测试菜单指令！！！'
        }
        Robot('Api_SendMsg', token, data).POST_DO()

    if '查看打卡情况' in unquote(recv_json['MQ_msg']):
        index = unquote(recv_json['MQ_msg']).split("+")
        print(index)
        zhuanye = index[2]
        print(zhuanye)
        banji = index[3]
        print(banji)
        xueyuan = index[1]
        print(xueyuan)
        data = {
            'c1': '3574515911',
            'c2': 2,
            'c3': recv_json['MQ_fromID'],
            'c4': recv_json['MQ_fromQQ'],
            'c5': Pycode(recv_json).Colck_msg(xueyuan, zhuanye, banji)
        }
        Robot('Api_SendMsg', token, data).POST_DO()


'''    if unquote(recv_json['MQ_msg']) in 'pic={':
        b = recv_json['MQ_msg']
        a = "}"
        s = re.split(a, b)
        a = "{"
        s = re.split(a, s[0])
        data = {
            'c1': '3574515911',
            'c2': 2,
            'c3': recv_json['MQ_fromQQ'],
            'c4': s
        }
        print(Robot('Api_GetPicLink', token, data).POST_DO())'''


def start_httpserver(callback_port):
    http_server = HTTPServer(('', callback_port), MSG_callback)
    http_server.serve_forever()


def global_set():
    a = threading.Thread(name='MQ_gbalsten', target=start_httpserver, args=(callback_port,))
    Running_ThreadingList.append(a)
    a.start()


def debug(token):
    data = {
        'c1': '3574515911',
        'c2': 1,
        'c3': '',
        'c4': '2270545457',
        'c5': 'hello word debug！！！'

    }
    Robot('Api_SendMsg', token, data).POST_DO()


if __name__ == '__main__':
    # debug(token)
    echo_mode = True  # 是否开启回调开关，实际上就是一个显示问题
    Running_ThreadingList = []  # 删掉会报错，能跑就行
    global_set()
