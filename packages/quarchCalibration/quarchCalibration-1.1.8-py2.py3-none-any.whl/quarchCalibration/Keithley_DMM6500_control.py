import socket
from quarchCalibration.deviceHelpers import locateMdnsInstr
from quarchpy.user_interface import *

'''
Prints out a list of calibration instruments nicely onto the terminal, numbering each unit
'''
#def listCalInstruments(scanDictionary):
#    if (not scanDictionary):
#        print ("No instruments found to display")
#    else:
#        x = 1
#        for k, v in scanDictionary.items():
#            # these items should all be Keysight DMM6500 AC Power Sources
#            # form of the value is '._scpi-raw._tcp.local.'
#            # we want to extract name, serial number and ip address
#            ip = k
#            # if we recognise the device, pull out the serial number
#            if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
#                id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
#            else:
#                id = v  # else we don't recognise the device, return the whole identifier unmodified
#            print (str(x) + " - " + id + "\t" + ip)
#            x += 1

'''
Allows the user to select a test instrument
'''
def userSelectCalInstrument(scanDictionary=None, scanFilterStr="DMM6500", title=None, message=None, tableHeaders= None, additionalOptions = None, nice=False):
    #Initiate values. Originals must be stored for the case of a rescan.
    originalOptions = additionalOptions
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        nice = False
    if message is None: message = "Select the calibration instrument to use:"
    if title is None: title = "Select a calibration instrument"
    while(True): #breaks when valid user input given
        # Scan first, if no list is supplied
        if (scanDictionary is None):
            printText ("Scanning for instruments...")
            scanDictionary = foundDevices = locateMdnsInstr(scanFilterStr)

        deviceList = []

        if nice: #prep data for nice list selection,
            if additionalOptions is None: additionalOptions = ["Rescan", "Quit"]
            if (not scanDictionary):
                deviceList.append(["No instruments found to display"])
            else:
                for k, v in scanDictionary.items():
                    # these items should all be Keysight AC6804B AC Power Sources
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out the serial number
                    if "Keithley 2460 " in v[:14]:  # currently we don't get here without this being true, but that may not be the case in future
                        name =v[:14]
                        serialNo = v[14:].split(".")[0]
                        deviceList.append([name,serialNo,ip])
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                        deviceList.append([ip + "=" + id + " " + ip])
            adOp = []
            for option in additionalOptions:
                adOp.append([option]*3)
            userStr = listSelection(title=title, message=message, selectionList=deviceList, tableHeaders=["Name","Serial","IP Address"], nice=nice, indexReq=True, additionalOptions=adOp)[3] #Address will allways be 3 in this format


        else: #Prep data for test center
            if (not scanDictionary):
                deviceList.append("1=No instruments found to display")
            else:

                x = 1
                for k, v in scanDictionary.items():
                    # these items should all be Keithley 2460 SMUs
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out Keithley serial number
                    if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                        id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                    deviceList.append(ip + "=" + id + "\t" + ip)
                    x += 1
            if additionalOptions is None:
                additionalOptions = "Rescan=Rescan,Quit=Quit"
            deviceList = ",".join(deviceList)
            userStr = listSelection(title=title,message=message,selectionList=deviceList, additionalOptions=additionalOptions)


            
        # Process the user response
        if (userStr == 'q' or userStr.lower() in "quit"):
            return "quit"
        elif (userStr == 'r' or userStr.lower() in "rescan"):
            scanDictionary = None
            additionalOptions = originalOptions
        else:
            # Return the address string of the selected instrument
            return userStr

