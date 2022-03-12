import machine
import time
import json

uart = machine.UART(1,115200)

SSID = "" #enter wifi ssid here
PASSWORD = "" #enter wifi password here

def main():
    setup_esp()
    connect_wifi()
    time.sleep(5)
    tcp_init()
    
    while True:
        check_wifi_connection()
        output = send_request()
        if output != -1:
            rate = get_rate(output)
            update_time = get_time(output)
            print("BTC: {} USD\nUpdated: {}".format(rate, update_time))
        else:
            uart.write('AT+CIPCLOSE\r\n')
            time.sleep(2)
            close_conn = serial_read()
            time.sleep(2)
            tcp_init() 
        time.sleep(15)

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
    wifi_info = serial_read()
    wifi_info = wifi_info.decode('utf-8')
    return wifi_info

def check_wifi_connection():
    uart.write('AT+CWJAP?\r\n')
    time.sleep(5)
    wifi_status = serial_read()
    wifi_status = wifi_status.decode('utf-8')
    while wifi_status.find('No AP') != -1:
        print('NO WIFI...MUST RECONNECT')
        connect_wifi()
        
def get_esp_ip():
    uart.write('AT+CIFSR\r\n')
    time.sleep(5)
    esp_ip = serial_read()
    esp_ip = esp_ip.decode('utf-8')
    return esp_ip

def tcp_init():
    uart.write('AT+CIPSTART="TCP","api.coindesk.com",80\r\n')
    time.sleep(2)
    tcp_info = serial_read()
    tcp_info = tcp_info.decode('utf-8')
    return tcp_info
    
#send_request returns -1 for bad request
def send_request():
    if uart.any() > 0:
        uart.read()
        
    send = 'GET /v1/bpi/currentprice.json HTTP/1.1\r\n'
    send += 'Host: api.coindesk.com\r\n'
    send += '\r\n'
    msg_length = str(len(send))
    
    uart.write('AT+CIPSEND='+msg_length+'\r\n')
    time.sleep(1)
    info_size = serial_read()
            
    uart.write(send+'\r\n')
    time.sleep(0.1)
    buf1 = serial_read()
    
    count1 = 0
    while buf1.decode('utf-8').find('+IPD') == -1:
        buf1 = serial_read()
        count1 += 1
        time.sleep(0.5)
        if count1 > 10:
            return -1
    buf1 = buf1.decode('utf-8')
    
    time.sleep(0.002)
    uart.write('+++')
    time.sleep(0.002)

    buf2 = serial_read()
    
    if (buf1.find('{"time"') == -1 and buf1.find('}}}') == -1):
        count2 = 0
        while (buf2.decode('utf-8').find('}}}') == -1):
            buf2 += serial_read()
            count2 += 1
            time.sleep(0.5)
            if count2 > 10:
                return -1
        buf2 = buf2.decode('utf-8')
        if (buf2.find('{"time"') == -1):
            return -1
    
        time.sleep(1)
    
    if uart.any() > 0:
        uart.read()
    time.sleep(0.5)
    
    if isinstance(buf2, str):
        output = buf1 + buf2
    else:
        output = buf1 + buf2.decode('utf-8')
    return output

def get_rate(output):
    output = output[output.find('{"time"'):output.find('}}}')+3:1]
    rate = json.loads(output).get('bpi').get('USD').get('rate_float')
    return rate

def get_time(output):
    output = output[output.find('{"time'):output.find('}}}')+3:1]
    update_time = json.loads(output).get('time').get('updateduk')
    return update_time
    
main()
