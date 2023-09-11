import serial
import threading
import subprocess
import shutil


class Term:

    def __init__(self, dev_path, baud):
        self.port = dev_path
        self.baud = baud


    def __open_serial_port_python(self, baud_rate):
        try:
            ser = serial.Serial(self.port, baud_rate)

            def receive_serial():
                while True:
                    try:
                        data = ser.readline().decode().rstrip()
                        print(data)
                    except UnicodeDecodeError:
                        pass

            def send_serial():
                while True:
                    try:
                        input_data = input()
                        ser.write(input_data.encode())
                    except (KeyboardInterrupt, EOFError):
                        ser.close()
                        break

            receive_thread = threading.Thread(target=receive_serial, daemon=True)
            send_thread = threading.Thread(target=send_serial, daemon=True)

            print(f"Serial port {self.port} opened. Press Ctrl+C to exit.")

            receive_thread.start()
            send_thread.start()

            receive_thread.join()
            send_thread.join()

        except serial.SerialException as e:
            print(f"Failed to open serial port {self.port}: {str(e)}")


    def __open_serial_port_terminal(self, terminal_program):
        if shutil.which('putty'):
            term_cmd = [
                'putty',
                '-serial',
                self.port,
                '-sercfg',
                str(self.baud),
                ', 8N1'
            ]
            #terminal_program = f"putty {self.port} -serial -sercfg {self.baud},8,n,1,N"
        elif shutil.which('screen'):
            terminal_program = 'screen'
        elif shutil.which('minicom'):
            terminal_program = 'minicom'
        else:
            print("No supported terminal program found.")
            return False
        
        print(term_cmd)

        try:
            subprocess.Popen(term_cmd)
        except FileNotFoundError:
            print(f"{terminal_program} is not installed or not in the system path.")
        return True


    def start(self, term=None):
        if self.__open_serial_port_terminal(term):
            return
        self.__open_serial_port_python()