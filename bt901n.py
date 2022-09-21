"""
Interface object to WITmotion BT901 gyroscope
(pair with adapter, default pw 1234)

 data is sent in 11 byte messages.
 1st byte = 0x55 = b'U'
 2nd bytes defined type
 0x50, b'P' - time

 0x51, b'Q' - acceleration
 0x52, b'R' - gyro
 0x53, b'S' - angle
 0x54, b'T' - mag

- other models have...
 0x55, b'U' - Dstatus
 0x56, b'V' - Pressure
 0x57, b'W' - LonLat
 0x58, b'X' - GPS
 
 
 Usage:
 
 1) Create interface object
 
 bt = BT901(port='com4')
 
 2) [optional] configure data types - angle only is default.
 
 bt.enable_accel(True)
 bt.enable_gyro(True)
 bt.enable_mag(True)
 
 3) To make a measurment...
 
 bt.reset_data()   #clear any previously logged data and data waiting on serial port
 
 bt.start_logging() # starts logging new data
 bt.stop_logging()  #stop the measurments
 
 
 data logged can be accessed via lists:
 
 bt.time
 bt.accel
 bt.gyro
 bt.angle
 bt.mag

"""
import serial
import struct
import threading
import numpy as np
import time

class BT901():
    def __init__(self, port='com4'):
        self.port = serial.Serial( port, 115200, timeout=1)

        #seems to need a save or reset to accept other commands
        #self.reset_to_default()
        
        # return data types (11 on/off bits)
        self._ret_lowbyte = b'\x08'     #default is angle only
        self._ret_highbyte =  b'\x00'   #only 1st three bytes are used
        self.config_command(b'\x02', self._ret_lowbyte, self._ret_highbyte)
        self.reset_to_default()

        # lists to store data
        self.time  = []     #time data (Y,M,D,h,m,s)
        self.accel = []     #acceleration data (ax,ay,az, Temp)
        self.gyro  = []     #gyroscope data (wx,wy, wz, Temp) deg/s
        self.angle = []     #angle data (thetax, thetay, thetaz) deg
        self.angle2 = []    #angle data (thetax, thetay, thetaz, Temp) deg
        self.mag   = []     #magnetic field (hx,hy,hz)
        
        #logging thread
        self.thread = None
        self._stop_thread = False
        
    def __del__(self):
        self.close()#changed from self.port.close() to prevent error
        
    def close(self):
        """
        Close the serial port.
        """
        try:
            self.port.close()
        except: 
            pass
        
    # configuration ------------------------------------------------------------
    def config_command(self, address, lowByte, highByte):
        """
        Send a config command
        address to write e.g. b'\x1b' LEDOFF Turn off LED
        data (2bytes)    e.g. short int 0/1 for LEDOFF 
        """
        #config command is 2 bytes header
        cmd = b'\xFF\xAA' + address + lowByte + highByte
        self.port.write(cmd)
        savecmd = b'\xFF\xAA\x00\x00\x00'
        self.port.write(savecmd)
        self.port.flush()
        
    def save_config(self):
        """
        Save configuration on device
        """
        self.config_command(b'\x00', b'\x00', b'\x00')
        
    def reset_to_default(self):
        """
        Reset device to default configuration
        """
        self.config_command(b'\x00', b'\x01', b'\x00')
    
    def _enable_data(self, bit, flag):
        """
        internal method to enable disable data types
        """
        if flag:
            #sets bit to 1
            self._ret_lowbyte = bytes([ self._ret_lowbyte[0] | (1<<bit)])
        else:
            #sets bit to 0
            self._ret_lowbyte = bytes([ self._ret_lowbyte[0] & ~(1<<bit)])
        self.config_command(b'\x02', self._ret_lowbyte, self._ret_highbyte)
        
    def enable_time(self, flag=True):
        """
        Enable return of time data
        """
        self._enable_data(0, flag)
        
    @property
    def time_enabled(self):
        """
        Return True/False if time data is enabled
        """
        return self._ret_lowbyte[0] & (1<<0) #get bit 0 from byte
    
    def enable_accel(self, flag=True):
        """
        Enable return of acceleration data
        """
        self._enable_data(1, flag)

    @property
    def accel_enabled(self):
        """
        Return True/False if acceleration data is enabled
        """
        return self._ret_lowbyte[0] & (1<<1) #get bit 1 from byte

    def enable_gyro(self, flag=True):
        """
        Enable return of gyroscope data
        """
        self._enable_data(2, flag)

    @property
    def gyro_enabled(self):
        """
        Return True/False if gyroscope data is enabled
        """
        return self._ret_lowbyte[0] & (1<<2) #get bit 2 from byte

    def enable_angle(self, flag=True):
        """
        Enable return of angle data
        """
        self._enable_data(3, flag)

    @property
    def angle_enabled(self):
        """
        Return True/False if angle data is enabled
        """
        return self._ret_lowbyte[0] & (1<<3) #get bit 3 from byte
        
    def enable_mag(self, flag=True):
        """
        Enable return of magnetic field data
        """
        self._enable_data(4, flag)
    
    @property
    def mag_enabled(self):
        """
        Return True/False if magnetic field data is enabled
        """
        return self._ret_lowbyte[0] & (1<<4) #get bit 4 from byte
        
    # read data and store internally
    def read_data(self):
        
        # Each message is 11 bytes...
        # byte 0 = 0x55
        # byte 1 = data type
        # bytes 2-10 = data
        # byte 11 = checksum
        msg = self.port.read(11)
        #read until 1st byte is correct
        while msg[0]!=0x55:
            msg = msg[1:]+self.port.read(1)
            
        #check the message checksum
        if self._checksum(msg) is False:
            #ignore for now
            return 
        
        #Unpack and log
        dtype = msg[1]
        data = msg[2:10]
        
        # time 
        if dtype == 0x50: #P
            ts = self._get_timestamp(data)
            self.time.append(ts)
            
        # acceleration
        elif dtype == 0x51: # Q
            ax,ay,az,T = self._get_acceleration(data)
            self.accel.append( (ax,ay,az,T) )
        
        # gyro
        elif dtype== 0x52: # R
            wx,wy,wz,T = self._get_gyro(data)
            self.gyro.append( (wx,wy,wz,T) )

        #angle
        elif dtype == 0x53: # S
            # angle
            tx,ty,tz = self._get_angle(data)
            self.angle.append( (tx,ty,tz) )
            
            #version using struct. for test (includes Temp)
            tx,ty,tz,T = self._get_angle2(data)
            self.angle2.append( (tx,ty,tz,T) )
            
        #magnetic field
        elif dtype == 0x54: # T
            hx,hy,hz,T = self._get_magnetic_field(data)
            self.mag.append( (hx,hy,hz,T))

    # internal read methods for different data types
    def _get_timestamp(self, data):
            # from JY901.h
            #unsigned char ucYear;  == bytes , struct code 'B'
            #unsigned char ucMonth;
            #unsigned char ucDay;
            #unsigned char ucHour;
            #unsigned char ucMinute;
            #unsigned char ucSecond;
            #unsigned short usMiliSecond; == 2bytes, struct 'H'
            #unpack
            Y,M,D,h,m,s,ms = struct.unpack('BBBBBBh', data)
            #print(f'Time: {Y}:{M}:{D} {h}:{m}:{s}')
            return  (h*60*60)+(m*60)+s+(ms/1000) #Amended to return in seconds
            # return Y,M,D,h,m,s,ms 
        
    def _get_acceleration(self, data):
        # from JY901.h
        # short a[3];
        # short T;
        ax,ay,az,T = struct.unpack('hhhh', data)
        return ax,ay,az,T
        
    def _get_gyro(self, data):
        # from JY901.h
        # short w[3];
        # short T;
        wx,wy,wz,T = struct.unpack('hhhh', data)
        return wx,wy,wz,T
        
    def _get_angle(self, data):
        rxl = data[0]                                        
        rxh = data[1]
        ryl = data[2]                                        
        ryh = data[3]
        rzl = data[4]                                        
        rzh = data[5]
        k_angle = 180
     
        angle_x = (rxh << 8 | rxl)/32768 * k_angle
        angle_y = (ryh << 8 | ryl)/32768 * k_angle
        angle_z = (rzh << 8 | rzl)/32768 * k_angle
        if angle_x >= k_angle:
            angle_x -= 2 * k_angle
        if angle_y >= k_angle:
            angle_y -= 2 * k_angle
        if angle_z >=k_angle:
            angle_z-= 2 * k_angle
     
        return angle_x, angle_y, angle_z
        
    def _get_angle2(self, data):
        # from JY901.h
        # short Angle[3]
        # short T;
        tx,ty,tz,T = struct.unpack('hhhh', data)
        return tx,ty,tz,T
        
    def _get_magnetic_field(self, data):
        # from JY901.h
        # short h[3];
        # short T;
        hx,hy,hz,T = struct.unpack('hhhh', data)
        return hx,hy,hz,T
        
    def _checksum(self, data):
        sum = data[0]+data[1]+data[2]+data[3]+data[4]+data[5]+data[6]+data[7]+data[8]+data[9]
        return (sum&0xFF)==data[10]
        
    # Log in a thread
    def start_logging(self):
        """
        Start logging thread.
        """
        if self.thread != None:
            raise RuntimeError('Thread already running')
        self.thread = threading.Thread(target=self._log)
        self.thread.start()
        
    def _log(self):
        """internal logging function called by thread."""
        while self._stop_thread is False:
            while self.port.in_waiting>0:
                self.read_data()
            time.sleep(0.1)
        self.thread = None
        self._stop_thread = False
        
    def stop_logging(self):
        """Stop the logging thread."""
        if self.thread == None:
            raise RuntimeError('No Thread running')
        self._stop_thread = True
        
    def reset_data(self):
        """
        Clear any waiting data and reset internal lists
        """
        while self.port.in_waiting>0:
            self.port.reset_input_buffer()
            #self.port.read_all()
            
        self.time = []         #time data (Y,M,D,h,m,s)
        self.accel = []     #acceleration data (ax,ay,az, Temp)
        self.gyro  = []     #gyroscope data (wx,wy, wz, Temp) deg/s
        self.angle = []     #angle data (thetax, thetay, thetaz) deg
        self.angle2 = []     #angle data (thetax, thetay, thetaz, Temp) deg
        self.mag   = []     #magnetic field (hx,hy,hz, Temp)
        
    def get_data(self):
        """
        Returns data as arrays:
            returns: t,acc,gyro, angle, mag
        """
        t = np.array(self.time)
        a = np.array(self.accel)
        g = np.array(self.gyro)
        ang = np.array(self.angle)
        mag = np.array(self.mag)
        
        return t,a,g,ang,mag
