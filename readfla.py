# -*- coding: utf8 -*- 
from flask import Flask, render_template_string
import os, glob, time
import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import RPi.GPIO as GPIO
import serial
app = Flask(__name__)

#os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
ser = serial.Serial('/dev/serial0', 9600) # 프로그램 호환성을 위해 ‘ttyS0’ 또는 ‘ttyAMA0’

COLUMNS = 16
ROWS = 2

RS = digitalio.DigitalInOut(board.D22)
EN = digitalio.DigitalInOut(board.D11)
D4 = digitalio.DigitalInOut(board.D23)
D5 = digitalio.DigitalInOut(board.D10)
D6 = digitalio.DigitalInOut(board.D9)
D7 = digitalio.DigitalInOut(board.D25)
lcd = characterlcd.Character_LCD_Mono(RS, EN, D4, D5, D6, D7, COLUMNS, ROWS)

GPIO.setmode(GPIO.BCM)
LED1=25
LED2=16
GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)

buzzer = 20
GPIO.setup(buzzer, GPIO.OUT)

d = 0

control_page = """
<script>
setTimeout(function(){location.reload();},1000);
</script>
<h1>Person : {{person}}</h1>
<h1>Temp : {{temp}}</h1>
"""


@app.route('/')
def serve():
	read_temp_raw()
	temp= read_temp()
	person = uartrx()
	lcd_check(temp)
	led_check(temp)	
	return render_template_string(control_page,temp=temp,person=person)
	
def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
	temp_c = float(temp_string) / 1000.0
	return temp_c

def lcd_check(a):
	lcd.clear( )
	lcd.cursor_position(1, 0)
	lcd.message = '<< Temp >>'
	lcd.cursor_position(2, 1)
	lcd.message = str(a)
	time.sleep(5)

def led_check(a):
	
    if(a>=30):
        ledbu(True)
    else:
        ledbu(False)
def ledbu(check):
    if (check):
        GPIO.output(LED1,True)
        GPIO.output(LED2,False)
        pwm = GPIO.PWM(buzzer, 1.0)
        pwm.start(50.0)
        for cnt in range(0,3):	
            pwm.ChangeFrequency(262)
            time.sleep(1.0)
            pwm.ChangeFrequency(294)   
            time.sleep(1.0)
            pwm.ChangeFrequency(330)   
            time.sleep(1.0)
        pwm.ChangeDutyCycle(0.0)
    else:
        GPIO.output(LED1,False)
        GPIO.output(LED2,True)
def uartrx():
    if ser.readable( ):
        rxd = ser.read( )
        d = (int)(rxd.decode())
        print('person : ' + rxd.decode( ))
        if(d >= 5):
            ledbu(True)
        else:
            ledbu(False)
    return(d)


if __name__ == "__main__":
	app.run(host='localhost', port=8082)
