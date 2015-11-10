# -*- coding: utf-8 -*-
import threading
import serial
import sys
import time

_preamble = '\xaa'
_postScript = '\x55'

_datLenFieldDelta = 0x02
_protVerFieldDelta = 0x01
_msgCRCFieldDelta = 0x01
_msgPSDelta = 0x02

sensor_list = ["Board MAC","TMP112","HTU21D","GP2Y1010AU0F","BMP180","PR103J2","TSL250RD","MMA8452Q","SPV1840LR5H-B","TSYS01","HMC5883L","HIH6130","APDS-9006-020","TSL260RD","TSL250RD","MLX75305","ML8511","D6T","MLX90614","TMP421","SPV1840LR5H-B","Total reducing gases","Ethanol (C2H5-OH)","Nitrogen Di-oxide (NO2)","Ozone (03)","Hydrogen Sulphide (H2S)","Total Oxidizing gases","Carbon Monoxide (C0)","Sulfur Dioxide (SO2)","SHT25","LPS25H","Si1145","Intel MAC"]

#decoded_output = ['0' for x in range(16)]

def format1 (input):
    byte1 = ord(input[0])
    byte2 = ord(input[1])
    value = (byte1 & 0x7F) + ((byte2 & 0x7F) * 0.01)
    if byte2 & 0x80 == 0x80:
        value = value * -1
    return value

def format2 (input):
    byte1 = ord(input[0])
    byte2 = ord(input[1])
    value = ((byte1 & 0x7F) << 8 )+ byte2
    return value

def format3 (input):
    return str(hex(ord(input)))[2:]

def format4 (input):
    byte1 = ord(input[0])
    byte2 = ord(input[1])
    value = ((byte1 & 0x3c) >> 2) + ((((byte1 & 0x03) << 8) + byte2) * 0.001)
    if byte1 & 0x40 == 0x40:
        value = value * -1
    return value

def format5 (input):
    byte1 = ord(input[0])
    byte2 = ord(input[1])
    value = ((byte1 & 0x3F) << 8) | (byte2)
    if byte1 & 0x40 == 0x40:
        value = value * -1
    return value

def format6 (input):
    byte1 = ord(input[0])
    byte2 = ord(input[1])
    byte3 = ord(input[2])
    value = ((byte1 & 0x3F) << 16 ) | (byte2 << 8) | byte3
    if (byte1 & 0x40) == 0x40:
        value = value * -1
    return value

def formatNULL (input):
    return input

def parse_sensor (sensor_id,sensor_data):
    if sensor_id == '0':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        data = ''
        for i in range(len(sensor_data)):
            data = data + str(format3(sensor_data[i]))
        print "Data:", data
        pass

    elif sensor_id == '1':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data)

    elif sensor_id == '2':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data[0:2]), format1(sensor_data[2:4])

    elif sensor_id == '3':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '4':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data[0:2]), format6(sensor_data[2:5])

    elif sensor_id == '5':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '6':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '7':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data[0:2]), format1(sensor_data[2:4]),format1(sensor_data[4:6]),format1(sensor_data[6:8])

    elif sensor_id == '8':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '9':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '10':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format4(sensor_data[0:2]),format4(sensor_data[2:4]),format4(sensor_data[4:6])

    elif sensor_id == '11':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data[0:2]), format1(sensor_data[2:4])

    elif sensor_id == '12':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '13':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '14':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '15':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '16':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    elif sensor_id == '17':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        data = ''
        for i in xrange(len(sensor_data)/2):
            data = data + str(format1(sensor_data[2*i:2*(i+1)])) + ' '
        print "Data:", data

    elif sensor_id == '18':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data)

    elif sensor_id == '19':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format1(sensor_data)

    elif sensor_id == '20':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data)

    #These are changing now, so have to be carefully checked.

    #gas sensors start here -->

    elif sensor_id == '21':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:",str(format6(sensor_data) << 1)
        #decoded_output[14] = str(format6(sensor_data) << 1)

    elif sensor_id == '22':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:",str(format6(sensor_data) << 1)
        #decoded_output[15] = str(format6(sensor_data) << 1)+'\n'

    elif sensor_id == '23':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[10] = str(format6(sensor_data) << 1)

    elif sensor_id == '24':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[9] = str(format6(sensor_data) << 1)

    elif sensor_id == '25':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[8] = str(format6(sensor_data) << 1)

    elif sensor_id == '26':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[13] = str(format6(sensor_data) << 1)

    elif sensor_id == '27':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[11] = str(format6(sensor_data) << 1)

    elif sensor_id == '28':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format6(sensor_data) << 1
        #decoded_output[12] = str(format6(sensor_data) << 1)

    # <-- gas sensors end here

    elif sensor_id == '29':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format5(sensor_data[0:2]),format5(sensor_data[2:4])
        #decoded_output[3] = str(format5(sensor_data[0:2]))
        #decoded_output[4] = str(format5(sensor_data[2:4]))

    elif sensor_id == '30':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        print "Data:", format5(sensor_data[0:2]) << 1, format6(sensor_data[2:5]) << 2
        #decoded_output[5] = str(format5(sensor_data[0:2]) << 1)
        #decoded_output[7] = str(format6(sensor_data[2:5]) << 2)

    elif sensor_id == '31':
        print "Sensor:", sensor_id, sensor_list[int(sensor_id)],'@',
        print "Data:", format2(sensor_data) << 1
        #decoded_output[6] = str(format2(sensor_data) << 1)

    elif sensor_id == '32':
        print "Sensor:", sensor_id,sensor_list[int(sensor_id)],'@',
        data = ''
        for i in range(len(sensor_data)):
            data = data + str(format3(sensor_data[i]))
        print "Data:", data
        #decoded_output[0] = '.*'+data

