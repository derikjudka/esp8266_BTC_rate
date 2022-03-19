import machine
import time
import json
import lcd_gpio

uart = machine.UART(1,115200)

SSID = "" #enter wifi ssid here
PASSWORD = "" #enter wifi password here

def main():
    initial_config()
    
    while True:
        check_wifi_connection()
        output = send_request()
             
        clear_display()
        if output != -1:
            rate = get_rate(output)
            update_time = get_time(output)
        
            new_rate = "BTC: {} USD".format(str(int(rate)))
            new_time = "   {} GMT".format(update_time[16:21:1])
            
            display(new_rate)
            lcd_gpio.second_row()
            display(new_time)
            time.sleep(30)
        else:
            display('bad data!!!')
            uart.write('AT+CIPCLOSE\r\n')
            time.sleep(2)
            close_conn = serial_read()
            time.sleep(10)
            tcp_init()
            
        
def initial_config():
    lcd_gpio.configure_LCD()
    setup_esp()
    connect_wifi()
    time.sleep(5)
    tcp_init()

def serial_read():
    data = bytes()
    if uart.any() > 0:
        data = uart.read()
    return data

def setup_esp():
    uart.write('AT+RST\r\n')
    time.sleep(2)
    uart.write('AT+CWMODE=1\r\n')
    time.sleep(2)
    uart.write('AT+CIPMUX=0\r\n')
    time.sleep(2)
    uart.write('AT+CWQAP\r\n')
    time.sleep(2)
    setup_info = serial_read()
    return setup_info

def connect_wifi():
    uart.write('AT+CWJAP="'+SSID+'","'+PASSWORD+'"\r\n')
    time.sleep(6)
    wifi_info = serial_read().decode('utf-8')
    return wifi_info

def check_wifi_connection():
    uart.write('AT+CWJAP?\r\n')
    time.sleep(5)
    wifi_status = serial_read().decode('utf-8')
    while wifi_status.find('No AP') != -1:
        connect_wifi()
        
def get_esp_ip():
    uart.write('AT+CIFSR\r\n')
    time.sleep(5)
    esp_ip = serial_read().decode('utf-8')
    return esp_ip

def tcp_init():
    uart.write('AT+CIPSTART="TCP","api.coindesk.com",80\r\n')
    time.sleep(2)
    tcp_info = serial_read().decode('utf-8')
    return tcp_info
    
#send_request returns -1 for bad request
def send_request():
    if uart.any() > 0:
        uart.read()
    
    send = 'GET /v1/bpi/currentprice.json HTTP/1.1\r\n'
    send += 'Host: api.coindesk.com\r\n\r\n'
    msg_length = str(len(send))
    
    uart.write('AT+CIPSEND='+msg_length+'\r\n')
    time.sleep(0.01)
    clear_buf = serial_read()
            
    uart.write(send)
    buf = ''
    buf = serial_read().decode('utf-8').strip()
    while (buf.find('}}}') == -1):
        buf += serial_read().decode('utf-8').strip()
    
    if (buf.find('{"time"') == -1 or buf.find('}}}') == -1):
        return -1
    return buf

def get_rate(output):
    output = output[output.find('{"time"'):output.find('}}}')+3:1]
    rate = json.loads(output).get('bpi').get('USD').get('rate_float')
    return rate

def get_time(output):
    output = output[output.find('{"time'):output.find('}}}')+3:1]
    update_time = json.loads(output).get('time').get('updateduk')
    return update_time

def clear_display():
    lcd_gpio.clear_display()
    lcd_gpio.return_home()

def display(info):
    for i in info:
        val = ord(i)
        lcd_gpio.write_LCD(val)
     
main()