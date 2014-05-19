import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def sendImage(username, password, to_addr, image_name):
    img_data = open(image_name, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Captured IMAGE'
    msg['From'] = username
    msg['To'] = to_addr

    text = MIMEText("IMAGE sent!")
    msg.attach(text)
   
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    myip = MIMEText(s.getsockname()[0])
    msg.attach(myip)
   
    image = MIMEImage(img_data, 'jpg')
    image.add_header('Content-Disposition', 'attachment', filename=image_name)
    msg.attach(image)

    # Send the message
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(username, password)
    s.sendmail(username, [to_addr], msg.as_string())
    print 'Email sent'
    s.quit()
