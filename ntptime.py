import ntplib
from time import sleep

def time():
    c = ntplib.NTPClient()
    while True:
        try:
            response = c.request('192.168.2.11', version=3)
            break
        except:
            print 'Failed to connect to NTP server. Trying again.'
            sleep(0.1)
    return response.tx_time