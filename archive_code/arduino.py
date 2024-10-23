import serial


class Arduino:
    port = None
    serial = None

    def __init__(self, port):
        self.initialize(port)

    def __del__(self):
        self.finalize()

    def initialize(self, port):
        self.port = port
        self.open_port()

    def open_port(self):
        self.serial = serial.Serial(self.port, 9600)

    def finalize(self):
        self.close_port()

    def close_port(self):
        self.serial.close()

    def send_serial(self, string):
        #print(string)
        #print(string.encode())
        self.serial.write(string.encode())

    def send_bytes(self, b):
        b.append(10)
        self.serial.write(bytes(b))


    def flush(self):
        self.serial.flush()

    def read_serial(self):
        line = self.serial.readline()
        stripped_str = str(line, 'latin-1').strip()

        return stripped_str
