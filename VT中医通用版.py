import os
import sys
import json
import re
import math
import time
import random
import requests
import datetime
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
JKHOST = 'http://43.128.225.218:9716/'
argv_list = sys.argv
if len(argv_list) == 1:
    ANAME = 'zy_VT'
    PNAME = 'VT通用版'
elif len(argv_list) == 2:
    ANAME = argv_list[1]
    PNAME = f'{ANAME}通用版'
else:
    print('参数不对，不执行×')
    exit()

def shuoming():
    print(f'【{PNAME}】当前版本V1.0')
    print('q群：114798500；投稿可联系群主群管理。')
    print('脚本需授权码才能运行，如需购买联系群主（10r/2000次）')
    print('=====================================')
    print('''通用配置
    ★★★授权码变量名★★★：MM_sqm
    如要推送 需配置wxpusher UID，不配置默认不推送(注：推送消息消耗0.1次卡密)
        微信关注应用: https://wxpusher.zjiecode.com/wxuser/?type=1&id=94949#/follow，然后点击「我的」-「我的UID」查询到UID
        ★★★UID变量名★★★：MM_wpUID
    分隔符自定义（不配置默认换行隔开）：★★★变量名★★★：MM_fenge
    并发数自定义（不配置默认5个并发）：★★★变量名★★★：MM_bingfa
''')

log_msg = []
def print_log(msg):
    print(msg)
    log_msg.append(str(msg))
shuoming()
appId = ''
account_all = ''
lianjie = ''
sqm = ''
wp_uid = ''
if not account_all:
    account_all = os.getenv(f'MM_{ANAME.lower()}')
if not lianjie:
    lianjie = os.getenv(f'MM_{ANAME.lower()}_lianjie')
if not sqm:
    sqm = os.getenv('MM_sqm')
if not account_all or not sqm or not lianjie:
    print('没有配置变量不执行×')
    exit()
fgf = os.getenv('MM_fenge')
if not fgf:
    fgf = '\n'
bingfa = os.getenv('MM_bingfa')
if not bingfa:
    bingfa = 5
wp_uid = os.getenv('MM_wpUID')
if wp_uid:
    try:
        resp = requests.post(JKHOST+'wxpusher_token', json={'sqm': sqm, 'a_name': 'WPTOKEN'}).json()
        if resp['code'] == 200:
            log_cf = resp['data']
        else:
            log_cf = ''
    except:
        print('请求通知服务器超时，不发送通知')
        log_cf = ''
else:
    log_cf = ''


def send_wxpusher(log_cf, wp_uid):
    data = {
        "appToken": log_cf,
        "content": '\n'.join(log_msg),
        "summary": f"{PNAME} 日志信息",

        "contentType": 1,
        "uids": [
            wp_uid,
        ],
        "verifyPay": False
    }

    resp = requests.post('https://wxpusher.zjiecode.com/api/send/message', json=data).json()
    if resp['success']:
        print('日志发送成功')


campPeriodId = ''
company_id = ''
campId = ''
origin = ''
host = 'cgateway.bjmantis.net.cn'
def get_csign(param_list):
    try:
        resp = requests.post(JKHOST + 'zy_bbkj_getcsign', json={'sqm': sqm, 'a_name': ANAME, 'data': {'param': param_list, 'type': 'csign'}}).json()
        if resp['code'] == 200:
            print_log(str(resp['msg']))
            return resp['data']
        else:
            print_log(f'请求异常：{resp}')
            return ''
    except:
        print('服务器异常，联系管理员')
        return ''


def get_sign(course_id, campPeriodId, d_id, appId, now):
    for i in range(3):
        try:
            resp = requests.post(JKHOST + 'zy_bbkj_getcsign', json={'sqm': sqm, 'a_name': ANAME, 'data': {'param': [course_id, campPeriodId, d_id, appId, now], 'type': 'sign'}}).json()
            if resp['code'] == 200:
                print_log(str(resp['msg']))
                return resp['data']
            else:
                time.sleep(2)
                print_log(f'请求异常：{resp}')
        except:
            time.sleep(2)
            print('服务器异常，联系管理员')

