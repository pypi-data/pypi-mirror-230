import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText


sender = '601178894@qq.com'
receivers = ['kivlin@tencent.com']

subject = 'test report'
from_name = 'from_name'
from_email = '601178894@qq.com'
to_mail = ['kivlin@tencent.com']
cc_mail = ['kivlin@tencent.com']

body = "hi, the attachment is the test report of this test, please check it in time."

msg = MIMEMultipart()
msg['Subject'] = Header(subject, 'utf-8')
msg['From'] = Header(from_name + ' <' + from_email + '> ')
msg['To'] = Header(','.join(to_mail), 'utf-8')
msg['Cd'] = Header(','.join(cc_mail), 'utf-8')
msg_text = MIMEText(body, "html", "utf-8")
msg.attach(msg_text)

server_ip = 'smtp.qq.com'
server_port = 465
auth_name = '601178894@qq.com'
auth_pwd = 'cooqwbyzgocjbbbh'



try:
    server = smtplib.SMTP_SSL(server_ip, server_port)
    server.login(auth_name, auth_pwd)
    server.sendmail(sender, receivers, msg.as_string())
    print("succ")
except Exception as e:
    print(e)
finally:
    server.quit()