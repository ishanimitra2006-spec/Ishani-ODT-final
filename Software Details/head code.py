from machine import Pin, PWM
import time


head = Pin(15, Pin.IN, Pin.PULL_UP)


headservo = PWM(Pin(22), freq=50)

while True:
    
    
    print("Left:",head.value())
    
    




    #detected
    if head.value() == 0:
        print("head detected")

        
        headservo.duty(70)
        time.sleep(1.5)

        
    else:    
        headservo.duty(110)
        time.sleep(1.5)
        print("hi")
        
    
    
            
    
    time.sleep(0.5)