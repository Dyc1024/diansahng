# 绕过验证码无限次获取上学吧题目答案
# 上学吧网址：https://www.shangxueba.com/ask
# by Tsing 2019.04.02

import random
import requests
import urllib3

urllib3.disable_warnings()  # 这句和上面一句是为了忽略 https 安全验证警告，参考：https://www.cnblogs.com/ljfight/p/9577783.html
from bs4 import BeautifulSoup
import webbrowser


def get_question(session, dataid):
    link = "https://m.shangxueba.com/ask/" + dataid + ".html"
    r = session.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        description = soup.find(attrs={"name": "description"})['content']  # 抓取题干内容
        if (description and description[
                            0:5] != '上学吧提供'):  # 页面错误的话，显示的内容是：上学吧提供考研、公务员、司法、会计、金融等各种资格考试认证学习资料,视频课程,真题,模拟试题分享下载服务和培训服务
            return description
        else:
            return "无法获取题目内容！"
    except:  # 有的时候网址出错会弹JavaScript弹框：该问题不存在或未审核
        return "该问题不存在或未审核！"


def get_answer(session, dataid):
    data = {
        "id": dataid,
        "action": "showZuiJia"
    }
    r = session.post("https://m.shangxueba.com/ask/ask_getzuijia.aspx", data=data)  # 核查验证码正确性
    soup = BeautifulSoup(r.content, "html.parser")
    ans = soup.select('.replyCon')
    if (ans):
        images = ans[0].select('img')  # 有的题目答案中有图片，例如：https://www.shangxueba.com/ask/9710781.html
        if (images):  # 有的答案中图片出错，链接为：[img]http://www.shangxueba.com/exam/images/onErrorImg.jpg[/img]
            with open('shangxueba_answer.html', 'w') as f:
                f.write(str(ans[0]))
                f.close()
                webbrowser.open('shangxueba_answer.html')
                return "答案中有图片，已自动打开答案网页文件。如没有自动打开网页，可以手动打开 shangxueba_answer.html"
        return ans[0].text.strip()
    else:
        return "答案获取失败！请检查链接是否正确。"


if __name__ == '__main__':
    s = requests.session()
    print("*" * 45 + "\n上学吧答案神器（绕过验证码 + 破解IP限制）\nby Tsing @Zhihu 2019.04.02\n" + "*" * 45)
    while True:
        s.headers.update({"X-Forwarded-For": "%d.%d.%d.%d" % (
        random.randint(120, 125), random.randint(1, 200), random.randint(1, 200),
        random.randint(1, 200))})  # 这一句是整个程序的关键，通过修改 X-Forwarded-For 信息来欺骗 ASP 站点对于 IP 的验证。
        link = input("\n请输入上学吧网站上某道题目的网址，例如：https://www.shangxueba.com/ask/8952241.html\n\n请输入：").strip()  # 过滤首尾的空格
        if (link[0:31] != "https://www.shangxueba.com/ask/" or link[-4:] != "html"):
            print("\n网址输入有误！请重新输入！\n")
            continue
        dataid = link.split("/")[-1].replace(r".html", "")  # 提取网址最后的数字部分
        if (dataid.isdigit()):  # 根据格式，dataid 应该全部为数字，判断字符串是否全部为数字，返回 True 或者 False
            print('\n' + '-' * 45 + '\n题目：' + get_question(s, dataid) + '\n\n' + get_answer(s,
                                                                                            dataid) + '\n' + '-' * 45 + '\n\n\n')
        else:
            print("\n网址输入有误！请重新输入！\n")
            continue