def get_union_id(headers):
    for i in range(3):
        try:
            resp = requests.post(JKHOST + 'zy_bbkj_unionid', json={'sqm': sqm, 'a_name': ANAME, 'data': {'headers': headers}}).json()
            if resp['code'] == 200:
                print_log(str(resp['msg']))
                return resp['data']
            else:
                time.sleep(2)
                print_log(f'请求异常：{resp}')
        except:
            time.sleep(2)
            print('服务器异常，联系管理员')


def course_detail(headers, d_id, course_id):
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    t = str(int(time.time() * 1000))
    headers['timestamp'] = t
    param_list = ['/scrm-course-api/pass/campPeriodCourse/queryCampPeriodCourseInfoPageList', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(600, 1000))
    params = {
        'id': course_id,
        'campPeriodCourseId': d_id,
        'campPeriodId': campPeriodId,
    }
    response = requests.post(
        f'https://{host}/scrm-course-api/pass/courseCenterApi/selectCourseDetailById',
        params=params,
        headers=headers,
    ).json()
    if response['code'] == 200 and not response['data']['watchExpiredFlag']:
        return response['data']['questionPaperId'], response['data']['duration']
    else:
        print('获取课程失败')


def query_appid(headers, corpId):
    headers['Content-Type'] = 'application/json'
    t = str(int(time.time() * 1000))
    headers['timestamp'] = t
    param_list = ['/scrm-course-api/pass/questionApi/initQuestionPaper', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(600, 1000))
    json_data = {
        'companyId': company_id,
        'scene': 'SHARE',
        'businessId': corpId,
    }

    response = requests.post('https://cgateway.bjmantis.net.cn/scrm-course-api/pass/queryAppInfo', headers=headers, json=json_data).json()
    return response['data']['appId']


def init_question(headers, question_id, course_id):
    headers['Content-Type'] = 'application/json'
    t = str(int(time.time() * 1000))
    headers['timestamp'] = t
    param_list = ['/scrm-course-api/pass/questionApi/initQuestionPaper', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(600, 1000))
    json_data = {
        'id': question_id,
        'courseId': course_id,
        'filterQuestionType': 'SUBJECTIVITY_QUESTION',
    }

    response = requests.post(
        f'https://{host}/scrm-course-api/pass/questionApi/initQuestionPaper',
        headers=headers,
        json=json_data,
    ).json()
    print(f'答案：{response}')
    if response['code'] == 200:
        return response['data']
    else:
        print_log('获取题目答案出错')


def update_course(headers, course_id, d_id):
    url = f'https://{host}/scrm-c-customer/pass/courseCenterApi/updateUserCourseRef'
    t = str(int(time.time()*1000))
    headers['Content-Type'] = 'application/json'
    headers['timestamp'] = t
    param_list = ['/scrm-c-customer/pass/courseCenterApi/updateUserCourseRef', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(800, 1000))

    json_data = {
        'courseId': str(course_id),
        'completeFlag': 'Y',
        'campPeriodCourseId': str(d_id),
        'campPeriodId': campPeriodId,
        "jsCompleteFlag": 'TRUE'
    }
    response = requests.post(url, headers=headers, json=json_data).text
    response = json.loads(response)
    print_log(f'完播：{response}')
    time.sleep(random.randint(1, 3))


