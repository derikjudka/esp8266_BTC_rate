import utime
import machine

RS = machine.Pin(0, machine.Pin.OUT)
E = machine.Pin(1, machine.Pin.OUT)
D0 = machine.Pin(2, machine.Pin.OUT)
D1 = machine.Pin(3, machine.Pin.OUT)
D2 = machine.Pin(6, machine.Pin.OUT)
D3 = machine.Pin(8, machine.Pin.OUT)
D4 = machine.Pin(11, machine.Pin.OUT)
D5 = machine.Pin(13, machine.Pin.OUT)
D6 = machine.Pin(14, machine.Pin.OUT)
D7 = machine.Pin(15, machine.Pin.OUT)

def enable_pulse():
    E.value(1)
    utime.sleep_us(40)
    E.value(0)
    utime.sleep_us(40)

def send_LCD(binary_num):
    D0.value((binary_num & 0b00000001) >> 0)
    D1.value((binary_num & 0b00000010) >> 1)
    D2.value((binary_num & 0b00000100) >> 2)
    D3.value((binary_num & 0b00001000) >> 3)
    D4.value((binary_num & 0b00010000) >> 4)
    D5.value((binary_num & 0b00100000) >> 5)
    D6.value((binary_num & 0b01000000) >> 6)
    D7.value((binary_num & 0b10000000) >> 7)
    enable_pulse()

def configure_LCD():
    RS.value(0)
    #necessary special case of 'Function set' 
    send_LCD(0b00110000)
    send_LCD(0b00110000)
    send_LCD(0b00110000)
    
    #configure 8-bit bus, 2 lines
    send_LCD(0b00111000)

    #display on, cursor off, blink off
    send_LCD(0b00001100)
    
    #entry mode set
    send_LCD(0b00000100)
    
    #clear screen
    send_LCD(0b00000001)
    utime.sleep_ms(5)

def second_row():
    RS.value(0)
    send_LCD(0b10101001)
    utime.sleep_ms(2)
    
def clear_display():
    RS.value(0)
    send_LCD(0b00000001)
    utime.sleep_ms(2)
    
def return_home():
    RS.value(0)
    send_LCD(0b00000010)
    utime.sleep_ms(2)
             
def write_LCD(binary):
    RS.value(1)
    send_LCD(binary)