import RPi.GPIO as GPIO

LED = 11                                                                    # GPIO pin for the LED
REDBUTTON = 16                                                              # GPIO pin for the red button
GREENBUTTON = 15                                                            # GPIO pin for the green button
runApp = 0                                                                  # Boolean variable to start (True) and stop (False) the controller

def GPIO_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(REDBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GREENBUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(REDBUTTON, GPIO.RISING, callback=handle_buttonINT, bouncetime=1000)       # handle_redbutton
    GPIO.add_event_detect(GREENBUTTON, GPIO.RISING, callback=handle_buttonINT, bouncetime=1000)     # handle_greenbutton

def handle_buttonINT(channel):
    if channel == REDBUTTON:
        set_runApp(False)
        print("red")
        GPIO.output(11, 0)
    elif channel == GREENBUTTON:
        set_runApp(True)
        print("green")
        GPIO.output(11, 1)

def set_runApp(state):
    global runApp
    runApp = state

def get_runApp():
    return runApp

def clean_gpio():
    GPIO.cleanup()