import logging
import os
import time
import pyvisa


def get_class_for_card(name, slot):
    if name == "34925A-1W":
        return KeySight34925A_1W(slot)
    elif name == "34951A":
        return Keysight34951A(slot)
    elif name == "34938A":
        return Keysight34938A(slot)
    return None


class KeySight34980A:
    """
    ``Base class for the Keysight 34980A DAQ``
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        # Supported Devices
        self.cards = None
        self.card_types = None
        self.connection_string = connection_string
        self.supported_list = ["34925A-1W", "34951A"]
        self.resource_manager = None
        self.daq = None
        # Cards Can be discovers with : SYSTem:CTYPe? <slot>
        # Should return AGILENT TECHNOLOGIES,<Modellnummer>,<Seriennummer>,<Firmware-Version>

    def open_connection(self):
        """
        ``Opens a TCP/IP connection to the Keysight DAQ 34980A``
        """
        self.resource_manager = pyvisa.ResourceManager()
        # self.connection_string = os.getenv("DAQ_CONNECTION_STRING", default='TCPIP0::192.168.123.10::INSTR')
        try:
            logging.info(f": Opening DAQ Resource at {self.connection_string}")
            self.daq = self.resource_manager.open_resource(self.connection_string)
            self.daq.read_termination = '\n'
            self.daq.write_termination = '\n'
        except Exception as e:
            raise Exception(f": ERROR {e}: Could not open Resource\n")
        self.cards = {}
        self.card_types = {}
        for slot in range(8):
            resp = self.daq.query(f'SYSTem:CTYPe? {slot + 1}')
            logging.info(f"Found Module {resp}")
            module_type = resp.split(',')[1]
            self.card_types[slot + 1] = module_type
        logging.info(self.card_types)
        for slot, module_type in self.card_types.items():
            if module_type in self.supported_list:
                self.cards[slot] = get_class_for_card(module_type, slot)

    def close_connection(self):
        """
        ``Closes the TCP/IP connection to the Keysight DAQ 34980A``
        """
        self.resource_manager.close()

    def raw_write(self, cmd):
        return self.daq.write(cmd)

    def raw_query(self, cmd):
        return self.daq.query(cmd)

    def read_channel(self, channel):
        if channel == "0000":
            # print(f"Error measuring net: {net_name} not found, skipping measurement")
            return 0
        else:
            try:
                self.daq.write("CONF:VOLT:DC 10,0.003, (@" + channel + ")")
                self.daq.write("ROUT:SCAN (@" + channel + ")")
                self.daq.write("INIT")
                measured_val = self.daq.query("FETC?")
                return float(measured_val)
            except Exception as e:
                raise Exception(f"ERROR Could not read channel {channel}: {e}")

    def factory_reset(self):
        """
        ``This function helps factory reset the DAQ``
        """
        # System reset
        self.daq.write(f'*RST')

    def id_number(self):
        """
        ``This function returns the ID number of the equipment``
        """
        self.daq.write('*IDN?')
        idn = self.daq.read()
        logging.info(f': *IDN? returned: {idn}')
        return str(idn)

    def system_info(self):
        """
        ``This function establishes a connection with the unit under test and gets general information
        from the KeysightDAQ and modules about Manufacturer, ModelNumber,SerialNumber, FirmwareVersion, etc.
        It also gets network information like: IP Address, LAN connectivity, DHCP settings, etc.`` \n
        :returns: `str` : System information
        """
        sys_info = {}
        logging.info("######## SYSINFO ########")
        logging.info(': IP: %s\n' %
                     (self.daq.get_visa_attribute(pyvisa.constants.VI_ATTR_TCPIP_ADDR)))
        sys_info["IP_Address"] = self.daq.get_visa_attribute(pyvisa.constants.VI_ATTR_TCPIP_ADDR)

        safety_interlock = self.daq.query(f'SYSTem:ABUS:INTerlock:SIMulate?')
        logging.info(f": Safety Interlock (0: OFF | 1: ON) {safety_interlock}")
        sys_info['Safety_interlock'] = safety_interlock

        mac_address = self.daq.query(f'SYST:COMM:LAN:MAC?')
        logging.info(f": MAC Address: {mac_address}")
        sys_info["MAC_Address"] = mac_address

        gateway = self.daq.query(f'SYST:COMM:LAN:GATEWAY?')
        logging.info(f": Gateway: {gateway}")
        sys_info['Gateway'] = gateway

        host_name = self.daq.query(f'SYST:COMM:LAN:HOST?')
        logging.info(f": Host Name: {host_name}")
        sys_info['Hostname'] = host_name

        dns_address = self.daq.query(f'SYST:COMM:LAN:DNS?')
        logging.info(f": DNS Address: {dns_address}")
        sys_info['DNS_Address'] = dns_address

        domain_name = self.daq.query(f'SYST:COMM:LAN:DOM?')
        logging.info(f": Domain Name: {domain_name}")
        sys_info['Domain_Name'] = domain_name

        dhcp_setting = self.daq.query(f'SYSTem:COMM:LAN:DHCP?')
        logging.info(f": DHCP Setting: {dhcp_setting}")
        sys_info['DHCP_Setting'] = dhcp_setting

        lan_boot_status = self.daq.query(f'SYSTem:COMM:LAN:BST?')
        logging.info(f": LAN boot status: {lan_boot_status}")
        sys_info['LAN_boot_status'] = lan_boot_status

        logging.info("######## SYSINFO ########")
        return sys_info

    def system_status(self):
        """
        ``This function will run module specific tests one slot at a time`` \n
        :returns: `str` : Status
        """
        sys_status = {}
        logging.info("######## SYSTEM STATUS ########")

        # Returns decimal value for the bit number which bits are enabled in the register
        ese_enabled_bits = self.daq.query(f'*ESE?')
        logging.info(f": ESE: Enabled bits in Register: {ese_enabled_bits}")
        sys_status['ESE'] = ese_enabled_bits

        # Returns decimal value for the bit number which is enabled in the Standard Event Register
        esr_enabled_ser = self.daq.query(f'*ESR?')
        logging.info(f": ESR: Enabled Standard Event Register: {esr_enabled_ser}")
        sys_status['ESR'] = esr_enabled_ser

        logging.info("######## SYSTEM STATUS ########")
        return sys_status

    def self_test(self):
        """
        ``Perform a self-test on the device`` \n
        :returns: `bool` : True or Raise exception
        """
        if not self.daq.query(f'SYST:COMM:LAN:MAC?'):
            raise EnvironmentError(f'ERROR: Keysight DAQ not found!')
        else:
            logging.info(f": Module found : Keysight DAQ 34980A")
        self.daq.write('*TST?')
        time.sleep(17)
        self_test = self.daq.read()
        if self_test == '+0':
            logging.info(": Self-test Passed!")
            return True
        else:
            raise Exception(f'ERROR in Self-test: Contact Customer Service at Keysight DAQ 34980A')

    def _is_dmm_installed(self):
        """
        ``This function checks if the internal DMM for the DAQ is installed in the mainframe`` \n
        :returns: `bool` : Status
        """
        dmm_installed = self.daq.query(f'INST:DMM:INST?')
        if dmm_installed == 1:
            logging.info(f": DMM is installed in mainframe! ")
            return True
        else:
            logging.error(f": DMM module not found")
            return False

    def _is_dmm_enabled(self):
        """
        ``This function checks if the internal DMM for the DAQ is enabled`` \n
        :returns: `bool` : Status
        """
        try:
            dmm_enabled = self.daq.query(f'INST:DMM?')
            if dmm_enabled == 0:
                logging.info(f": DMM is OFF!")
                return False
            elif dmm_enabled == 1:
                logging.info(f": DMM is ON!")
                return True
        except Exception as e:
            raise Exception(f": {e}")

    def enable_dmm(self):
        """
        ``This function checks if the internal dmm is present, and is disabled and Enables it``
        """
        if self._is_dmm_enabled():
            logging.info(f": Internal DMM already enabled")
            # print(f": Internal DMM already enabled")
            pass
        elif not self._is_dmm_enabled():
            self.daq.write(f'INST:DMM ON')
            logging.info(f": Internal DMM now enabled!")
            # print(f": Internal DMM now enabled!")

    def disable_dmm(self):
        """
        ``This function checks if the internal dmm is present, and is enabled and Disables it``
        """
        if self._is_dmm_enabled():
            self.daq.write(f'INST:DMM OFF')
            logging.info(f": Internal DMM now Disabled!")
            # print(f": Internal DMM now Disabled!")
        elif not self._is_dmm_enabled():
            logging.info(f": Internal DMM already Disabled")
            # print(f": Internal DMM already Disabled")
            pass

    def connect_dmm(self):
        """
        ``This function will check the status of the internal DMM and connect it``
        """
        try:
            _is_dmm_conn = self.daq.query(f'INST:DMM:CONN?')
            if _is_dmm_conn == '0':
                self.daq.write(f'INST:DMM:CONN')
                time.sleep(0.5)
                if self.daq.query(f'INST:DMM:CONN?') == '1':
                    logging.info(f": DMM Connected ")
                    return True
                else:
                    logging.error(f"ERROR: Could not connect DMM")
                    return False
            elif _is_dmm_conn == '1':
                logging.info(f"DMM already connected")
                return True
        except Exception as e:
            raise Exception(f": {e}: trouble reaching DMM. Check installation.")

    def disconnect_dmm(self):
        """
        ``This function will check the status of the internal DMM and disconnect it``
        """
        try:
            _is_dmm_disc = self.daq.query(f'INST:DMM:DISC?')
            if _is_dmm_disc == '0':
                self.daq.write(f'INST:DMM:DISC')
                time.sleep(0.5)
                if self.daq.query(f'INST:DMM:DISC?') == '1':
                    logging.info(f": DMM Disconnected ")
                    return True
                else:
                    logging.error(f"ERROR: Could not disconnect DMM")
                    return False
            elif _is_dmm_disc == '1':
                logging.info(f": DMM already Disconnected ")
                return True
        except Exception as e:
            raise Exception(f": {e}: trouble reaching DMM. Check installation.")

    def get_dmm_voltage(self, test_mode):
        """
        ``This function measures the internal dmm voltage for AC and DC`` \n
        :param test_mode: `str` : AC/DC \n
        :returns: `float` : DMM voltage in Volts
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_volt = self.daq.query(f'MEAS:VOLT:{str(test_mode).upper()}?')
                logging.info(f": {str(test_mode).upper()} Voltage measurement for the internal DMM: {dmm_volt} V")
                return float(dmm_volt)
            except Exception as e:
                raise Exception(f": {e} Could not get Voltage measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_current(self, test_mode):
        """
        ``This function measures the internal dmm AC current`` \n
        :param test_mode: `str` : AC/DC \n
        :returns: `float` : DMM Current in Amps
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_curr = self.daq.query(f'MEAS:CURR:{str(test_mode).upper()}?')
                logging.info(f": {str(test_mode).upper()} Current measurement for the internal DMM: {dmm_curr} A")
                return float(dmm_curr)
            except Exception as e:
                raise Exception(f": {e} Could not get Current measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_resistance(self, range, resolution):
        """
        ``This function measures the internal DMM Resistance`` \n
        :param range: `int` : 1000 Ohm range \n
        :param resolution: `int` : 1 Ohm resolution \n
        :returns: `float` : DMM Resistance in Ohms
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_res = self.daq.query(f'MEAS:RES? {int(range)},{int(resolution)}')
                logging.info(f": Resistance measurement for the internal DMM: {dmm_res} Ohms")
                return float(dmm_res)
            except Exception as e:
                raise Exception(f": {e} Could not get Resistance measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_frequency(self):
        """
        ``This function measures the internal DMM Frequency`` \n
        :returns: `float` : DMM Frequency in Hertz
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_frequency = self.daq.query(f'MEAS:FREQ?')
                logging.info(f": Frequency measurement for the internal DMM: {dmm_frequency} Hz")
                return float(dmm_frequency)
            except Exception as e:
                raise Exception(f": {e} Could not get Frequency measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_period(self):
        """
        ``This function measures the internal DMM Period`` \n
        :returns: `float` : DMM Period in ms
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_period = self.daq.query(f'MEAS:PER?')
                logging.info(f": Period measurement for the internal DMM: {dmm_period} ms")
                return float(dmm_period)
            except Exception as e:
                raise Exception(f": {e} Could not get Period measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_trigger_source(self):
        """
        ``This query returns the trigger source currently selected.`` \n
        :returns: `float` : Trigger source - SING | CONT
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                trigger_source = self.daq.query(f'TRIG:SOUR:ALAR?')
                logging.info(f": Checking the trigger source (SING|CONT): {str(trigger_source)}")
                return str(trigger_source)
            except Exception as e:
                raise Exception(f": {e} Could not get Trigger source")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_alarm_condition(self):
        """
        ``This query returns the condition register for the Alarm Register group.`` \n
        :returns: `int` : Binary-weighed sum of bits set in alarm register
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                alarm_condition = self.daq.query(f'STAT:ALAR:COND?')
                logging.info(f": Bits set in Alarm register: {alarm_condition}")
                return alarm_condition
            except Exception as e:
                raise Exception(f": {e} Could not get Alarm Condition")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def read_high_current_shunt_raw(self):
        """
        ``This function reads the high current shunt value for 34925A in BCN FKT`` \n
        :returns: `float` : Voltage value
        """
        # Close Analog Bus 1 and 4 Relais on slot 1
        self.daq.write('ROUT:CLOS (@1911,1914)')
        # Read the DMM Voltage
        val = float(self.daq.query('MEAS:VOLT:DC?'))
        # Open Analog Bus relais
        self.daq.write('ROUT:OPEN (@1911,1914)')
        return val

    def get_1wire_measurements(self, channel_in):
        """
        ``This function configures the instrument to do voltage, resistance, frequency and period measurements by
        internally triggering the instrument to scan channel n on the module in slot m.``
        """
        # TODO check first with sys err
        # TODO break up - Voltage (1 ch and multiple channel) + Freq Res Period

        module_in_use = [k for k, v in self.card_types.items() if v == '34925A-1W']
        slot_in_use = int(KeySight34925A_1W(module_in_use[0]).get_address_by_channel(0))

        meas_dc_volt = self.daq.query(f'MEAS:VOLT:DC? (@{slot_in_use + channel_in})')
        logging.info(f"DC Voltage measurement on channels {slot_in_use + channel_in}: {meas_dc_volt} V")

        meas_res = self.daq.query(
            f'MEAS:RES? 1000,1,(@{slot_in_use + 3}:{slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Resistance measurement for channels {slot_in_use + 3} to {slot_in_use + 8}: {meas_res} Ohm")

        meas_frequency = self.daq.query(
            f'MEAS:FREQ? 100,(@{slot_in_use + 3}, {slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Frequency measurement on channels {slot_in_use + 3} and {slot_in_use + 8}: {meas_frequency} Hz")

        meas_period = self.daq.query(f'MEAS:PER? (@{slot_in_use + 3}, {slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Period measurement on channels {slot_in_use + 3} and {slot_in_use + 8}: {meas_period} ms")

        # system_error = self.daq.query(f'SYST:ERR?')
        # if system_error != '+0,"No error"':
        #     raise Exception(f"System error: {system_error}")

    def dac_set_dc_voltage(self, voltage_in, channel_in):
        """
        ``This function sets the voltage in the DAC module 34951A`` \n
        :param voltage_in: `int` : Input voltage in Volts \n
        :param channel_in: `int` : Channel ranges between 1-20 \n
        :returns: `bool` : True or False for if the channels are closed or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34951A']
        slot_in_use = int(Keysight34951A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        logging.info(f'DAC Module is: {found_module}')

        self.daq.write(
            f'SOURce:VOLTage {voltage_in},(@{slot_in_use + channel_in},{slot_in_use + channel_in + 1},{slot_in_use + channel_in + 2})')
        self.daq.write(
            f'OUTPut:STATe ON,(@{slot_in_use + channel_in},{slot_in_use + channel_in + 1},{slot_in_use + channel_in + 2})')
        time.sleep(2)

    def dac_set_current(self, current, channel_in):
        """
        ``This function sets the current in the DAC module 34951A`` \n
        :param current: `int` : Input current in Amps \n
        :param channel_in: `int` : Channel ranges between 1-20 \n
        :returns: `bool` : True or False for if the channels are closed or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34951A']
        slot_in_use = int(Keysight34951A(module_in_use[0]).get_address_by_channel(0))

        self.daq.write(
            f'SOURce:CURRent {current},(@{slot_in_use + channel_in},{slot_in_use + channel_in + 1},{slot_in_use + channel_in + 2})')
        self.daq.write(
            f'OUTPut:STATe ON,(@{slot_in_use + channel_in},{slot_in_use + channel_in + 1},{slot_in_use + channel_in + 2})')
        time.sleep(2)

    def switch_check_channel_closed(self, channel_in):
        """
        ``This function checks if a channel is closed in the switch module 34938A`` \n
        :param channel_in: `int` : Channel ranges between 1-20 \n
        :returns: `bool` : True or False for if the channels are closed or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")
        if channel_in in range(1, 21):
            result = self.daq.query(f'ROUTe:CLOSe? (@{slot_in_use + channel_in})')
            if result == '1':
                logging.info(f"Channel {slot_in_use + channel_in} is already closed\n")
                return True
            elif result == '0':
                logging.info(f'Channel {slot_in_use + channel_in} is open\n ')
                return False
        else:
            raise Exception(f"Channel not in range\n")

    def switch_check_channel_open(self, channel_in):
        """
        ``This function checks if a channel is open in the switch module 34938A`` \n
        :param channel_in: `int` : Channel ranges between 1-20 \n
        :returns: `bool` : True or False for if the channels are open or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        if channel_in in range(1, 21):
            result = self.daq.query(f'ROUTe:OPEN? (@{slot_in_use + channel_in})')
            if result == '1':
                logging.info(f"Channel {slot_in_use + channel_in} is already open\n")
                return True
            elif result == '0':
                logging.info(f'Channel {slot_in_use + channel_in} is closed\n ')
                return False
        else:
            raise Exception(f"Channel not in range\n")

    def switch_open_channel(self, channel_in):
        """
        ``This function opens 1 channel in the switch module`` \n
        :param channel_in: `int` : Range 1-20; the first channel to be opened in the switch module \n
        :returns: `bool` : True or False for if the channels are open or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        if channel_in in range(1, 21):
            self.daq.write(f'ROUTe:OPEN (@{slot_in_use + channel_in})')
            logging.info(f'Trying to open one channel: {slot_in_use + channel_in}')
            result = self.daq.query(f'ROUTe:OPEN? (@{slot_in_use + channel_in})')
            if result == '1':
                logging.info(f'Channel {slot_in_use + channel_in} is opened\n')
                return True
            elif result == '0':
                logging.info(f'Channel {slot_in_use + channel_in} could not be opened\n')
                return False
            else:
                raise Exception(f"Channel not opened\n")
        else:
            raise Exception(f"Channel not in range\n")

    def switch_open_two_channels(self, channel1, channel2):
        """
        ``This function opens 1 or 2 channels consecutively in the switch module`` \n
        :param channel1: `int` : Range 1-20; the first channel to be opened in the switch module \n
        :param channel2: `int` : Range 1-20; the second channel to be opened in the switch module \n
        :returns: `bool` : True or False for if the channels are both open or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        if channel1 and channel2 in range(1, 21):
            self.daq.write(f'ROUTe:OPEN (@{slot_in_use + channel1}, {slot_in_use + channel2})')
            logging.info(f'Trying to open channels: {slot_in_use + channel1}, {slot_in_use + channel2}')
            result1 = self.daq.query(f'ROUTe:OPEN? (@{slot_in_use + channel1})')
            result2 = self.daq.query(f'ROUTe:OPEN? (@{slot_in_use + channel2})')
            if result1 == '1' and result2 == '1':
                logging.info(f'Channels {slot_in_use + channel1}, {slot_in_use + channel2} are open\n')
                return True
            elif result1 == '0' and result2 == '0':
                logging.info(f'Channels {slot_in_use + channel1}, {slot_in_use + channel2} are closed\n')
                return False
            elif result1 == '1' and result2 == '0':
                logging.info(f'Channel {slot_in_use + channel1} is open; Channel {slot_in_use + channel2} is closed\n')
                return False
            elif result1 == '0' and result2 == '1':
                logging.info(f'Channel {slot_in_use + channel1} is closed; Channel {slot_in_use + channel2} is open\n')
                return False
            else:
                raise Exception(f"Both Channels not Opened\n")
        else:
            raise Exception(f"Channel not in range\n")

    def switch_close_channel(self, channel_in):
        """
        ``This function closes 1 channel in the switch module`` \n
        :param channel_in: `int` : Range 1-20; the first channel to be opened in the switch module \n
        :returns: `bool` : True or False for if the channels are open or not
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        if channel_in in range(1, 21):
            self.daq.write(f'ROUTe:CLOSe (@{slot_in_use + channel_in})')
            logging.info(f'Trying to close channel: {slot_in_use + channel_in}')
            result = self.daq.query(f'ROUTe:CLOSe? (@{slot_in_use + channel_in})')
            if result == '1':
                logging.info(f'Channel {slot_in_use + channel_in} is closed\n')
                return True
            elif result == '0':
                logging.info(f'Channel {slot_in_use + channel_in} could not be closed\n')
                return False
            else:
                raise Exception(f"Channel not closed\n")
        else:
            raise Exception(f"Channel not in range\n")

    def switch_read_power_failure_state(self):
        """
        ``This function checks the state of relays during power failure in switch module 34938A`` \n
        :returns: `str` : MAIN or OPEN for if the relays maintain present state or are open
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")
        result = self.daq.query(f'SYSTem:MODule:PFAil:JUMPer:AMP5? {module_in_use[0]}')
        if result == 'MAIN':
            logging.info(f"Relays maintain their present state\n")
            return result
        elif result == 'OPEN':
            logging.info(f'Relays open when power fails\n ')
            return result
        else:
            raise Exception(f"Cannot read state\n")

    def switch_read_cycle_count(self, channel_in):
        """
        ``This function returns the relay cycle count in switch module 34938A`` \n
        :param channel_in: `int` : Range 1-20; the first channel to be opened in the switch module \n
        :returns: `int` :cycle_count : Cycle count of a relay on a channel
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        if channel_in in range(1, 21):
            cycle_count = self.daq.query(f'DIAGnostic:RELay:CYCLes? (@{slot_in_use + channel_in})')
            if cycle_count:
                logging.info(f"Relay Cycle count on channel {channel_in} is: {cycle_count} \n")
                return cycle_count
            else:
                raise Exception(f"Cannot read state\n")
        else:
            raise Exception(f"Channel not in range\n")

    def switch_reset_cycle_count(self, channel_in):
        """
        ``This function resets the relay cycle count in switch module 34938A or all switch modules`` \n
        :param channel_in: `int` : Range 1-20; the first channel to be opened in the switch module \n
        :returns: `bool` : True or False for if the cycle count for a channel is reset
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module\n")

        if channel_in in range(1, 21):
            secure_state = self.daq.query(f'CAL:SEC:STAT?')
            if secure_state == '0':
                pass
            elif secure_state == '1':
                self.daq.write(f'CAL:SEC:STAT OFF,AT34980')
                secure_state = self.daq.query(f'CAL:SEC:STAT?')
                if secure_state == '1':
                    raise Exception(f"Could NOT turn OFF secure state \n")
                elif secure_state == '0':
                    pass
                else:
                    raise Exception(f"Unknown Secure State ")
            logging.info(f"Secure State is :OFF")
            self.daq.write(f'DIAGnostic:RELay:CYCLes:CLEar (@{slot_in_use + channel_in})')
            count = self.daq.query(f'DIAGnostic:RELay:CYCLes? (@{slot_in_use + channel_in})')
            if count == '0':
                logging.info(f"Relay cycle count Reset on channel {channel_in}\n")
                return True
            else:
                return False
        else:
            raise Exception(f"Channel not in range\n")

    def switch_power_on_state_reset(self):
        """
        ``This function resets a switch module 34938A to its power-on state.``
        """
        module_in_use = [k for k, v in self.card_types.items() if v == '34938A']
        slot_in_use = int(Keysight34938A(module_in_use[0]).get_address_by_channel(0))
        found_module = self.daq.query(f'SYSTem:CTYPe? {module_in_use[0]}')
        if '34938A' in found_module:
            logging.info(f'Switch Module is: {found_module}')
        else:
            raise Exception("Could not find Module")

        self.daq.write(f'SYSTem:CPON {module_in_use[0]}')
        logging.info(f"Reset to power-on-state\n")


class KeySight34925A_1W:
    def __init__(self, slot):
        # Pin Channel Map. Key is Channel, Value is PIN
        self.channel_pin_map = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 9,
            8: 10,
            9: 13,
            10: 14,
            11: 35,
            12: 36,
            13: 21,
            14: 22,
            15: 41,
            16: 42,
            17: 27,
            18: 28,
            19: 45,
            20: 46,
            21: 19,
            22: 20,
            23: 39,
            24: 40,
            25: 25,
            26: 26,
            27: 11,
            28: 12,
            29: 31,
            30: 32,
            31: 37,
            32: 38,
            33: 23,
            34: 24,
            35: 43,
            36: 44,
            37: 29,
            38: 30,
            39: 15,
            40: 16,
            "COM": 8
        }
        # Set-up the inverse map Key is Pin, Value is Channel
        self.pin_channel_map = {}
        for channel, pin in self.channel_pin_map.items():
            self.pin_channel_map[pin] = channel

        self.slot = slot

    def get_address_by_pin(self, pin):
        addr = "0000"
        try:
            addr = str(self.slot) + str(self.pin_channel_map[pin]).zfill(3)
        except Exception as e:
            raise Exception(f"Error {e} in Getting Channel address for pin {pin} on slot {self.slot}")
        return addr

    def get_address_by_channel(self, channel):
        return str(self.slot) + str(channel).zfill(3)


class Keysight34951A(KeySight34980A):
    def __init__(self, slot):
        self.slot = slot

    def get_address_by_channel(self, channel):
        return str(self.slot) + str(channel).zfill(3)


class Keysight34938A(KeySight34980A):
    def __init__(self, slot):
        self.slot = slot

    def get_address_by_channel(self, channel):
        return str(self.slot) + str(channel).zfill(3)
