import sendimage
from serialinterface import serialThread
from collections import deque
import serial
from xbee import XBee
import datetime
import time
import os.path

PORT='/dev/ttyUSB0'
BAUD_RATE=57600

ser = serial.Serial(PORT, BAUD_RATE)

# ZB XBee here. If you have Series 1 XBee, try XBee(ser) instead
xbee=XBee(ser)

#MAC, number written on the back of the XBee module
# CO3 = my coordinator
# EP1 = my endpoint
device={
        "CO3":'\x00\x13\xa2\x00\x40\xa7\x9b\xad',
        "EP1":'\x00\x13\xa2\x00\x40\xb3\x65\x5c'
}

data_queue = deque([])
command_queue = deque([])
serialMonitor = serialThread(1, PORT, BAUD_RATE,1, data_queue, command_queue)
serialMonitor.start()

logfile = datetime.datetime.now().strftime('%b_%d_%Y')
if not os.path.isfile('/var/www/logFiles/%s.txt' %logfile):
    f = open('/var/www/logFiles/%s.txt' %logfile, 'w')
    f.close

def writeLog(string):
    global logfile
    daynow = datetime.datetime.now().strftime('%b_%d_%Y')
    timestamp = datetime.datetime.now().strftime('%B_%d_%Y__%I:%M:%S')
    if daynow == logfile:
        f = open('/var/www/logFiles/%s.txt' %logfile, 'a')
    else:
        logfile = datetime.datetime.now().strftime('%b_%d_%Y')
        f = open('/var/www/logFiles/%s.txt' % logfile, 'w')
    f.write('%s     %s' %(timestamp, string))
    f.close
    
while True:
    time.sleep(1)
    # Check Data Queue
    if len(data_queue) > 0:
        data = data_queue.popleft()

        if data[0] == 'image':
            with open(data[1], 'w') as image_file:
                image_file.write(data[2])
            email_file = open("/var/www/web/emailAddress.txt", "r") 
            email_address = email_file.read()
            sendimage.sendImage('sskyler.lee@gmail.com', 'leesy6714', email_address, data[1])
            print 'To: ' + email_address
            email_file.close()
            writeLog('A motion detected. Email Sent\n')
        if data[0] == 'battery_life':
            print 'Battery Life: ' + data[1].encode("hex")

        if data[0] == 'command_executed':
            print 'Command executed: ' + data[1]
    
    command_file = open("/var/www/web/command.txt", "r+")
    command = command_file.read()
    if command != '':
        print 'Command received: ' + command 
        # PIR Sensing Disable
        if command == '1': 
            print 'Motion Sensing Disable'
            writeLog('Motion Sensing Disable\n')
            xbee.remote_at(dest_addr_long=device["EP1"],command='D0',parameter='\x05')
            time.sleep(1)		
            xbee.remote_at(dest_addr_long=device["EP1"],command='D0',parameter='\x04')
        # PIR Sensing Enable
        elif command == '2':
            print 'Motion Sensing Enable'
            writeLog('Motion Sensing Enable\n')
            xbee.remote_at(dest_addr_long=device["EP1"],command='D1',parameter='\x05')
            time.sleep(1)		
            xbee.remote_at(dest_addr_long=device["EP1"],command='D1',parameter='\x04')
        # Take a picture		
        elif command == '3':
            print 'Take A Picture'
            writeLog('Take A Picture\n')
            xbee.remote_at(dest_addr_long=device["EP1"],command='D2',parameter='\x05')
            time.sleep(1)		
            xbee.remote_at(dest_addr_long=device["EP1"],command='D2',parameter='\x04')
		# Check Battery	
        elif command == '4':
            print 'Check Battery Life'
            writeLog('Check Battery Life\n')
            xbee.remote_at(dest_addr_long=device["EP1"],command='D3',parameter='\x05')
            time.sleep(1)		
            xbee.remote_at(dest_addr_long=device["EP1"],command='D3',parameter='\x04')
        command_file.seek(0)
        command_file.truncate()
    command_file.close()