class usbSerial ( threading.Thread ):
    def __init__ ( self,port):
        self.port = port
        threading.Thread.__init__ ( self )
        self.lastSeq = 0
        self.currentSeq = 0
        self.repeatInt = 0.001
        self.data = []
        self.CoreSenseConf = 1
        self.dataLenBit = 0
        self.packetmismatch = 0

    def run (self):
        print time.asctime()
        #Checking if the port is still available for connection
        try:
            self.ser = serial.Serial(self.port,timeout=0)
            #print "device attached @ " + str(self.ser)
            self.keepAlive = 1
        except:
            #port unavalable. Between Inotify spanning the thread and the current
            #read the port has magically disappeared.
            #print "unable to open serial port"
            self.stop()
        print "> > >  usbSerial initiated on port"+str(self.port)+" @ "+str(time.asctime())
        self.counter = 0
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
        except:
            self.stop()

        #self.scObj = serviceClient(self.port, self.fromdevq,self.todevq)

        while self.keepAlive:

            time.sleep(self.repeatInt)

            try:
                self.counter = self.counter + 1
                if self.ser.inWaiting() > 0:
                    self.marshalData(self.ser.read(self.ser.inWaiting()))
                    self.counter = 0
            except:
                print "serial port not responding"
                self.stop()

            if (self.counter > 100000 or self.packetmismatch > 10) and (self.CoreSenseConf):
                print "not blade - error - " + str(self.counter) + " and " + str(self.packetmismatch)
                self.stop()

        print "< < <  usbSerial exit - port"+str(self.port)+" @ "+str(time.asctime())
        print ""


    def stop (self):
        self.keepAlive = False
        try :
            self.ser.close()
        except:
            pass


    def marshalData(self,_dataNew):
        self.data.extend(_dataNew)

        #at this point you just need to extract the message, check for crc and acknowledge the
        #receipt.

        while self.keepAlive:

            try:
                del self.data[:self.data.index(_preamble)]
                _preambleLoc = 0
            except:
                break;
            #check protocol version

            if (ord(self.data[_preambleLoc+_protVerFieldDelta]) == 0):
                #it is protocol version 0, and we can parse that data, using this script.
                try :
                    _postscriptLoc = ord(self.data[_preambleLoc+_datLenFieldDelta]) + _msgPSDelta + _datLenFieldDelta
                    if self.data[_postscriptLoc] == _postScript:
                        #we may have a valid packet, go ahead and set bytes
                        _packetCRC = 0
                        packetmismatch = 0

                        for i in range(_preambleLoc + _datLenFieldDelta + 0x01, _postscriptLoc):
                            _packetCRC = ord(self.data[i]) ^ _packetCRC
                            for j in range(8):
                                if (_packetCRC & 0x01):
                                    _packetCRC = (_packetCRC >> 0x01) ^ 0x8C
                                else:
                                    _packetCRC =  _packetCRC >> 0x01

                        if _packetCRC == 0x00:
                            #extract the data bytes alone, exclude preamble, prot version, len, crc and postScript
                            extractedData = self.data[_preambleLoc+3:_postscriptLoc-2]
                            consume_ptr = 0x00

                            while consume_ptr < len(extractedData):

                                This_id = str(ord(extractedData[consume_ptr]))
                                This_id_msg_size_valid = ord(extractedData [consume_ptr+1])
                                This_id_msg_size = This_id_msg_size_valid & 0x7F
                                This_id_msg_valid = (This_id_msg_size_valid & 0x80) >> 7
                                This_id_msg = extractedData [consume_ptr+2:consume_ptr+2+This_id_msg_size]
                                if (This_id_msg_valid == 1):
                                    parse_sensor (This_id, This_id_msg)
                                else:
                                    parse_sensor (This_id, This_id_msg)
                                    print "Invalid Message from sensor_id - ", This_id

                                consume_ptr = consume_ptr + 2 + This_id_msg_size


                            self.CoreSenseConf = 0

                            try:
                                pass
                                #self.fromdevq.put_nowait(extractedData)
                            except:
                                print "unable to put in buffer"
                        else:
                            print "CRC error.",

                    #bad packet, let us drop the packet
                    try:
                        del self.data[:self.data.index(_postScript)]
                    except:
                        pass

                    #try:
                        #del self.data[:self.data.index(_preamble)]
                    #except:
                        #pass

                except:
                    return

            else:
                # we either caught the wrong byte as preamble or have a packet with protocol version that
                # we do not know how to parse, so we will delete a byte and try and catch the preamble in
                #the next cycle
                try:
                    del self.data[0]
                except:
                    pass

                return


