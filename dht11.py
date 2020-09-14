# -*- coding: utf-8 -*-
"""
参考:
https://www.souichi.club/raspberrypi/temperature-and-humidity/
"""
# DHT11_Python
import RPi.GPIO as GPIO
from DHT11_Python import dht11 # 温湿度センサーモジュール

from time import sleep
from datetime import datetime

# mail
import smtplib, ssl
from email.mime.text import MIMEText

TEMP_SENSOR_PIN = 4 # 温湿度センサーのピンの番号
INTERVAL = 10 # 監視間隔（秒）
RETRY_TIME = 2 # dht11から値が取得できなかった時のリトライまでの秒数
MAX_RETRY = 20 # dht11から温湿度が取得できなかった時の最大リトライ回数

PLACE = 'yourplace' # 設置場所
HUM_MAX = 70.0  # 設定湿度
TEMP_MAX = 28.0 # 設定温度

GMAIL_ACCOUNT = 'frommail'
GMAIL_PASSWORD = 'password'
MAIL_TO = 'tomail'


class EnvSensorClass: # 温湿度センサークラス
    def GetTemp(self): # 温湿度を取得
        instance = dht11.DHT11(pin=TEMP_SENSOR_PIN)
        retry_count = 0
        while True: # MAX_RETRY回まで繰り返す
            retry_count += 1
            result = instance.read()
            if result.is_valid(): # 取得できたら温度と湿度を返す
                return result.humidity, result.temperature
            elif retry_count >= MAX_RETRY:
                return 99.9, 99.9 # MAX_RETRYを過ぎても取得できなかった時に温湿度99.9を返す
            sleep(RETRY_TIME)

GPIO.setwarnings(False) # GPIO.cleanup()をしなかった時のメッセージを非表示にする
GPIO.setmode(GPIO.BCM) # ピンをGPIOの番号で指定


def SendMail(temp, hum, detail):

    # メールデータ(MIME)の作成
    subject = 'Warning From {0}'.format(PLACE)
    msg = MIMEText(detail, "html")
    msg["Subject"] = subject
    msg["To"] = MAIL_TO
    msg["From"] = GMAIL_ACCOUNT

    # Gmailに接続
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10, context=context)
    server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
    server.send_message(msg) # メールの送信


def CreateMsg(temp, hum):

    # 現在日時
    ymdhms = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # ワーニングレベル
    level = "Info"
    if temp >= TEMP_MAX and hum >= HUM_MAX:
        level = "Warning-TEMP-HUM"
    elif temp >= TEMP_MAX:
        level = "Warning-TEMP"
    elif hum >= HUM_MAX:
        level = "Warning-HUM"

    # 温度と湿度
    tempstr = '{0:.1f}'.format(temp)
    humstr = '{0:.1f}'.format(hum)

    detail = '{0} [{1}] {2} {3}'.format(ymdhms, level, tempstr, humstr)
    return detail


try:
    if __name__ == "__main__":
        env = EnvSensorClass()
        while True:
            hum, temp = env.GetTemp() # 温湿度を取得
            detail = CreateMsg(temp, hum)

            if temp >= TEMP_MAX or hum >= HUM_MAX:
                SendMail(temp, hum, detail)
                print(detail + ' mailed')
            else:
                print(detail + ' -')

            break

            sleep(INTERVAL)

except KeyboardInterrupt:
    pass
GPIO.cleanup()

