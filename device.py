import time
import logging
import re
import os

logger = logging.getLogger(__name__)

class Device(object):

  def __init__(self, privateKeyLocation=None,
                     publicKeyLocation=None,
                     serverPublicKeyLocation=None):

    if privateKeyLocation is not None and publicKeyLocation is not None and serverPublicKeyLocation is not None:
      fPriv = open(privateKeyLocation, 'r')
      fPub = open(publicKeyLocation, 'r')
      sPub = open(serverPublicKeyLocation, 'r')

      self.privateKey = fPriv.read()
      self.publicKey = fPub.read()
      self.serverPublicKey = sPub.read()

      fPriv.close()
      fPub.close()
      sPub.close()

    else:
      logger.warn("No key files provided, we can't encrypt anything!")
      self.privateKey = None
      self.publicKey = None
      self.serverPublicKey = None

  ''' Here we get the ID of this device, this should obviously be overwritten
      in your specific implementation
  '''
  def getID(self):
    return 0

  def privateKeyEncrypt(self, message):
    #TODO: actually encrypt the message
    return message

  ''' Here we get the message (stats) and encrypt it using our private key.
      We then add our device_id in plaintext and the timestamp. 

      NOTE: we're trying to verify the message authenticity and *not* make
            the message hard to decode. Hence the private key.

      Once it receives the message the server will decrypt the message using 
      our public key (verifying our authenticity) and log this message

      @param message: message to be encrypted with our private key
      @return: encrypted message and metadata
  '''
  def encodeAsDevice(self, message):
    encrypted_message = self.privateKeyEncrypt(message)
    return {'device_id': self.getID(),
            'timestamp': time.time(),
            'message': encrypted_message}

  ''' Here we get a message that we assume has been encrypted with our public key
      to prevent other entities to decode the message and decode it with our private key.

      NOTE: Here we are trying to ensure only we can see the message and *not* that the
            origin is a trusted source

      @param message: encrypted message
      @return: decrypted message
  '''
  def decodeAsDevice(self, message):
    #TODO: actually decrypt the message
    return message

  ''' Here we get a message that we assume is enctypted with the trusted server's private key
      to verify the authenticity of the message and we decode it with our private key
 
      NOTE: Here we are trying to ensure the authenticity of the sender and *not* that other
            persons cannot read our message

      @param message: encrypted message
      @return: decrypted message
  '''
  def decodeFromServer(self, message):
    #TODO: actually decrypt the message
    return message

  ''' This function assumes that the message has been ecrypted once with our public key
      to ensure only we can see it and then with the server's private key to ensure
      origin authenticity.

      NOTE: Here we are trying to verify the message originated from our trusted server
            *and* we're trying to make it impossible for entities other than us to
            decode the message
      
      @param message: encrypted message
      @return: decrypted message
  '''
  def decodeAsDeviceFromServer(self, message):
    half_decrypted = self.decodeFromServer(message) #decoded by server public key
    if half_decrypted is None: return None

    return self.decodeAsDevice(half_decrypted) #decoded as our private key

class RaspberryPi(Device):
  ''' A subclass specific to Raspberry Pis '''

  def __init__(self, privateKeyLocation=None, publicKeyLocation=None, serverPublicKeyLocation=None):
    super().__init__(privateKeyLocation=None, publicKeyLocation=None, serverPublicKeyLocation=None)

  def getID(self):
    """Retreives and returns the CPU Serial ID of the Raspberry Pi that it runs on.
    """
    try:
        f = open('/host-proc/cpuinfo','r')
        for line in f:
            if line[0:6]=='Serial':
                return line[10:26]
        f.close()
    except:
        return 0

  def getWLANMetrics(self):
    # TODO: somehow get the information from the host
    """Executes 'iwconfig' and parses results for WLAN diagnostics use."""
    command_output = ""
    # Returns the name of the wireless interface
    interface_name = re.search(r'^\S*', command_output).group(0)

    # Returns the ESSID of the current network
    essid = re.search(r'ESSID: ?"(\w*)"', command_output).group(1)

    # Returns the cell address of the Access Point that the device is connected to.
    ap_address = re.search(r'Access Point: ?([A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2}:[A-Fa-f0-9]{2})', command_output).group(1)
    
    # Returns the operating mode of the connection
    operating_mode = re.search(r'Mode: ?(\w*)', command_output).group(1)

    # Returns the frequency of the connection, 1st capture group being the number, and the second being the unit
    frequency = re.search(r'Frequency: ?([0-9]+\.?[0-9]*) ([KMGHz]*)', command_output).group(1)
    
    # Returns the bit rate of the connection
    bit_rate = re.search(r'Bit Rate= ?([0-9]+\.?[0-9]*) ([KMGBb]*/s)', command_output).group(1)

    # Returns the transmission power of the radio
    tx_power = re.search(r'Tx-Power= ?([-]?[0-9]+\.?[0-9]*) dBm', command_output).group(1)

    retry_short_limit = re.search(r'Retry short limit: ?([0-9]+)', command_output).group(1)

    rts_thr = re.search(r'RTS thr: ?(on|off)', command_output).group(1)

    fragment_thr = re.search(r'Fragment thr: ?(on|off)', command_output).group(1)

    power_management = re.search(r'Power Management: ?(on|off)', command_output).group(1)
    # Link quality
    link_quality = re.search(r'Link Quality= ?(\d{1,3})/(\d{1,3})', command_output).group(1)
    # Link quality, out of (it's always out of 70 but whatever)
    link_quality_max = re.search(r'Link Quality= ?(\d{1,3})/(\d{1,3})', command_output).group(2)

    sig_lvl = re.search(r'Signal level= ?([-]?[0-9]+\.?[0-9]*) dBm', command_output).group(1)

    invalid_nwid = re.search(r'Rx invalid nwid: ?([0-9]+\.?[0-9]*)', command_output).group(1)

    invalid_crypt = re.search(r'Rx invalid crypt: ?([0-9]+\.?[0-9]*)', command_output).group(1)

    invalid_frag = re.search(r'Rx invalid frag: ?([0-9]+\.?[0-9]*)', command_output).group(1)

    tx_excessive_retries = re.search(r'Tx excessive retries: ?([0-9]+\.?[0-9]*)', command_output).group(1)

    invalid_misc = re.search(r'Invalid misc: ?([0-9]+\.?[0-9]*)', command_output).group(1)

    missed_beacon = re.search(r'Missed beacon: ?([0-9]+\.?[0-9]*)', command_output).group(1)

  def getCPUTemperature(self):
    """Executes '/opt/vc/bin/vcgencmd measure_temp' to retrieve the CPU temp"""
    temp = os.popen("/host-vc/bin/vcgencmd measure_temp").readline()
    return re.search(r"temp=([\d\.]+)'C", temp).group(1)
