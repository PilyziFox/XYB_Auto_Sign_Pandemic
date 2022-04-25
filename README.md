## 校友邦实习自动签到-疫情健康申报功能

前人栽树，后人乘凉，现在算是做了一点微小的贡献吧 😋。

> **更新日志：**
> 
> 【2022/04/25】添加了疫情信息申报接口（按需填写健康信息后使用），更新了签到Api ，延迟签到功能
> 
> 【2021/03/07】完善文档说明，~~更换通知方式为更稳定的钉钉机器人~~（被我删掉了，因为不我会用，还把我整蒙了！`有需要使用的自己加上原来方法和导一下包就好`）

### ⛏️运行环境

Python3以及相应的库

### ⛏️运行方式

1. 配置`user.json`信息
2. 填写`healthInfo.json`信息
3. 按首次运行时的提示放入对应的健康码和行程码.
4. 运行`autoSign.py`测试是否可以正常执行
5. 设定定时任务

### ⛏️相关说明

#### ⏲️延迟功能

> 运行程序时可以加入`int`参数，延迟程序签到时间，如`autoSign.py 1800`将在0-1800（秒）内随机延迟一段时间进行签到，避免过于准时

#### 健康申报功能

> 在首次运行后会生成healthCodeImg和travelCodeImg目录，之后每次签到前，会读取最后存放至目录的图片，作为健康码上传申报。因此按要求把健康码放到对应文件夹就可以了。

> 至于怎么全自动化（获取每日最新的健康码） 目前想到的只有几个思路 1.Android 上使用 Tasker 之类软件完成的当日截图工作。 2.研究健康码小程序去？ 3.***就嗯用..卧槽，我不好说***

#### 💉`healthInfo.json`配置
```json
{
  "healthCodeStatus":"填写健康码状态，用0-2表示",
  "locationRiskLevel":"填写所在地风险，用0-2表示",
  "__comment__": "healthCodeStatus 为健康码状态，locationRiskLevel为所在地风险。0 代表`低风险`及`绿码` 1 代表`中风险`及`黄码` 2 代表`红...`"
}
```

#### 📃`user.json`配置

```json
{
  "token":{
    "openId":"填写你的openId",
    "unionId":"填写你的unionId"
  },
  "location":{
    "country":"中国",
    "province":"XX省",
    "city":"XX市",
    "adcode":"城市编码",
    "address":"XX街道XX路XX号"
  },
  "reason": "",
  "DingDingtoken":"钉钉机器人token",
  "DingDingsecret":"钉钉机器人secret"
}
```

##### ✔️获取`openId`和`unionId`的方法

> 签到默认提交的地址是在申请实习时的地址，如果需要修改请自行修改`getPosition()`中的`lat`、`lng`参数（即修改经纬度）

**工具：**`Fiddler`等抓包工具、`PC端wx`

**前提：**`校友邦`微信小程序已绑定校友邦账号

**抓包：**

1. 登录PC端wx
2. 开启`Fiddler`抓包（`Fiddler`安装方法请自行百度）
3. 打开`校友邦`微信小程序，登录（**使用微信快捷登录**）

<img src="https://img.xiehestudio.com/pic_go/20210307123713.png" style="zoom: 50%;" />

4. 这时就能看到`Fiddler`抓包结果，如下图

![](https://img.xiehestudio.com/pic_go/20210307124015.png)

##### ✔️关于`adcode`

> 查询地址：http://pxcity.net/sfz/zhejiang/  
>
> 以浙江省宁波市为例

<img src="https://img.xiehestudio.com/pic_go/20210307125001.png" style="zoom: 67%;" />

<img src="https://img.xiehestudio.com/pic_go/20210307125053.png" style="zoom:67%;" />

**实习地址**对应的县区级代码即为`adcode`


### ⏰定时任务

> 设置定时任务后就可以实现每天定时执行前到啦~
>
> 设置定时任务前请在相应的定时任务环境中手动执行一遍，检查参数是否填写正确。

1. 腾讯云函数：[文档](https://cloud.tencent.com/document/product/583/9210)
2. VPS部署：[文档](https://pwner.cn/posts/12d18c2f.html)


### 鸣谢

- [BytePrince/XYB_Auto_Sign](https://github.com/CncCbz/xybSign)
- [CncCbz/xybSign](https://github.com/CncCbz/xybSign)
- [xiaomingxingwu/xyb-sign](https://github.com/xiaomingxingwu/xyb-sign)

