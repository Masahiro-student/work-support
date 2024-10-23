#体性感覚モジュール用
import arduino

class ModuleController:
    arduino = None

    def __init__(self):
        self.initialize()

    def __del__(self):
        self.allmotor_stop()

    def initialize(self):
        self.arduino = arduino.Arduino("/dev/ttyUSB0")

    # hand_pos and goal_pos is in [0.0, 0.0] ~ [1.0, 1.0]  正規化している
    def drive(self, hand_pos, goal_pos):
        dx = goal_pos[0] - hand_pos[0]
        dy = goal_pos[1] - hand_pos[1]
        if abs(dx) > abs(dy):
            if dx > 0.0:
                self.send_pwm(1, 200)
            else:
                self.send_pwm(3, 200)
        else:
            if dy > 0.0:
                self.send_pwm(2, 200)
            else:
                self.send_pwm(0, 200)

    def drive_8direction(self, direction, intensity):
        self.stop()
        base, mod = divmod(direction, 2)
        if mod == 0:
            self.send_pwm(base, intensity)
        else:
            self.send_pwm(base, int(intensity / 1.4))
            self.send_pwm((base + 1) % 4, int(intensity / 1.4))

    def drive_4direction(self, direction, intensity):
        self.stop()
        self.send_pwm(direction, intensity)

    def drive_all(self, intensity):
        # print('all')
        val = int(intensity)
        self.arduino.send_serial("allmotor:" + str(val) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def send_pwm(self, motor, val):
        # print('pwm')
        motor = int(motor)
        val = int(val)
        self.arduino.send_serial("motor:" + str(motor) + ":" + str(val) + "\n")
        # 2行のメッセージが来るため
        results = [self.arduino.read_serial() for i in range(2)]
        # print(results)

    def allmotor_stop(self):
        # print('all stop')
        val = int(0)
        self.arduino.send_serial("allmotor:" + str(val) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def prm(self, motor_num):
        # print('prm')
        motor = int(motor_num)
        self.arduino.send_serial("prm:" + str(motor) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def valve(self, valve_num, valve_state):
        # print('valve')
        valve_n = int(valve_num)
        valve_s = int(valve_state)
        self.arduino.send_serial("valve:" + str(valve_n) + ":" + str(valve_s) + "\n")
        result = self.arduino.read_serial()
        print(result)


    def mod(self, mode_prm):
        # print('mod')
        mode_p = int(mode_prm)
        self.arduino.send_serial("mod:" +  str(mode_p) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def pressure(self, unload_press):
        # print('stop')
        unload_p = int(unload_press)
        self.arduino.send_serial("stop:" + str(unload_p) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def comp_start(self):
        # print('comp start')
        on_off = int(1)
        self.arduino.send_serial("comp:" + str(on_off) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def comp_stop(self):
        # print('comp stop')
        on_off = int(0)
        self.arduino.send_serial("comp:" + str(on_off) + "\n")
        result = self.arduino.read_serial()
        print(result)

    def motor_right_forearm(self):
        self.send_pwm(0,100)
        self.send_pwm(1,100)
        self.send_pwm(3,100)
        self.send_pwm(4,100)

    def motor_right_forearm_stop(self):
        self.send_pwm(0,0)
        self.send_pwm(1,0)
        self.send_pwm(3,0)
        self.send_pwm(4,0)