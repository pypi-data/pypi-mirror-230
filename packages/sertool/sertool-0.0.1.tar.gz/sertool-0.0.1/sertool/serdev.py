import serial
import serial.tools.list_ports

class SerialList:
    
    def __init__(self):
        self.port_list = serial.tools.list_ports.comports()


    def is_port_available(self, port):
        """
        Returns True if the specified port is available (i.e. not already open)
        """
        try:
            p = serial.Serial(port)
            p.close()
            return True
        except serial.SerialException:
            return False


    def print_list(self, verbose_print, test_port_avail):
        """
        Prints a list of all serial ports.

        Additional device information can be printed if 'verbose_print' is True
        
        If 'test_port_avail' is True, this function will additionally check if the
        specified port is avilable (i.e. not already open). This option does not
        depend on the verbose option.
        """
        print("Available serial ports:")
        for i, serdev in enumerate(self.port_list):
            dev_str = f"{i+1}. {serdev[0]}"
            if test_port_avail:
                if self.__is_port_available(serdev[0]):
                    dev_str = dev_str + "\tAvailable"
                else:
                    dev_str = dev_str + "\tIn use"
            if verbose_print:
                dev_str = dev_str + f"\n\r\tDesc: {serdev[1]}\n\r\tHWID: {serdev[2]}"
            print(dev_str)
                      
        if not self.port_list:
            print("No serial ports available.")

    def get_port_from_number(self, port_id):
        return self.port_list[port_id-1][0]
    

    def validate(self, port_str):
        """
        Checks if the provided port string is valid and returns the validated
        string. If the port is not valid or can't be found, None will be returned.

        Using this functions allows the use of incomplete serial device identifier strings
        such as 'ttyACM0' instead of the full '/dev/ttyACM0'
        """
        port_paths = [p.device for p in self.port_list]
        path = [s for s in port_paths if port_str in s]
        if len(path) == 0:
            print(f"Invalid serial port: {port_str}")
            return None
        if (len(path)> 1):
            print(f"Multiple instances of {port_str} found...")
            return None
    
        return path[0]