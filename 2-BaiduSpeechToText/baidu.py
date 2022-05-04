import sys
import json
import base64
import time
import os
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import ast
timer = time.perf_counter
import requests

API_KEY = ' '
SECRET_KEY = ' ' # 自行补充
TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'  # 接口功能URL
STT_URL = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/create' # 长文本的转写请求url
RATE = 16000
DEV_PID = 1737  # 1737英文，1537中文
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'
CUID = '123456PYTHON'
Format = ['pcm', 'wav', 'amr']
# stt_task_list = []

class DemoError(Exception):
    pass

# 格式转换
def converta(d=None):
    origin_path = d
    # new_path = d + f[:-4] + ".mp3"
    x = 3
    if (d[-5] == '.'):
        x = 4
    if (d[-4] == '.'):
        x = 3
    new_path = d[:-x] + "wav"
    os.system("ffmpeg -i " + origin_path + " " + new_path)
    return new_path

# 获取权限token
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params).encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read().decode()
    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']  # access token
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

"""  TOKEN end """

# 获取发送格式
def tok(file):
    if file[-3:] not in Format:
        readfile = converta(file)
    else :
        readfile = file
    with open(readfile, "rb") as speech_file:
        speech_data = speech_file.read()
    leng = len(speech_data)
    if (leng == 0):
        raise DemoError('file %s length read 0 bytes' % readfile)
    speech = str(base64.b64encode(speech_data), "utf-8")
    params = {
            'dev_pid': DEV_PID, # 语音类型 DEV_PID = 1737 表示英文，1537中文
             #"lm_id" : LM_ID,    #测试自训练平台开启此项
            'format': readfile[-3:], # 格式，支持pcm/wav/amr/m4a
            'rate': RATE, # 采样率
            'token': token, #  权限token
            'cuid': CUID, # 用户唯一标识
            'channel': 1,  # 声道
            'speech': speech, # 语音数据 b64解析
            'len': leng # 长度
    }
    post_data = json.dumps(params, sort_keys=False)
    return post_data

# 发送请求
def requ(post_data):
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        # print(f)
        result_str = f.read()
        # print ("Request time cost %f" % (timer() - begin))
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
    # print(result_str)
    result_str = str(result_str, 'utf-8')
    result = ast.literal_eval(result_str)
    # print(result)  # 转换为字典
    # print(result['result'])  # 文字部分
    return result['result'][0]

def sttquery(stt_task_list):
    print(stt_task_list)
    for task_id in stt_task_list:
        url = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/query'  # 查询音频任务转写结果请求地址
        body = {
            "task_ids": [task_id],
        }
        token = {"access_token": fetch_token()}
        headers = {'content-type': "application/json"}
        response = requests.post(url, params=token, data=json.dumps(body), headers=headers)
        print(json.dumps(response.json(), ensure_ascii=False))

def sttbody(audio):
    with open(audio, "rb") as speech_file:
        speech_data = speech_file.read()
    s = str(base64.b64encode(speech_data), "utf-8")
    body = {
        "speech_url": s,
        "format": audio[-3:],
        "pid":
1737, # 中文1537 英文1737
        "rate": 16000
    }
    token = {"access_token": fetch_token()}
    headers = {'content-type': "application/json"}
    respons = requests.post(STT_URL, params=token, data=json.dumps(body), headers=headers)
    results = ast.literal_eval(respons.text)
    print(results, results["task_id"])
    # stt_task_list.append(results["task_id"])
    # print(stt_task_list)

def grouptts(d):
    audios = os.listdir(d)
    res = open(d + "result.txt", "w", encoding="utf-8")
    for a in audios:
        if a[-3:] == 'txt' :
            continue
        patha = d + a
        post_req = tok(patha)
        text = requ(post_req)
        print(a, text)
        res.write(a + "\t" + text + "\n")
    res.close()

if __name__ == "__main__":
    token = fetch_token()
    dire = "./testAudio/"
    grouptts(dire)


