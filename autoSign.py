import requests
import sys
import json
from datetime import datetime, timedelta, timezone
import time
import glob
import os
import random
from urllib3 import encode_multipart_formdata


def getTimeStr():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


def log(content):
    print(getTimeStr() + ' ' + str(content))
    sys.stdout.flush()


urls = {
    'login': 'https://xcx.xybsyw.com/login/login!wx.action',
    'loadAccount': 'https://xcx.xybsyw.com/account/LoadAccountInfo.action',
    'ip': 'https://xcx.xybsyw.com/behavior/Duration!getIp.action',
    'trainId': 'https://xcx.xybsyw.com/student/clock/GetPlan!getDefault.action',
    # 'position':'https://xcx.xybsyw.com/student/clock/GetPlan!detail.action',
    'sign': 'https://app.xybsyw.com/behavior/Duration.action',
    'autoSign': 'https://xcx.xybsyw.com/student/clock/Post!autoClock.action',
    'newSign': 'https://xcx.xybsyw.com/student/clock/Post!updateClock.action',
    'status': 'https://xcx.xybsyw.com/student/clock/GetPlan!detail.action',
    'post': 'https://xcx.xybsyw.com/student/clock/Post.action',
    'epidemic': 'https://xcx.xybsyw.com/student/clock/saveEpidemicSituation.action',
    'policy': 'https://xcx.xybsyw.com/uploadfile/commonPostPolicy.action'
}

host1 = 'xcx.xybsyw.com'
host2 = 'app.xybsyw.com'


# 获取小程序用户唯一标识openId


def getOpenId(userInfo):
    data = {
        'openId': userInfo['token']['openId'],
        'unionId': userInfo['token']['unionId']
    }
    return data


# 获取Header
def getHeader(host):
    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat'
    contentType = 'application/x-www-form-urlencoded'
    headers = {
        'user-agent': userAgent,
        'content-type': contentType,
        'host': host,
        'Connection': 'keep-alive'
    }
    return headers


# 登录获取sessionId和loginerId
def login(userInfo):
    data = getOpenId(userInfo)
    headers = getHeader(host1)
    url = urls['login']
    resp = requests.post(url=url, headers=headers, data=data).json()
    if ('成功' in resp['msg']):
        ret = {
            'sessionId': resp['data']['sessionId'],
            'loginerId': resp['data']['loginerId']
        }
        log(f"sessionId:{resp['data']['sessionId']}获取成功")
        log(f"loginerId:{resp['data']['loginerId']}获取成功")
        return ret
    else:
        log('登录失败')
        exit(-1)


# 获取username
def getUsername(sessionId):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['loadAccount']
    resp = requests.post(url=url, headers=headers).json()
    if ('成功' in resp['msg']):
        ret = resp['data']['loginer']
        log(f"username:{ret}获取成功")
        return ret
    else:
        log('获取username失败')
        exit(-1)


# 获取ip
def getIP(sessionId):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['ip']
    resp = requests.post(url=url, headers=headers).json()
    if ('success' in resp['msg']):
        ret = resp['data']['ip']
        log(f'ip:{ret}获取成功')
        return ret
    else:
        log('ip获取失败')
        exit(-1)


# 获取trainID
def getTrainID(sessionId):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['trainId']
    resp = requests.post(url=url, headers=headers).json()
    if ('成功' in resp['msg']):
        ret = resp['data']['clockVo']['traineeId']
        log(f'traineeId:{ret}获取成功')
        return ret
    else:
        log('trainid获取失败')
        exit(-1)


# 获取经纬度\签到地址
def getPosition(sessionId, trainId):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['status']
    data = {
        'traineeId': trainId
    }
    resp = requests.post(url=url, headers=headers, data=data).json()
    if ('成功' in resp['msg']):
        address = resp['data']['postInfo']['address']
        lat = resp['data']['postInfo']['lat']
        lng = resp['data']['postInfo']['lng']
        ret = {
            'lat': lat,
            'lng': lng
        }
        log(f'经度:{lng}|纬度:{lat}')
        log(f'签到地址:{address}')
        return ret
    else:
        log('经纬度获取失败')
        exit(-1)


