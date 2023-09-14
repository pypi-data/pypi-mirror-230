# -*- coding: utf-8 -*-
# @Time : 2023/6/30
# @Author : chengwenping2
# @File : mail.py
"""
文件说明：使用smtplib接口发送邮件
"""

import traceback
from pig_frame import log
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


mail_host = "smtp.feishu.cn"  # 设置邮箱服务器
mail_pass = "UmaUOXgvvFLk7XLm"  # 这里就是邮箱的口令，也就是授权码，不是密码。

def sent_mail(sender, sender_alias, to, cc, subject, body, att):
    receivers = ",".join(to) + ",".join(cc)

    msg = MIMEMultipart("mixd")
    msg["Subject"] = subject
    msg["From"] = sender_alias
    msg["To"] = receivers

    alternative = MIMEMultipart('alternative')
    texthtml = MIMEText(body, _subtype='html', _charset='UTF-8')
    alternative.attach(texthtml)
    msg.attach(alternative)

    for i in att:
        HTMLpart = MIMEText(open(att[i],'rb').read(), 'html', 'UTF-8')
        HTMLpart['Content-Type'] = 'application/octet-stream'
        HTMLpart.add_header('Content-Disposition', 'attachment', filename=i+".html")
        msg.attach(HTMLpart)

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(sender, mail_pass)
        smtpObj.sendmail(sender_alias, receivers.split(","), msg.as_string())
        smtpObj.quit()
        log.info(f"发送成功:{subject}")
        return True
    except smtplib.SMTPException as e:
        log.error(f"邮件发送失败{e}  \n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    sent_mail("chengwenping2@newhope.cn", "chengwenping2", ["chengwenping2@newhope.cn","18108278175@163.com"], [], "自动化巡检报告",
              "just a test",{"test1":r"D:\autotest\smartpig_api\test_report\01-测试物料\APP端登录并获取cookie值.html",
                             "test2":r"D:\autotest\smartpig_api\test_report\慧养猪功能巡检.html"})
