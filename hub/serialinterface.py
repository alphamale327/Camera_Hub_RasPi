
from collections import deque
import threading
import datetime
import serial
import time

class serialThread(threading.Thread):
    def __init__(self, threadID, device, baud_rate, timeout_val, data_queue, command_queue):  
        threading.Thread.__init__(self) 
        self.ser = serial.Serial(device, baud_rate, timeout=timeout_val)
        self.ID = threadID
        self.state = 'waiting'
        self.databuffer = ''
        self.data_queue = data_queue
        self.command_queue = command_queue

    def run(self):
        
        strbyte = self.ser.read()
        lastbyte = ''
        while True:
            if len(self.command_queue) > 0 and self.state == 'waiting':
                self.state = 'writing'
                self.ser.write(self.command_queue.popleft())    # Write command to serial port
                self.state = 'waiting'
            else:
                if strbyte == '':
                    time.sleep(1)
                    if self.state != 'waiting':
                        self.state = 'waiting'
                        self.databuffer = ''
                else:
                    self.state = 'reading'
                    self.databuffer += strbyte
                    if strbyte.encode('hex') == '7e':
                        for x in range(0,7):
                            dump = self.ser.read()
                        self.databuffer = ''
                    else:
                        # If data is a jpg image:
                        if lastbyte.encode("hex") == 'ff' and strbyte.encode('hex') == 'd8':
                            print 'JPG recognized, downloading...'
                            image_file = self.getJPG()
                            if image_file != 'error':
                                print 'JPG successfully downloaded'
                                timestamp = datetime.datetime.now().strftime('%B%d_%Y %I:%M:%S')
                                self.data_queue.append(('image','/var/www/pictures/%s.jpg' % timestamp, image_file))
                            else:
                                print 'Malformed JPEG File'
                        
                        # If data is battery life:
                        if strbyte.encode('hex') == 'f1':
                            print 'Battery Life recognized, downloading...'
                            batterylife = self.getBatteryLife()
                            self.data_queue.append(('battery_life', batterylife))

                        # If command successfully executed:
                        if strbyte.encode('hex') == 'f8':
                            print 'Command successfully executed...'
                            self.data_queue.append(('command_executed', 'True'))

                        # If command not successfully executed:
                        if strbyte.encode('hex') == 'f9':
                            print 'Command failed to execute...'
                            self.data_queue.append(('command_executed', 'False'))

                # Get next byte
                lastbyte = strbyte
                strbyte = self.ser.read()
    def getJPG(self):
        strbyte = self.ser.read()
        nextbyte = ''
        while strbyte != '':
            nextbyte = self.ser.read()
            if strbyte.encode('hex') == '7e':
                if nextbyte.encode('hex') == '00': 
                    for x in range(0,6):
                        dump = self.ser.read()
                    nextbyte = self.ser.read()    
                else:
                    self.databuffer += strbyte
                    self.databuffer += nextbyte
            elif strbyte.encode("hex") == 'ff' and nextbyte.encode('hex') == 'd9':
                self.databuffer += strbyte
                self.databuffer += nextbyte
                return self.databuffer
            else:                
                if not nextbyte.encode('hex') == '7e':
                    self.databuffer += strbyte
            strbyte = nextbyte
        # End of JPG was not sent or detected
        return 'error'

    def getBatteryLife(self):
        strbyte = self.ser.read()

        while strbyte != '':
            self.databuffer += strbyte
            strbyte = self.ser.read()

        return self.databuffer
        
    def getState(self):
        return self.state