'''
Class for control of Keithley source measure units for calibration purposes
'''
class KeithleyDMM6500:

    ACCurrentRanges = {"1mA":1E-3,"10mA":10E-3,"100mA":100E-3,"1A":1,"3A":3,"10A":10}
    CurrentRange = ""
    ACVoltageRanges = {"100mV":100E-3,"1V":1,"10V":10,"750V":750}
    VoltageRange = ""

    # Discover DMM6500 devices through mDNS
    # returns a list of [ALIAS,IP] lists from mDNS, where the name includes "DMM6500" and the service type is scpi-raw
    # This function makes a lot of assumptions about the data and certainly could be a lot more robust
    @staticmethod
    def discover():

        logging.debug(os.path.basename(__file__) + ": Searching for DMM6500 Multimeters: ")

        # Look for matching mDNS devices
        responses = locateMdnsInstr("DMM6500",serviceType="_scpi-raw._tcp.local.")

        logging.debug(os.path.basename(__file__) + ": Received the following responses: " + str(responses))

        #create a list of names and ip addresses to match the standard return type for this function
        devices = []
        for response in responses:
            try:
                devices.append([responses[response],response])
            except:
                raise ValueError()

        return devices


    '''
    Init the class
    '''
    def __init__(self, addr):
        self.TIMEOUT = 10
        self.BUFFER_SIZE = 4096
        self.connection = None
        self.addr = addr
        #self.numeric = re.compile("(\+|-)([0-9\.]+)")
        self.measurementType = "RMS"
        self.measurementTypeList = ["PEAK", "RMS"]
        self.maxCurrentLimit = 8.0
        self.isOpen = False
        self.commandDelay = 0.05 # It errors on back to back comms, delay needed.
        self.lastResult = None
        self.CurrentRange = ""
        self.conString = None
        
    def openConnection (self, connectionString = None):
        logging.debug(os.path.basename(__file__) + ": Opening connection to: " + str(self.addr))
        if (connectionString is not None):
            self.conString = connectionString
        else:
            self.conString = self.addr
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        self.connection.connect((self.conString,5025))
        self.isOpen = True

        # Reset the device on connection
        self.connection.send("*LANG SCPI\r\n".encode('latin-1'))
        self.connection.send("*RST\r\n".encode('latin-1'))
        
    '''
    Close the connection to the instrument
    '''
    def closeConnection (self):
        logging.debug(os.path.basename(__file__) + ": closing connection to DMM6500 ")
        self.connection.close()

    '''
    Attempts to force close any existing (LAN) socket connections
    '''
    def closeDeadConnections (self):
        deadSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        deadSocket.settimeout(self.TIMEOUT)
        deadSocket.connect((self.conString,5030))
        deadSocket.close()

    '''
    getError returns the instruments error for a specified reading
    '''
    def getCurrentError(self,reading):
        if self.CurrentRange in KeithleyDMM6500.ACCurrentRanges.keys():
            if reading == 0:
                sign = 1
            else:
                sign = reading/abs(reading)
            return (reading*0.004)+KeithleyDMM6500.ACCurrentRanges[self.CurrentRange]*0.0006*sign
        else:
            raise ValueError("Can't return error as no range has been set")
        
    '''
    Send a command to the instrument and return the response from the query
    This should only be used for commands which expect a response

    timeoutAllowed = False : set this to True if a timeout is a valid response, function will return None
    '''
    def sendCommandQuery (self, commandString, timeoutAllowed = False):
        if not self.isOpen:
            self.openConnection()
        retries = 1
        while retries < 5:
            try:
                # Send the command
                startTime= int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Read back the response data
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                endTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": received: " + resultStr)
                logging.debug(os.path.basename(__file__) + ": Time Taken : " + str(endTime-startTime) + " mS")
                resultStr = resultStr.strip ('\r\n\t')
                # If no response came back
                if (resultStr is None or resultStr == ""):
                    logging.error("resultStr = "+ resultStr)
                    # Check for errors
                    if (self.getStatusEavFlag () == True):
                        for i in range(self.getErrorCount()):
                            errorStr = self.getNextError ()
                            logging.error(os.path.basename(__file__) + ": DMM6500 Reported Errors: " + errorStr)
                            raise ValueError ("The DMM6500 reported Errors")
                    else:
                        raise ValueError ("The DMM6500 did not return a response")
                return resultStr
            except socket.timeout:
                if timeoutAllowed == False:
                    logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString + ", closing connection and retrying")
                    # reset connections on DMM6500
                    self.closeDeadConnections()
                    # reopen connection to DMM6500
                    self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.connection.settimeout(self.TIMEOUT)
                    self.connection.connect((self.conString,5025))
                    # increment retry counter
                    retries = retries + 1
                else:
                    logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString + ", returning None as timeoutAllowed is set to True")
                    return None
        raise TimeoutError (os.path.basename(__file__) + ": timed out while expecting a response")
        
    
    '''
    Sends a command to the instrument where a response is not expected.
    Status byte check is used to verify that the command does not flag an error
    If an error is found, it will be flushed and the first error text returned
    'OK' is returned on success
    '''    
    def sendCommand (self, commandString, expectedResponse = True):
        if not self.isOpen:
            self.openConnection()
        retries = 1
        while retries < 5:
            try:
                # Send the command
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Check for errors
                if (self.getStatusEavFlag () == True):
                    for i in range(self.getErrorCount()):
                        errorStr = self.getNextError ()
                        logging.error(os.path.basename(__file__) + ": DMM6500 Reported Errors: " + errorStr)
                    raise ValueError ("The DMM6500 reported Errors: " + errorStr)
                else:
                    return "OK"
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on DMM6500
                self.closeDeadConnections()
                # reopen connection to DMM6500
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while sending command to AC6804B")
    
    '''
    Reset the instrument
    '''
    def reset (self):
        result = self.sendCommand("*RST")
        return result

    '''
    Measures AC Current Once
    '''
    def measureACCurrent (self,range="AUTO",readings=1):

        # set the range, if required
        if range != self.CurrentRange:
            if range in self.ACCurrentRanges.keys():
                self.sendCommand("SENS:CURR:AC:RANG " + str(self.ACCurrentRanges[range]))
            else:
                self.sendCommand("SENS:CURR:AC:RANG:AUTO ON")

        #Make a buffer of at least the specified size

        self.sendCommand("TRAC:CLEAR")
        self.sendCommand("SENS:COUNT " + str(readings))
        self.sendCommand("STAT:OPER:MAP 0, 4917, 4918")
        self.sendCommandQuery("MEAS:CURR:AC?",timeoutAllowed=True)

        while (self.sendCommandQuery("STAT:OPER?",timeoutAllowed=True) != "0"):
            time.sleep(0.1)
        count = self.sendCommandQuery("TRAC:ACT?")
        result = float(self.sendCommandQuery("TRACE:STAT:AVER?"))
        return result
        
    '''
    Measures AC Voltage
    '''
    def measureACVoltage (self,range="AUTO,",readings=1):  
        
        # set the range, if required
        if range != self.CurrentRange:
            if range in self.ACVoltageRanges.keys():
                self.sendCommand("SENS:VOLT:AC:RANG " + str(self.ACCurrentRanges[range]))
            else:
                self.sendCommand("SENS:VOLT:AC:RANG:AUTO ON")

        #Make a buffer of at least the specified size

        self.sendCommand("TRAC:CLEAR")
        self.sendCommand("SENS:COUNT " + str(readings))
        self.sendCommand("STAT:OPER:MAP 0, 4917, 4918")
        self.sendCommandQuery("MEAS:VOLT:AC?",timeoutAllowed=True)

        while (self.sendCommandQuery("STAT:OPER?",timeoutAllowed=True) != "0"):
            time.sleep(0.1)
        count = self.sendCommandQuery("TRAC:ACT?")
        result = float(self.sendCommandQuery("TRACE:STAT:AVER?"))
        return result
       
    '''
    Reset Trace
    '''
    def resetTrace (self):    
        self.sendCommandQuery("TRAC:CLE")
        self.sendCommandQuery("TRAC:CLE")
        return

    '''
    Returns Trace Minimum Value
    '''
    def returnTraceMAX (self):    
        result = float(self.sendCommandQuery("TRAC:STAT:MIN?"))
        return result

    '''
    Returns Trace Maximum Value
    '''
    def returnTraceMAX (self):    
        result = float(self.sendCommandQuery("TRAC:STAT:MAX?"))
        return result

    '''
    Returns the status byte from the instrument (the result of the *STB? command)
    This is used to tell if the module is ready or has errored
    '''
    def getStatusByte (self, retries=4):
        tryCount = 0
        while tryCount <= retries:
            tryCount +=1
            # Read status byte
            resultStr = self.sendCommandQuery ("*STB?")
            # If we get junk, try again
            try:
                statInt = int(resultStr)
                return statInt
            except:
                logging.debug("AC6804B is not responding with valid data retry " + str(tryCount))

        #If we have reached here we have excepet on every try and should raise a value error
        logging.error("AC6804B is not responding with valid data : " + str(resultStr))
        raise ValueError ("AC6804B is not responding with valid data")

    def printInstrumentStatus (self):
        stat = self.getStatusByte ()
        if (stat&1 != 0):
            print ("Reserved[0] Flag Set")
        if (stat&2 != 0):
            print ("Reserved[1] Flag Set")
        if (stat&4 != 0):
            print ("Error Available Flag Set")
        if (stat&8 != 0):
            print ("Questionable Event Flag Set")
        if (stat&16 != 0):
            print ("Message Available Flag Set")
        if (stat&32 != 0):
            print ("Event Status Flag Set")
        if (stat&64 != 0):
            print ("Request Service Flag Set")
        if (stat&128 != 0):
            print ("Operation Status Flag Set")
        if (stat == 0):
            print ("Status flags are clear")
        
    '''
    Returns the Measurement Summary Bit of the status information
    '''
    def getStatusMsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&1 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Question Summary Bit of the status information
    '''
    def getStatusQsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&8 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Error Available Bit of the status information
    '''
    def getStatusEavFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&4 != 0):
            return True
        else:
            return False;
    
    '''
    Gets the error count from the instrument
    '''
    def getErrorCount (self):   
        errorCount = int(self.sendCommandQuery ("SYSTem:ERRor:COUNT?"))
        return errorCount
    
    '''
    Gets the next error from the instrument
    '''
    def getNextError (self):   
        errorStr = self.sendCommandQuery ("SYSTem:ERRor:NEXT?")
        return errorStr
    
    '''
    Puts the device into a safe state
    Move to generic class?
    '''
    def disable (self):
        # Nothing to do here
        pass