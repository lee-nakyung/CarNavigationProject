import os; import io; import time
import RPi.GPIO as GPIO
import picamera
import cv2; import numpy as np
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio
sda = 2
scl = 3
i2c = busio.I2C(scl, sda)
sensor = HTU21D(i2c)

trig = 20; echo = 16 #  초음파 센서를 대한 전역 변수 선언 및 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.output(trig, False)

fileName = ""
stream = io.BytesIO()
camera = picamera.PiCamera()
camera.start_preview()
camera.resolution = (320, 240)
time.sleep(1)

def measureDistance(): # 초음파센서    - 거리    측정    함수
    global trig, echo
    time.sleep(0.5)
    GPIO.output(trig, True) #  신호   1 발생
    time.sleep(0.00001) #  짧은    시간을    나타내기   위함
    GPIO.output(trig, False) #  신호   0 발생

    while(GPIO.input(echo) == 0):
        pass
    pulse_start = time.time() #  신호   1을   받았던   시간
    while(GPIO.input(echo) == 1):
        pulse_end = time.time() #  신호    0을   받았던   시간
    pulse_duration = pulse_end - pulse_start
    return 340*100/2*pulse_duration

def getTemperature():
        return float(sensor.temperature)

def getHumidity():
        return float(sensor.relative_humidity)

def takePicture() :
        global fileName, stream, camera

        if len(fileName) != 0:
                os.unlink(fileName)

        stream.seek(0)
        stream.truncate()
        camera.capture(stream, format='jpeg', use_video_port=True)
        data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, 1)
        haar = cv2.CascadeClassifier('./haarCascades/haar-cascade-files-master/haarcascade_frontalface_default.xml')
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = haar.detectMultiScale(image_gray,1.1,3)
        for x, y, w, h in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        takeTime = time.time()
        fileName = "./static/%d.jpg" % (takeTime * 10)
        cv2.imwrite(fileName, image)
        return fileName



led = 6 # LED  점등을   위한   전역    변수    선언    및   초기화
GPIO.setup(led, GPIO.OUT) # GPIO 6번   핀을   출력   선으로    지정

def ledin():
    onOff=1
    controlLED(led, onOff)

def ledOut():
    onOff=0
    controlLED(led, onOff)

def controlLED(led = 6, onOff =0 ): # led  번호의    핀에    onOff(0/1)  값    출력
    GPIO.output(led, onOff)

if __name__ == '__main__' :
    while(True):
        distance = measureDistance() #거리    값    불러옴
        print("distance=%f" % distance) #거리    값   출력
        temp = getTemperature()
        print("temp=%3d" % temp)
        humi = getHumidity()
        print("humi=%3d" %  humi)
        name = takePicture() #사진   촬영
        print("fname= %s" % name) #사진   파일    이름    출력