def getSignForm(data, user):
    timeStamp = int(time.time())
    form = {
        'login': '1',
        'appVersion': '1.7.18',
        'operatingSystemVersion': '10',
        'deviceModel': 'microsoft',
        'operatingSystem': 'android',
        'screenWidth': '415',
        'screenHeight': '692',
        'reportSrc': '2',
        'eventTime': timeStamp,
        'eventType': 'click',
        'eventName': 'clickSignEvent',
        'clientIP': data['ip'],
        'pageId': data['pageId'],  # 30
        'itemID': 'none',
        'itemType': '其他',
        'stayTime': 'none',
        'deviceToken': user['token']['openId'],
        'netType': 'WIFI',
        'app': 'wx_student',
        'preferName': '机会',
        'pageName': '成长-签到',
        'userName': data['userName'],
        'userId': data['loginerId'],
        'province': user['location']['province'],
        'country': user['location']['country'],
        'city': user['location']['city'],
        'pageUrl': 'growUp/pages/sign/sign/sign',
        'preferPageId': '1',
        'preferPageUrl': 'pages/find/index/index',
        'urlParamsStr': ''

    }
    return form


# 判断userinfo.json信息是否完整
def checkUserInfo():
    with open('user.json', 'r', encoding='utf8') as fp:
        user = json.load(fp)
        if not (user['location']['province'] == "XX省" and user['location']['city'] == "XX市" and user['location'][
            'adcode'] == "城市编码" and user['location']['address'] == "XX街道XX路XX号"):
            if not (user['token']['openId'] == "填写你的openId" and user['token']['unionId'] == "填写你的unionId"):
                return True
    fp.close()
    return False


# 签到请求
def signReq(sessionId, data):
    headers = getHeader(host2)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['sign']
    resp = requests.post(url=url, headers=headers, data=data).json()
    if ('success' in resp['msg']):
        log(f'已成功获取账号信息')
    else:
        log('账号信息获取失败')
        exit(-1)


# 执行签到
def autoSign(sessionId, data):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['autoSign']
    log("发起签到请求")
    requests.post(url=url, headers=headers, data=data)


# 重新签到
def newSign(sessionId, data):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['newSign']
    resp = requests.post(url=url, headers=headers, data=data).json()
    log(resp['msg'])
    return resp['msg']


# 获取直传规则
def getPolicy(sessionId):
    data = {
        'customerType': 'STUDENT',
        'uploadType': 'UPLOAD_EPIDEMIC_SITUATION_IMAGES',
        'publicRead': True
    }
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['policy']
    resp = requests.post(url=url, headers=headers, data=data).json()
    return resp


# 获取上传地址
def getOssUrl(sessionId):
    policy = getPolicy(sessionId)
    healthCodeImg = max(glob.glob('healthCodeImg/*'), key=os.path.getctime)  # 获取文件夹内最新的一张健康码截图
    healthCodeImgOssUrl = uploadImgToOss(policy, open(healthCodeImg, 'rb'))
    travelCodeImg = max(glob.glob('travelCodeImg/*'), key=os.path.getctime)  # 获取文件夹内最新的一张行程码截图
    travelCodeImgOssUrl = uploadImgToOss(policy, open(travelCodeImg, 'rb'))
    return [healthCodeImgOssUrl, travelCodeImgOssUrl]


# 保存健康信息
def saveEpidemicSituation(sessionId):
    ossUrl = getOssUrl(sessionId)
    info = getHealthInfo()
    data = {
        'healthCodeStatus': info['healthCodeStatus'],
        'locationRiskLevel': info['locationRiskLevel'],
        'healthCodeImg': ossUrl[0],
        'travelCodeImg': ossUrl[1]
    }
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['epidemic']
    requests.post(url=url, headers=headers, data=data)
    log("已上传健康信息")


# 将健康码、行程码图片上传至oss
def uploadImgToOss(policy, file):
    ossHost = policy['data']['host']
    (path, name) = os.path.split(file.name)
    timestr = str(round(time.time() * 1000))
    params = {
        'OSSAccessKeyId': policy['data']['accessid'],
        'callback': policy['data']['callback'],
        'key': policy['data']['dir'] + '/' + timestr + '.png',
        'policy': policy['data']['policy'],
        'signature': policy['data']['signature'],
        'success_action_status': policy['data']['success_action_status'],
        'file': (name, file.read(), 'image/png')
    }
    (body, header) = encode_multipart_formdata(params, boundary=timestr)  # 构建multipart请求体，以及指定boundary
    headers = getHeader(ossHost[8:])
    headers['content-type'] = header
    resp = requests.post(url=ossHost, data=body, headers=headers).json()
    log(resp['status'] + " OK :)" if resp['status'] == "200" else " Sad :(")
    return resp['vo']['customParams']['ossUrl']


