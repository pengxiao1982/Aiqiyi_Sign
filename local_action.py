'''
@FILE    :   action.py
@DSEC    :   爱奇艺会员打卡
@AUTHOR  :   ioutime
@DATE    :   2021/07/11  00:56:17
@VERSION :   1.1
'''
import requests
import argparse
import execjs
import re
from http import cookiejar

cookie = '''QC005=59fe2c1c2af0b2d6e5ed5e85733c08f7; QC008=1632499845.1632499845.1632499845.1; __uuid=e9a36a95-a844-00b1-1f4f-d81f7509250b; QC173=0; QC006=50tavpb569wimuaspc62ydpb; QP0030=1; nu=0; QC007=DIRECT; QC010=206296855; QC180=true; P00004=.1633072680.2c7426b250; P00001=6aF4MkJkrTxspG4tJxFlYeUQIuUbasU0102OpiXLrwoZF18bCEZD8jjem35loMcTR01bb; P00003=2003169118; P00010=2003169118; P01010=1633104000; P00007=6aF4MkJkrTxspG4tJxFlYeUQIuUbasU0102OpiXLrwoZF18bCEZD8jjem35loMcTR01bb; P00PRU=2003169118; QC160=%7B%22type%22%3A3%7D; QYABEX={"mergedAbtest":"1707_B,1550_B","PCW-Home-List":{"value":"1","abtest":"1707_B"},"pcw_home_hover":{"value":"1","abtest":"1550_B"}}; QC170=0; QC179=%7B%22vipTypes%22%3A%22%22%2C%22userIcon%22%3A%22%2F%2Fimg7.iqiyipic.com%2Fpassport%2F20170317%2F98%2Fc5%2Fpassport_2003169118_148973701691386_130_130.jpg%22%2C%22iconPendant%22%3A%22%22%2C%22uid%22%3A2003169118%7D; QC175=%7B%22upd%22%3Atrue%2C%22ct%22%3A1633072724809%7D; __dfp=a07223b4d769364dc6901d44d099ec4cf03c36fca81d89168a806c50514cda6644@1634357441538@1633061442538; P00002=%7B%22uid%22%3A2003169118%2C%22pru%22%3A2003169118%2C%22user_name%22%3A%22157****8812%22%2C%22nickname%22%3A%222003169118%22%2C%22pnickname%22%3A%222003169118%22%2C%22type%22%3A4%2C%22email%22%3A%22%22%7D; QC163=1; QP0013=0'''

# 创建一个session,作用会自动保存cookie
Session = requests.session()

#推送信息
def push_info(infos,msg):
    token = infos["token"]
    if not token:
        return
    else: 
        try:
            url = "http://www.pushplus.plus/send?token="+token+"&title=爱奇艺打卡&content="+msg+"&template=html"
            requests.get(url=url)
        except Exception as e:
            print('推送失败')
            print(e)
#参数
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", dest="token", help="p58979041e46449b4b74c7d4b4878a109")
    args = parser.parse_args()

    return {
        "token" : args.token,
    }

#sign
def member_sign(cookies_dict):
    P00001 = cookies_dict.get('P00001')
    if P00001 == None:
        msg = "输入的cookie有问题(P00001)，请重新获取"
        return msg   
    login = Session.get('https://static.iqiyi.com/js/qiyiV2/20201023105821/common/common.js').text
    regex1=re.compile("platform:\"(.*?)\"")
    platform=regex1.findall(login)
    if len(platform) == 0:
        msg = "出错了，无法获取platform"
        return msg
    url='https://tc.vip.iqiyi.com/taskCenter/task/userSign?P00001='+P00001+'&platform='+platform[0] + '&lang=zh_CN&app_lm=cn&deviceID=pcw-pc&version=v2'
    try:
        sign=Session.get(url)
        strr = sign.json()
        try:
            sign_msg = strr.get('msg')
        except:
            msg = "未签"
        str2 = strr.get('data')
        continueSignDaysSum = str2.get('continueSignDaysSum')
        rewardDay = 7 if continueSignDaysSum%28<=7 else (14 if continueSignDaysSum%28<=14 else 28)
        rouund_day = 28 if continueSignDaysSum%28 == 0 else continueSignDaysSum%28
        growth = str2.get('acquireGiftList')[0]
        msg = f"{sign_msg}\n{growth}\n连续签到：{continueSignDaysSum}天\n签到周期：{rouund_day}天/{rewardDay}天\n"
    except Exception as e:
        print(e)
        msg = "出错了,未签到成功,可能是程序问题,也可能你不是爱奇艺会员"
    return msg

#获取用户信息
def get_info(cookies_dict):
    P00001 = cookies_dict.get('P00001')
    if P00001 == None:
        msg = "输入的cookie有问题(P00001)，请重新获取"
        print(msg)
        return msg 
    url = 'http://serv.vip.iqiyi.com/vipgrowth/query.action'
    params = {
        "P00001": P00001,
        }
    res = Session.get(url, params=params)
    if res.json()["code"] == "A00000":
        try:
            res_data = res.json()["data"]
            #VIP等级
            level = res_data["level"]
            #升级需要成长值
            distance = res_data["distance"]
            #VIP到期时间
            deadline = res_data["deadline"]
            msg = f"VIP等级：{level}\n升级需成长值：{distance}\nVIP到期时间:{deadline}"
        except:
            msg = "获取个人具体信息失败"
    else:
        msg = "获取个人信息失败"
    return msg

#转换获取的COOKIE
def transform(infos):
    try:
        cookies = cookie.replace(' ','')
        dct = {}
        lst = cookies.split(';')
        for i in lst:
            name = i.split('=')[0]
            value = i.split('=')[1]
            dct[name] = value
    except:
        msg0 = "输入的cookie不正确，请重新获取"
        print(msg0)
        push_info(infos,msg0)
        return
    #判断是否有要的值
    P00001 = dct.get('P00001')
    if P00001 == None:
        msg0 = "输入的cookie有问题(P00001)，请重新获取"
        print(msg0)
        push_info(infos,msg0)
        return
    #签到
    msg0  = member_sign(dct)
    #获取用户信息
    # msg1 = get_info(dct)
    # #输出信息
    # msg = msg0 + msg1
    print(msg0)
    #推送消息
    push_info(infos,msg0)
    return

#主函数
def main(infos):
    '''
    爱奇艺会员打卡,本地代码执行
    '''
    transform(infos)

if __name__=="__main__":
    main(get_args())

