import argparse

import sertool
from sertool.serdev import SerialList
from sertool.term import Term


def print_serial_port_list(more_info, test_port):
    slist = SerialList()
    slist.print_list(more_info, test_port)


def open_serial_port(port_str, baud):
    slist = SerialList()

    if port_str.isdecimal():
        try:
            port = slist.get_port_from_number(int(port_str))
        except Exception:
            print(f"ERROR: {port_str} is not a valid serial port ID")
            return 1
    else:
        port = port_str

    port = slist.validate(port)
    if port is None:
        print(f"ERROR: {port_str} is not a valid serial port")
        return 1

    if not slist.is_port_available(port):
        print("ERROR: {port_str} is already in use")
        return 1

    print(f"Opening port {port}")
    term = Term(port, baud)
    term.start()
    return 0


def cli(argv):
    parser = argparse.ArgumentParser(description="Open a serial port and read/write data.")
    parser.add_argument('--version', action='version', version=sertool.__version__,
                                                help="Print package version")
    parser.add_argument('-p', '--port', help="Serial port path or number")
    parser.add_argument('--baud', type=int, default=115200,
                                                help="Baud rate (default: 115200)")
    parser.add_argument('-v', '--verbose', action='store_true',
                                                help="Print more information")
    parser.add_argument('-t', '--test', action='store_true',
                                                help="Test if serial port is available")

    args = parser.parse_args(argv)

    if not args.port:
        # If no port was provided, then we simply print the list of serial ports
        print_serial_port_list(args.verbose, args.test)
        return 0
    else:
        # Try to open serial port
        return open_serial_port(args.port, args.baud)