def submit_question(headers, question_dict, course_id, question_id, start_time):
    questionDetail = question_dict['questionDetailVOList']
    questionDetailVOList = []
    for index, detail in enumerate(questionDetail):
        q_id, content, result_select = detail['id'], detail['content'], detail['resultSelect']
        detail['sort'] = index
        detail['singleScore'] = 0
        detail['answerSelect'] = result_select
        detail['resultCode'] = 'Y'
        detail['statusCode'] = 'Y'
        detail['answerScore'] = 0
        detail['questionDetailId'] = q_id
        questionDetailVOList.append(detail)
    total_count = question_dict['totalQuestion']
    now = int(time.time() * 1000)
    json_data = {
        "courseId": str(course_id),
        "questionPaperId": question_id,
        "totalCount": total_count,
        "startTime": str(start_time),
        "endTime": str(now),
        "correctCount": total_count,
        "errorCount": 0,
        "unansweredCount": 0,
        "answeredCount": total_count,
        "subjectiveCount": 0,
        "examScore": 0,
        "totalScore": question_dict['totalScore'],
        "paperName": question_dict['name'],
        "questionDetailVOList": questionDetailVOList,
        "videoLiveRedFlag": "Y",
        "courseType": "",
        "visitUrl": quote(lianjie).replace('/', '%2F')
    }
    resp = requests.post(f'https://{host}/scrm-course-api/pass/questionApi/submitQuestionPaper', headers=headers, json=json_data).json()
    print_log(f'答题结果：{resp}')
    time.sleep(random.randint(1, 3))

def cash_out(headers, course_id, d_id, bz):
    now = str(int(time.time()*1000))
    headers['Content-Type'] = 'application/json'
    headers['timestamp'] = now
    param_list = ['/scrm-c-customer/pass/courseCenterApi/videoLiveRedCashOut', headers['uuid'], now]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(800, 1000))

    sign = get_sign(course_id, campPeriodId, d_id, appId, now)
    if sign:
        json_data = {
            'courseId': str(course_id),
            'campPeriodId': campPeriodId,
            'campPeriodCourseId': str(d_id),
            'appId': appId,
            'miniAppId': '',
            'visitUrl': quote(lianjie).replace('/', '%2F'),
            'verifyCode': '',
            'phone': '',
            'sign': sign,
            'time': now,
        }
        response = requests.post(
            f'https://{host}/scrm-c-customer/pass/courseCenterApi/videoLiveRedCashOut',
            headers=headers,
            json=json_data
        ).json()
        print(f'【{bz}】提现结果：{response}')
        if response['code'] == 200:
            data = response['data']
            if data:
                print_log(f'【{bz}】提现成功，获得 {data["amount"]} 红包')
            return True
        else:
            print_log(f'【{bz}】提现失败，大概率是被拉黑了')
        time.sleep(random.randint(2, 5))
    else:
        print_log(f'【{bz}】提现失败，手动试试')


