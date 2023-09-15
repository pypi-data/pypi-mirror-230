import socket
from quarchCalibration.deviceHelpers import locateMdnsInstr
from quarchpy.user_interface import *

'''
Prints out a list of calibration instruments nicely onto the terminal, numbering each unit
'''
def listCalInstruments(scanDictionary):
    if (not scanDictionary):
        print ("No instruments found to display")
    else:
        x = 1
        for k, v in scanDictionary.items():
            # these items should all be Keysight AC6804B AC Power Sources
            # form of the value is '._scpi-raw._tcp.local.'
            # we want to extract name, serial number and ip address
            ip = k
            # if we recognise the device, pull out the serial number
            if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
            else:
                id = v  # else we don't recognise the device, return the whole identifier unmodified
            print (str(x) + " - " + id + "\t" + ip)
            x += 1

'''
Allows the user to select a test instrument
'''
def userSelectCalInstrument(scanDictionary=None, scanFilterStr="AC6804B", title=None, message=None, tableHeaders= None, additionalOptions = None, nice=False):
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
class KeysightAC6804B:

    '''
    getError returns the instruments error for a specified reading
    '''
    @staticmethod
    def getCurrentError(reading):
        return (reading*0.005)+0.04

    # Discover AC6804B devices through mDNS
    # returns a list of [ALIAS,IP] lists from mDNS, where the name includes "AC6804B" and the service type is scpi-raw
    # This function makes a lot of assumptions about the data and certainly could be a lot more robust
    @staticmethod
    def discover():

        logging.debug(os.path.basename(__file__) + ": Searching for AC9804B AC Power Sources: ")

        # Look for matching mDNS devices
        responses = locateMdnsInstr("AC6804B",serviceType="_scpi-raw._tcp.local.",scanTime=3)   # longer scan time seems to be required

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
        self.conString = None
        
    def openConnection (self, connectionString = None):
        logging.debug(os.path.basename(__file__) + ": Opening connection to: " + str(connectionString))
        if (connectionString is not None):
            self.conString = connectionString
        else:
            self.conString = self.addr
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        self.connection.connect((self.conString,5025))
        self.isOpen = True

        # Reset the device on connection
        self.connection.send("*RST\r\n".encode('latin-1'))
        
    '''
    Close the connection to the instrument
    '''
    def closeConnection (self):
        logging.debug(os.path.basename(__file__) + ": closing connection to AC6804B ")
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
    Send a command to the instrument and return the response from the query
    This should only be used for commands which expect a response
    '''
    def sendCommandQuery (self, commandString):
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
                            logging.error(os.path.basename(__file__) + ": AC9804B Reported Errors: " + errorStr)
                            raise ValueError ("The AC6804B reported Errors")
                    else:
                        raise ValueError ("The AC6804B did not return a response")
                return resultStr
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": AC6804B command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on AC6804B
                self.closeDeadConnections()
                # reopen connection to AC6804B
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
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
                        logging.error(os.path.basename(__file__) + ": AC9804B Reported Errors: " + errorStr)
                    raise ValueError ("The AC6804B reported Errors")
                else:
                    return "OK"
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": AC6804B command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on AC6804B
                self.closeDeadConnections()
                # reopen connection to AC6804B
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
    Enable/disable the outputs
    '''
    def setOutputEnable (self, enableState):
        if (enableState == True):
            result = self.sendCommand("OUTP ON")
        else:
            result = self.sendCommand("OUTP OFF")
            
        return result
        
    '''
    Return the output enable state as a boolean
    '''
    def getOutputEnable (self):
        result = self.sendCommandQuery ("OUTP?")
        if (int(result) == 1):
            return True
        else:
            return False
        
    '''
    Set the output voltage limit, in volts
    '''
    def setSupplyVoltageLimit (self, voltRMSValue):
        return self.sendCommand("VOLT:LIM:LOW " + str(voltRMSValue))
        return self.sendCommand("VOLT:LIM:UPP " + str(voltRMSValue))
        
    '''
    Return the output voltage limit as a float
    '''
    def getSupplyVoltageLimit (self):
        # assuming upper and lower limits are the same
        result = self.sendCommandQuery ("VOLT:LIM:UPP?")
        return float(result)
        
    '''
    Set the output current limit, in amps
    '''
    def setSupplyCurrentLimit (self, ampRMSValue):
        self.sendCommand("CURR " + str(ampRMSValue))
        self.sendCommand("CURR:PROT:STATE ON ")
        return True
        
    '''
    Return the output current limit as a float
    '''
    def getSupplyCurrentLimit (self):
        result = self.sendCommandQuery ("CURR?")
        return float(result)
        
    '''
    Sets the number of measurements to be averaged together to return one measurement
    '''
    def setAverageCount (self, measCount=1):
        return self.sendCommand("SENS:AVER " + str(measCount))

    '''
    Sets the AC Supply output voltage in Volts
    '''
    def setACSupplyVoltage (self, voltValue):
        return self.sendCommand("SOUR:VOLT " + str(voltValue))
        
    '''
    Gets the AC Supply output voltage in volts
    '''
    def getACSupplyVoltage (self):
        result = float((self.sendCommandQuery("SOUR:VOLT?")))
        return result
        
    '''
    Sets the AC Supply Range "155|310|AUTO"
    '''
    def setACSupplyRange (self, rangeString):
        if rangeString == "AUTO":
            self.sendCommand("SOUR:VOLT:RANGE:AUTO ON")
        elif (rangeString == "155" or rangeString =="310"):
            self.sendCommand("SOUR:VOLT:RANGE:AUTO OFF")
            self.sendCommand("SOUR:VOLT:RANGE" + rangeString)
        else:
            raise valueException("invalid parameter supplied to setACSupplyRange")
        
    '''
    Sets the AC Supply frequency in Hz
    '''
    def setACSupplyFrequency (self, hertzValue):
        return self.sendCommand("SOUR:FREQ " + str(hertzValue))
        
    '''
    Gets the AC Supply frequency in Hz
    '''
    def getACSupplyFrequency (self):
        result = float((self.sendCommandQuery("SOUR:FREQ?")))
        return result
        
    '''
    Measures the current load voltage value
    '''
    def measureSupplyVoltage (self,count=4):    
        self.setAverageCount(count)
        result = float(self.sendCommandQuery("MEAS:VOLT:AC?"))
        return result
        
    '''
    Measures the current load voltage value
    '''
    def measureSupplyCurrent (self,count=4):    
        self.setAverageCount(count)
        result = float(self.sendCommandQuery("MEAS:CURR:AC?"))
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
    Puts the into a safe state
    Move to generic class?
    '''
    def disable (self):
            self.setOutputEnable(False)