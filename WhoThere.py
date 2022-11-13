import requests
import time
import lgpio
import cv2

CHIP = lgpio.gpiochip_open(0)
if CHIP >= 0:
	print("Chip setup")
	
PINS = [24,23,22,27]

STEPS = [
	[1,0,0,0],
	[1,1,0,0],
	[0,1,0,0],
	[0,1,1,0],
	[0,0,1,0],
	[0,0,1,1],
	[0,0,0,1],
	[1,0,0,1]]

OVERIDE = 4
TRIGGER = 6
ECHO = 5
#BUZZ = 12

CAM_PORT = 0
OPEN = 1
CHANGE = 0
TIME = 0

WEB_PORT = 8000



def INIT():
	
	lgpio.gpio_claim_output(CHIP, PINS[0])
	lgpio.gpio_claim_output(CHIP, PINS[1])
	lgpio.gpio_claim_output(CHIP, PINS[2])
	lgpio.gpio_claim_output(CHIP, PINS[3])
	
	#lgpio.gpio_claim_output(CHIP, BUZZ)
	lgpio.gpio_claim_output(CHIP, TRIGGER)
	lgpio.gpio_claim_input(CHIP, ECHO)
	lgpio.gpio_claim_input(CHIP, OVERIDE)
	

def Distance():
	
	lgpio.gpio_write(CHIP,TRIGGER,1)
	time.sleep(.00001)
	lgpio.gpio_write(CHIP,TRIGGER,0)
	
	startTime = time.time()
	stopTime = time.time()
	
	while lgpio.gpio_read(CHIP,ECHO) == 0:
		startTime = time.time()
		
	while lgpio.gpio_read(CHIP,ECHO) == 1:
		stopTime = time.time()
		
	timeElapsed = stopTime - startTime
	
	distance = (timeElapsed * 34300) / 2
	
	return distance
	
#def buzz():
#	tone = 1000
#	lgpio.tx_pulse(CHIP, BUZZ, tone,tone,0,round(500000/tone))
		
		
def doorOpen():
	print("Door Opened")
	for i in range(128):
		for state in STEPS:
			for pin in range(4):
				lgpio.gpio_write(CHIP,PINS[pin],state[pin])
			time.sleep(.001)
			
	for pin in range(4):
		lgpio.gpio_write(CHIP,PINS[pin],0)
	
	
def doorClose():
	print("Door Closed")
	for i in range(128):
		for state in reversed(STEPS):
			for pin in range(4):
				lgpio.gpio_write(CHIP,PINS[pin],state[pin])
			time.sleep(.001)
			
	for pin in range(4):
		lgpio.gpio_write(CHIP,PINS[pin],0)
	
def displayImage(image):
	cv2.imshow('Image',image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	
def callServer():
	
	CAMERA = cv2.VideoCapture(-1)
	result, image = CAMERA.read()
	if result:
		#displayImage(image)
		cv2.imwrite('Image.jpg',image)
		repacked = {'img' : open('Image.jpg','rb')}
		print("Sending Image")
		pack = {'img' : image}
		r = requests.post('http://100.88.45.13:8000',files=repacked)
		
		print("Image Sent")
	else:
		print("No Image Detected")
	
def stateMachine():
	global CHANGE
	global TIME
	global OPEN
	Cycles = 0
	Mod = 20	
	while True:
	
		if Cycles == Mod:
			r = requests.get('http://100.88.45.13:8000/door-status')
			print(r.content)
			if int(r.content) != OPEN :
				CHANGE = 1
			
			Cycles = 0
		else:
			CHANGE = lgpio.gpio_read(CHIP,OVERIDE)
			
			
		if CHANGE:
			if OPEN:
				doorOpen()
				CHANGE = 0
				OPEN = 0
			else:
				#buzz()
				doorClose()
				CHANE = 0
				OPEN = 1
		elif TIME == 0:
			dist = round(Distance(), 3)
			print(dist , "cm")
			if dist < 10:
				callServer()
				TIME = 5
		else:
			TIME -= 1
		Cycles += 1
		time.sleep(.5)



def Main():
	INIT()
	try:
		stateMachine()
	except Exception as e:
		print(e)
		print("Program Stopped")
		lgpio.gpiochip_close(CHIP)
		


if __name__ == "__main__":
	Main()