def main_flow(union_id, duration, d_id, campId):
    headers_do = {
        'Host': 'track.bjmantis.net.cn',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9079 Flue',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9',
    }

    def create_guid():
        pattern = "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx"
        return re.sub('[xy]', lambda c: format(random.randint(0, 15) if c.group() == 'x' else (random.randint(0, 3) | 8), 'x'), pattern)

    def ve():
        data = '{"type":"VE","union_id":"'+union_id+'","source":"camp_video_red","source_id":'+str(d_id)+',"uid":"'+vod_uid+'@'+company_id+'","company_id":"'+company_id+'","url":"'+quote(lianjie).replace('/', '%2F')+'","browser":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9079 Flue","companyId":"'+company_id+'","ext":{"campId":"'+campId+'","campPeriodId":"'+campPeriodId+'"},"page_title":""}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data).json()
        return response['track_id']

    def vod_action():
        data = '{"type":"VOD_ACTION","trackId":"'+track_id+'","union_id":"'+union_id+'","source":"camp_video_red","source_id":'+str(d_id)+',"uid":"'+vod_uid+'@'+company_id+'","company_id":"'+company_id+'","companyId":"'+company_id+'","ext":{"campId":"'+campId+'","campPeriodId":"'+campPeriodId+'"},"action":"PLAY"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data).json()

    def vod_ttl(nn="90"):
        data = '{"type":"VOD_TTL","trackId":"'+track_id+'","uid":"'+vod_uid+'@'+company_id+'","ttl":'+random.choice([nn])+',"union_id":"'+union_id+'","source":"camp_video_red","source_id":'+str(d_id)+',"company_id":"'+company_id+'","companyId":"'+company_id+'","ext":{"campId":"'+campId+'","campPeriodId":"'+campPeriodId+'"}}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data).json()

    def vod_end():
        data = '{"type":"VOD_ACTION","trackId":"'+track_id+'","union_id":"'+union_id+'","source":"camp_video_red","source_id":'+str(d_id)+',"uid":"'+vod_uid+'@'+company_id+'","company_id":"'+company_id+'","companyId":"'+company_id+'","ext":{"campId":"'+campId+'","campPeriodId":"'+campPeriodId+'"},"action":"PAUSE"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data).json()

    def log_didMount():
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"tcPlayer-huawei-preCacheTime-didMount","message":"0-WX_MINI_ENV=false-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data).json()

    def log_durationchange():
        duration_random = duration + round(random.random(), 2)
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"tcPlayer-huawei-durationchange","message":"获取视频时长回调：undefined-undefined-'+str(duration_random)+'-undefined-0-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data.encode()).json()

    def log_end():
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"tcPlayer-huawei-end","message":"腾讯播放器完播回调-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data.encode()).json()

    def log_play(now_duration):
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"tcPlayer-huawei-play","message":"历史播放时长：'+str(now_duration)+'，当前播放时长：'+str(now_duration+round(random.random(), 6))+'-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data.encode()).json()

    vod_uid = create_guid()
    track_id = ve()
    print(track_id)
    log_didMount()
    log_durationchange()
    log_play(0)
    vod_action()
    num = math.floor(duration/90)
    for i in range(num):
        vod_ttl()
        print(datetime.datetime.now().strftime('%H:%M:%S'), f'上报时间：{i*90}')
        time.sleep(random.randint(88, 93))
    last_t = int(duration) - num * 90
    time.sleep(last_t+random.randint(15, 20))
    vod_ttl(str(last_t))
    log_play(duration)
    vod_end()
    log_end()


def get_campId(headers):
    url = f'https://{host}/scrm-c-customer/pass/campPeriodCourse/initUserCampInfo'
    t = str(int(time.time()*1000))
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['timestamp'] = t
    param_list = ['/scrm-c-customer/pass/campPeriodCourse/initUserCampInfo', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(800, 4000))
    params = {
        'campPeriodId': campPeriodId,
    }
    response = requests.post(url, params=params, headers=headers).json()
    for data in response['data']:
        if str(data['campPeriodId']) == campPeriodId:
            return data['campId']


def get_info(url):
    for i in range(3):
        try:
            resp = requests.post(JKHOST+'zy_bbkj_getinfo', json={'sqm': sqm, 'a_name': ANAME, 'data': {'url': url}}).json()
            if resp['code'] == 200:
                print_log(str(resp['msg']))
                return resp['data']
            else:
                time.sleep(2)
                print_log(f'请求异常：{resp}')
        except Exception as e:
            time.sleep(2)
            print(e)


