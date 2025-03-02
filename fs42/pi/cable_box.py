import json
import time

# Uses adafruit circuitpython via Blink - install blinka first: 
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
# pip3 install adafruit-circuitpython-matrixkeypad
import digitalio
import adafruit_matrixkeypad
import board

#also requires tm1673 library:
# pip3 install raspberrypi-tm1637
import tm1637



class CableBox:

    def __init__(self, channel_socket = "runtime/channel.socket", status_socket = "runtime/play_status.socket"):

        self.channel_socket = channel_socket
        self.status_socket = status_socket

        self.tm = tm1637.TM1637(clk=17, dio=18)    
        self.tm.brightness(0)
        self.tm.show("FS42")

        column_pins = [digitalio.DigitalInOut(x) for x in (board.D26, board.D20, board.D21)]
        row_pins = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]

        # Define keypad layout
        keys = (
            ('1', '2', '3'),
            ('4', '5', '6'),
            ('7', '8', '9'),
            ('down', '0', 'up'))

        self.keypad = adafruit_matrixkeypad.Matrix_Keypad(row_pins, column_pins, keys)
        self.last_stat = ""
        

    def send_command(self, command, channel=-1):
        as_obj = {'command' : command, 'channel': channel}
        as_str = json.dumps(as_obj)
        print(f"Sending command: {as_str}")
        with open(self.channel_socket, "w") as fp:
            fp.write(as_str)    

    def check_status(self):
        new_stat = None
        with open(self.status_socket) as fp:
            as_str = fp.read()

            if as_str != self.last_stat:
                print("Status changed:")
                self.last_stat = as_str
                new_stat = json.loads(as_str)

        return new_stat
                
            

    def read_keys(self):
        pressed = self.keypad.pressed_keys
        if len(pressed) == 1:
            return pressed[0]
        return None



    def event_loop(self):
        
        last_pressed = ""
        in_selection = False
        last_selection_tick = -1
        channel_num = 0 
        while True:
            key_pressed = self.read_keys()
            
            if key_pressed:
                self.tm.show(f"    ")
                last_selection_tick = time.monotonic()
                in_selection = True
                
                as_num = None
                print("Key pressed:", key_pressed)
                
                if key_pressed == "up":
                    self.send_command("up")
                    channel_num += 1
                    self.tm.show(f"----")
                    in_selection = False
                elif key_pressed == "down":
                    if(channel_num > 0):
                        self.send_command("down")
                        channel_num -= 1
                        self.tm.show(f"----")
                    in_selection = False
                else:                                    
                    try:
                        as_num = int(last_pressed+key_pressed)
                        last_pressed = key_pressed
                        self.tm.show(f"  {as_num:02d}")
                    except:
                        pass
                
                
                time.sleep(0.3)

                
            # see if we need to reset selection or apply it
            if in_selection:
                tick_diff = time.monotonic() - last_selection_tick
                if tick_diff > 1.5:
                    print(f"Applying selection CH{as_num:02d}")
                    self.tm.show(f"CH{as_num:02d}")
                    last_selection_tick = -1
                    in_selection = False
                    last_pressed = ""
                    channel_num = as_num
                    self.send_command("direct", channel_num)
                
            
            time.sleep(0.1)
            
            new_stat = self.check_status()
            if new_stat:
                try:
                    channel_num = int(new_stat['channel_number'])
                    if channel_num >= 0:
                        self.tm.show(f"CH{channel_num:02d}")
                        print("Set channel: ", channel_num)
                    else:
                        self.tm.show("FS42")
                except:
                    self.tm.show("FS42")


if __name__ == "__main__": 
    cable_box = CableBox()
    cable_box.event_loop()

