from machine import Pin, PWM, TouchPad
import time
import neopixel

head_sensor = Pin(15, Pin.IN, Pin.PULL_UP)
head_servo  = PWM(Pin(22), freq=50)

tail_touch  = TouchPad(Pin(14))
tail_servo  = PWM(Pin(13), freq=50)

S0 = Pin(33, Pin.OUT); S0.value(1)   
S1 = Pin(5,  Pin.OUT); S1.value(0)
S2 = Pin(19, Pin.OUT)
S3 = Pin(32, Pin.OUT)
OUT = Pin(18, Pin.IN)

np = neopixel.NeoPixel(Pin(21, Pin.OUT), 16)

R_MIN, R_MAX = 126, 1167
G_MIN, G_MAX = 120,  891
B_MIN, B_MAX = 164, 1120

def read_channel(s2, s3):
    S2.value(s2); S3.value(s3)
    time.sleep_ms(5)
    count, end, last = 0, time.ticks_add(time.ticks_ms(), 80), OUT.value()
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        cur = OUT.value()
        if last == 1 and cur == 0:
            count += 1
        last = cur
    return count

def map_val(v, lo, hi):
    return max(0, min(255, int((v - lo) * 255 / (hi - lo))))

def set_pixels(r, g, b):
    for i in range(16):
        np[i] = (r, g, b)
    np.write()

servo_busy = False
head_t = tail_t = col_t = 0
head_s = tail_s = col_s = 0   
cur_r, cur_g, cur_b = 101, 67, 33

set_pixels(101, 67, 33)   # default brown

while True:
    now = time.ticks_ms()

    # HEAD: sensor → servo
    if head_s == 0 and time.ticks_diff(now, head_t) >= 0:
        if head_sensor.value() == 0 and not servo_busy:
            servo_busy = True
            head_servo.duty(70)
            head_t = time.ticks_add(now, 1500)
            head_s = 1
        else:
            head_servo.duty(110)
            head_t = time.ticks_add(now, 300)
    elif head_s == 1 and time.ticks_diff(now, head_t) >= 0:
        head_servo.duty(110)
        head_t = time.ticks_add(now, 400)
        head_s = 2
    elif head_s == 2 and time.ticks_diff(now, head_t) >= 0:
        servo_busy = False
        head_t = time.ticks_add(now, 300)
        head_s = 0

    # TAIL: touch → wag
    if tail_s == 0 and time.ticks_diff(now, tail_t) >= 0:
        if tail_touch.read() < 200 and not servo_busy:
            servo_busy = True
            tail_servo.duty(35)
            tail_t = time.ticks_add(now, 750)
            tail_s = 1
        else:
            tail_t = time.ticks_add(now, 200)
    elif tail_s == 1 and time.ticks_diff(now, tail_t) >= 0:
        tail_servo.duty(110)
        tail_t = time.ticks_add(now, 750)
        tail_s = 2
    elif tail_s == 2 and time.ticks_diff(now, tail_t) >= 0:
        servo_busy = False
        tail_t = time.ticks_add(now, 200)
        tail_s = 0

    # COLOUR: read sensor → update NeoPixel
    if col_s == 0 and time.ticks_diff(now, col_t) >= 0:
        col_s = 1
    elif col_s == 1:
        r = map_val(read_channel(0, 0), R_MIN, R_MAX)
        g = map_val(read_channel(1, 1), G_MIN, G_MAX)
        b = map_val(read_channel(0, 1), B_MIN, B_MAX)
        if abs(r-cur_r) > 12 or abs(g-cur_g) > 12 or abs(b-cur_b) > 12:
            set_pixels(r, g, b)
            cur_r, cur_g, cur_b = r, g, b
            print("RGB:", r, g, b)
        col_t = time.ticks_add(time.ticks_ms(), 300)
        col_s = 0