def log_wanbo(union_id, log_t=1):
    headers_do = {
        'Host': 'track.bjmantis.net.cn',
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9079 Flue',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    if log_t == 1:
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"updateUserCourseRef-request","message":"完播接口请求开始-'+appId+'-'+appId+'-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data.encode()).json()
    else:
        data = '{"type":"LOG","uid":"'+union_id+'","messageType":"updateUserCourseRef-request","message":"完播接口详情=200-msg=ok}-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers_do, data=data.encode())


def log_answer(unino_id, log_t=1):
    headers = {
        'Host': 'track.bjmantis.net.cn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c33) XWEB/8447 Flue',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    if log_t == 1:
        data = '{"type":"LOG","uid":"'+unino_id+'","messageType":"RedEnvelopeQuestion-select-click","message":"答题选项点击=Y-N-false-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers, data=data.encode())
        time.sleep(1)
        data = '{"type":"LOG","uid":"'+unino_id+'","messageType":"RedEnvelopeQuestion-submit","message":"提交答案点击-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers, data=data.encode())
    else:
        data = '{"type":"LOG","uid":"'+unino_id+'","messageType":"RedEnvelopeQuestion-submit","message":"提交答案点击-成功提交code=200msg=ok-companyId='+company_id+'"}'
        response = requests.post('https://track.bjmantis.net.cn/t_scrm/p.do', headers=headers, data=data.encode())


def query_cash_status(headers, course_id, d_id, bz):
    time.sleep(random.randint(60, 80))
    t = str(int(time.time() * 1000))
    headers['Content-Type'] = 'application/json'
    headers['timestamp'] = t
    param_list = ['/scrm-c-customer/pass/courseCenterApi/queryCashStatus', headers['uuid'], t]
    csign = get_csign(param_list)
    headers['csign'] = csign
    headers['rectifytime'] = str(random.randint(800, 4000))
    sign = get_sign(course_id, campPeriodId, d_id, appId, t)
    if sign:
        json_data = {
            'courseId': str(course_id),
            'campPeriodId': campPeriodId,
            'campPeriodCourseId': str(d_id),
            'appId': appId,
            'miniAppId': '',
            'visitUrl': quote(lianjie).replace('/', '%2F'),
            'sign': sign,
            'time': t,
        }

        response = requests.post(
            f'https://{host}/scrm-c-customer/pass/courseCenterApi/queryCashStatus',
            headers=headers,
            json=json_data,
        ).json()
        print(f'【{bz}】提现状态返回：', response)
        status = response['data']['status']
        if status == 'WAIT_USER_CONFIRM' or status == 'FAILED':
            print_log(f'【{bz}】提现待确认，手动提现：{lianjie}')
        else:
            print_log(f'【{bz}】提现状态：{status}')

def main(account):
    global company_id
    global campPeriodId
    global campId
    global appId
    authorization, x_authorizationaccess, uuid, bz = account.split('#')
    print_log(f'开始执行：【{bz}】')
    headers = {
        'Host': host,
        'x-authorizationaccess': x_authorizationaccess,
        'authorization': f'Bearer {authorization.replace("Bearer ", "")}',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090c2d) XWEB/13487 Flue',
        'accept': 'application/json, text/plain, */*',
        'x-company-gray': company_id,
        'uuid': uuid,
        'rectifytime': '3841',
        'cid': company_id,
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
    }
    print_log(f'【{bz}】获取基本信息')
    course_dict = get_info(lianjie)
    if course_dict:
        print_log(f'【{bz}】获取unionid')
        union_id = get_union_id(headers)
        if union_id:
            start_now = int(time.time() * 1000)
            company_id, campPeriodId, campId, course_id, d_id, corpId = str(course_dict['companyId']), str(course_dict['campPeriodId']), str(course_dict['campId']), str(course_dict['course_id']), str(course_dict['d_id']), str(course_dict['corpId'])
            appId = query_appid(headers, corpId)
            print(appId)
            print_log(f'【{bz}】获取课程信息')
            question_id, duration = course_detail(headers, d_id, course_id)
            print(datetime.datetime.now().strftime('%H:%M:%S'), duration)
            print_log(f'【{bz}】观看视频中')
            main_flow(union_id, duration, d_id, campId)
            log_wanbo(union_id)
            update_course(headers, course_id, d_id)
            log_wanbo(union_id, 2)
            if question_id:
                question_dict = init_question(headers, question_id, course_id)
                log_answer(union_id)
                submit_question(headers, question_dict, course_id, question_id, start_now)
                log_answer(union_id, 2)
                time.sleep(random.randint(1, 2))
                if cash_out(headers, course_id, d_id, bz):
                    query_cash_status(headers, course_id, d_id, bz)
            else:
                print_log('该视频没有答题')
        else:
            print_log(f'【{bz}】获取unionid出错')
    else:
        print_log(f'【{bz}】链接解析出错')


account_list = account_all.split(fgf)
print(f'共找到{len(account_list)}个账号')

with ThreadPoolExecutor(max_workers=int(bingfa)) as executor:
    answer_list = list(executor.map(main, account_list))

if log_cf and wp_uid:
    send_wxpusher(log_cf, wp_uid)