# 获取签到状态
def getSignStatus(sessionId, trainId):
    headers = getHeader(host1)
    headers['cookie'] = f'JSESSIONID={sessionId}'
    url = urls['status']
    data = {
        'traineeId': trainId
    }
    resp = requests.post(url=url, headers=headers, data=data).json()
    # if(resp['data']['clockInfo']['status'] == 0):
    if len(resp['data']['clockInfo']['inTime']) > 0:
        return True
    else:
        return False


# 获取用户信息
def getUserInfo():
    with open('user.json', 'r', encoding='utf8') as fp:
        user = json.load(fp)
    fp.close()
    return user


# 获取健康申报信息
def getHealthInfo():
    with open('healthInfo.json', 'r', encoding='utf8') as fp:
        info = json.load(fp)
    fp.close()
    return info


def preCheck():
    healthCode = True
    travelCode = True
    healthInfo = True
    userInfo = checkUserInfo()
    if os.path.exists('healthCodeImg'):
        if len(os.listdir('healthCodeImg')) != 0:
            healthCode = False
    else:
        os.makedirs('healthCodeImg')

    if os.path.exists('travelCodeImg'):
        if len(os.listdir('travelCodeImg')) != 0:
            travelCode = False
    else:
        os.makedirs('travelCodeImg')

    info = getHealthInfo()
    if info['healthCodeStatus'] != '填写你的健康码状态' and info['locationRiskLevel'] != '填写你的所在地风险':
        healthInfo = False

    if healthCode or travelCode or healthInfo or not userInfo:
        log("请完成以下步骤后，再重新执行签到：")
        order = 1
        if healthCode:
            log(str(order) + ".请将 健康码 存储到 travelCodeImg/ 目录中")
            order = order + 1
        if travelCode:
            log(str(order) + ".请将 行程码 存储到 healthCodeImg/ 目录中")
            order = order + 1
        if healthInfo:
            log(str(order) + ".请将 healthInfo.json 中的内容填写完整")
            order = order + 1
        if not userInfo:
            log(str(order) + ".请将 user.json 中的内容填写完整")
        exit(-1)
    else:
        log("检查通过，开始进行签到")


def main(argv):
    preCheck()
    if len(argv) > 1:
        delay = random.randint(0, int(argv[1]))
        print("延迟" + str(delay) + "秒后，执行签到...")
        time.sleep(delay)
    else:
        log('立即执行签到...')
    log('开始获取账号信息')
    userInfo = getUserInfo()
    sessions = login(userInfo)
    sessionId = sessions['sessionId']
    loginerId = sessions['loginerId']
    trainId = getTrainID(sessionId)
    userName = getUsername(sessionId)
    ip = getIP(sessionId)
    position = getPosition(sessionId, trainId)
    lng = position['lng']
    lat = position['lat']
    data = {
        'pageId': '27',
        'userName': userName,
        'loginerId': loginerId,
        'ip': ip
    }
    formData = getSignForm(data, userInfo)
    signReq(sessionId, formData)

    signFormData = {
        'model': 'microsoft',
        'brand': 'microsoft',
        'platform': 'windows',
        'system': 'Windows 11 x64',
        'openId': userInfo['token']['openId'],
        'unionId': userInfo['token']['unionId'],
        'traineeId': trainId,
        'adcode': userInfo['location']['adcode'],
        'lat': lat,
        'lng': lng,
        'address': userInfo['location']['address'],
        'deviceName': 'microsoft',
        'punchInStatus': '0',
        'clockStatus': '2'
    }
    if getSignStatus(sessionId, trainId):
        log('今天已经已签到啦,无需再次签到 :)')
        # newSign(sessionId, signFormData)（不可用，会提示 “状态异常，请联系客服...”）
    else:
        saveEpidemicSituation(sessionId)
        autoSign(sessionId, signFormData)
        if getSignStatus(sessionId, trainId):
            log('校友邦实习任务签到成功')
        else:
            log('校友邦实习任务签到失败!')


# 腾讯云函数使用
def main_handler(event, context):
    main(sys.argv)


if __name__ == '__main__':
    main(sys.argv)
