import broadlink
import pickle
import sys
import logging
import os
import re
from time import sleep
import pychromecast
import threading
COMMAND_PICKLED = os.path.dirname(os.path.abspath(__file__)) + '/commands.pickled'
VARIBLE_PICKLED = os.path.dirname(os.path.abspath(__file__)) + "/varibles.pickled"
CHROMECAST_NAME = "Alexcast"

POWER = 'power'
VOLUME_UP = 'volume up'
VOLUME_DOWN = 'volume down'
VOLUME = 'volume'
SOURCE = 'source'
OK = 'okay'
UP = 'up'
DOWN = 'down'
CH_UP = "channel up"
CH_DOWN = "channel down"
INPUT_TO_NUMBER = {"tv": 1,
                   "av": 2,
                   "scart": 3,
                   "ypbpr": 4,
                   "hdmi 1": 5,
                   "hdmi 2": 6,
                   "hdmi 3": 7,
                   "pc": 8,
                   "media": 9,

                   "chromecast": 6,
                   "computer": 7,
                   "alexcast": 6,
                   "yes": 5,
                   "xbox": 7
}
class check_chromes(threading.Thread):
    def __init__(self, cast_name, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.exit = False
        self.caste_name = cast_name
        self.timeout = 5
        self.off_counter = 0
    
    def chrome_names(self, lst):
        names = []
        for d in lst:
            if type(d) is list:
                names.append(d[0].device.friendly_name)
        return names

    def run(self):
        self.off_counter = 0
        while not self.exit:
            chromecasts = pychromecast.get_chromecasts(timeout= self.timeout)
            names = self.chrome_names(chromecasts)
            if self.caste_name in names:
                self.parent.activate("set tv state to on", echo=False)
                self.off_counter = 0
            else:
                self.off_counter += 1
            if self.off_counter > 3:
                self.off_counter = 0
                self.parent.activate("set tv state to off", echo=False)
            sleep(self.timeout)




class TV_handler():
    def __init__(self, tv_name,ir_device_name):
        self.ir_device_name = ir_device_name
        self.tv_name = tv_name
        self.auth = False
        self.ir_device = None
        with open(COMMAND_PICKLED, 'rb') as commands_dictionary_file:
            try:
                self.commands_dictionary = pickle.load(commands_dictionary_file)
            except EOFError:
                self.commands_dictionary = {}
        with open(VARIBLE_PICKLED, 'rb') as varible_dictionry_file:
            try:
                self.state_dictionry = pickle.load(varible_dictionry_file)
            except EOFError:
                self.state_dictionry = {}
        self.chrome_check = check_chromes(CHROMECAST_NAME, self)
        self.chrome_check.start()

    def configure_power_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning Power Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new power state')
                self.commands_dictionary['power'] = ir_packet
                self.save_command()

    def configure_up_volume_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning volume up Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new volume state')
                self.commands_dictionary[VOLUME_UP] = ir_packet
                self.save_command()
            else:
                print("Havn't got any information")

    def configure_down_volume_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning volume down Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new volume state')
                self.commands_dictionary[VOLUME_DOWN] = ir_packet
                self.save_command()

    def configure_channel_down_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning channel down Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new state')
                self.commands_dictionary[CH_DOWN] = ir_packet
                self.save_command()

    def configure_channel_up_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning channel up Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new volume state')
                self.commands_dictionary[CH_UP] = ir_packet
                self.save_command()

    def configure_ok_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning ok button")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new ok button')
                self.commands_dictionary[OK] = ir_packet
                self.save_command()

    def configure_source_packet(self):
        if self.auth:
            self.ir_device.enter_learning()
            ir_packet = None
            timeout = 1000
            print ("Learning source/input Mode")
            while (ir_packet is None):
                ir_packet = self.ir_device.check_data()
                timeout -= 1
                if timeout <= 0:
                    break
            if ir_packet is not None:
                print('The deviced has learned new imput state')
                self.commands_dictionary[SOURCE] = ir_packet
                self.save_command()

    def activate(self, text_command, echo=True):
        text_command = text_command.lower()
        if not "set" in text_command:
            if "netflix" in text_command or "chrome" in text_command:
                if self.state_dictionry[POWER] == "on":
                    self.set_source("change tv source to chromecast")
                else:
                    self.turn_power("turn on tv")
                    sleep(15.5)
                    self.set_source("change tv source to chromecast")
            elif "cable tv" in text_command or ("yes" in text_command and "mode" in text_command):
                if self.state_dictionry[POWER] == "on":
                    self.set_source("change tv source to yes")
                else:
                    self.turn_power("turn on tv")
                    sleep(15.5)
                    self.set_source("change tv source to yes")
            elif "xbox" in text_command:
                if self.state_dictionry[POWER] == "on":
                    self.set_source("change tv source to xbox")
                else:
                    self.turn_power("turn on tv")
                    sleep(15.5)
                    self.set_source("change tv source to xbox")

        elif "set" in text_command:
            if 'volume' in text_command and 'state' in text_command:
                self.set_volume_state(text_command)
            elif ('source' in text_command or 'input' in text_command) and 'state' in text_command:
                self.set_source_state(text_command)
            elif ('source' in text_command or 'input' in text_command) and 'state' not in text_command:
                self.set_source(text_command)
            elif 'set' in text_command and ('on' in text_command or 'off' in text_command):
                self.set_power_state(text_command, echo)

        elif 'turn' in text_command and ('on' in text_command or 'off' in text_command):
            self.turn_power(text_command)

    def save_file(self, file_path, data):
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

    def save_state(self):
        self.save_file(VARIBLE_PICKLED, self.state_dictionry)

    def save_command(self):
        self.save_file(COMMAND_PICKLED, self.commands_dictionary)

    def set_ir_device(self, ir_device):
        self.ir_device = ir_device

    def configure_device(self):
        timeout = 1
        devices = []
        while len(devices) < 1:
            devices = broadlink.discover(timeout=timeout)
            timeout += 1
        self.ir_device = devices[0]
        self.auth = self.ir_device.auth()
        '''
        if len(devices) != 0:
            for device in devices:
                if type(device) == broadlink.rm and device.auth():
                    if 'turn' in text_command:
                        turn_power(device, text_command)'''

    def state_analyzer(self, text_command):

        if 'on' in text_command.lower():
            return 'on'
        elif 'off' in text_command.lower():
            return 'off'
        else:
            logging.error('Got wrong input for turning TV state:' + text_command)
            return None, None

    def turn_power(self, text_command, echo=True):
        if self.ir_device is None:
            self.configure_device()
        if echo:
            print('Current state:' + self.state_dictionry[POWER])
        current_state = self.state_dictionry[POWER]
        wanted_state = self.state_analyzer(text_command)
        if echo:
            print('wanted state:' + wanted_state )
        if wanted_state != current_state:
            if echo:
                print('turning on/off')
            self.ir_device.send_data(self.commands_dictionary[POWER])
            self.state_dictionry[POWER] = wanted_state
            self.save_state()
        else:
            if echo:
                print('Device already in this state')

    def set_power_state(self, text_command, echo=True):
        wanted_state = self.state_analyzer(text_command)
        if echo:
            print ("Setting Power State")
            print ("Current Source State: " + self.state_dictionry[POWER] + "\nWanted State: " + wanted_state)
        if wanted_state.lower() == 'on' or wanted_state.lower() == 'off':
            self.state_dictionry['power'] = wanted_state
            self.save_state()
            if echo:
                print ("The power state was saved as: " + wanted_state)
        else:
            if echo:
                print('No such state')

    def volume_state_analyzer(self, text_command):
        if len(re.findall('\d+',text_command)) > 0:
            return int(re.findall('\d+',text_command)[0])
        else:
            return None

    def set_volume_state(self, text_command):
        wanted_volume = self.volume_state_analyzer(text_command)
        if wanted_volume is not None:
            self.state_dictionry[VOLUME] = wanted_volume
            self.save_state()
        else:
            print("iliigal volume")

    def set_volume(self, text_command):
        if self.ir_device is None:
            self.configure_device()
        wanted_state = self.volume_state_analyzer(text_command)
        if wanted_state is not None:
            current_volume = self.state_dictionry[VOLUME]
            change = wanted_state - current_volume
            print("current volume:" + str(current_volume))
            print("wanted volume:" + str(wanted_state))
            print("changing volume by:" + str(change))
            if change > 0:
                self.up_volume(change)
            else:
                change = 0 - change
                self.down_volume(change)
            print("new volume:" + str(wanted_state))
            self.state_dictionry[VOLUME] = wanted_state
            self.save_state()
        else:
            print("illigal Volume")

    def up_volume(self, repeat):
        counter = 0
        while counter < repeat:
            self.ir_device.send_data(self.commands_dictionary[VOLUME_UP])
            counter += 1

    def down_volume(self, repeat):
        counter = 0
        while counter < repeat:
            self.ir_device.send_data(self.commands_dictionary[VOLUME_DOWN])
            counter += 1

    def set_source(self, text_command):
        if self.ir_device is None:
            self.configure_device()
        wanted_state = self.source_analyzer(text_command)
        print ("Current Source State: " + str(self.state_dictionry[SOURCE]) + "\nWanted State: " + str(wanted_state))
        if wanted_state is not None:
            print("Changing Source")
            self.next_source(self.source_repeat_number_calc(wanted_state))
            self.press_ok()
            self.set_source_state(text_command)
        else:
            print("Illigal Value")


    def source_analyzer(self, text_command):
        print(text_command)
        options_list = []
        for source in INPUT_TO_NUMBER:
            if str(source) in str(text_command):
                options_list.insert(len(options_list), source)
        if len(options_list) == 1:
            return INPUT_TO_NUMBER[options_list[0]]
        else:
            wanted_source = ""
            for source in options_list:
                if len(source) > len(wanted_source):
                    wanted_source = source
            return INPUT_TO_NUMBER[wanted_source]
        return

    def set_source_state(self, text_command):
        wanted_input = self.source_analyzer(text_command)
        print ("Current Source State: " + str(self.state_dictionry[SOURCE]) + "\nWanted State: " + str(wanted_input))
        if wanted_input is not None:
            self.state_dictionry[SOURCE] = wanted_input
            self.save_state()
        else:
            print("iliigal input")

    def source_repeat_number_calc(self, wanted_state):
        current_state = self.state_dictionry[SOURCE]
        if wanted_state - current_state >= 0:
            return (wanted_state - current_state, CH_DOWN)
        elif wanted_state - current_state < 0:
            return (abs(wanted_state - current_state) , CH_UP)


    def get_number_of_sources(self):
        max = 0
        for x in INPUT_TO_NUMBER:
            if max < INPUT_TO_NUMBER[x]:
                max = INPUT_TO_NUMBER[x]
        return max

    def next_source(self, repeat):
        print(repeat)
        repeat_num, packet = repeat
        self.ir_device.send_data(self.commands_dictionary[SOURCE])
        counter = 0
        while counter < repeat_num:
            self.ir_device.send_data(self.commands_dictionary[packet])
            counter += 1

    def press_ok(self):
        self.ir_device.send_data(self.commands_dictionary[OK])



def lunching(text_command):
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("args:" + str(sys.argv))
    tv = TV_handler("ir_tv", "ir")
    tv.activate(text_command)

def configrue_packets():
    # lunching("turn on tv")
    tv = TV_handler("ir_tv", "i")
    tv.configure_device()
    print(tv.ir_device)
    # tv.configure_power_packet()
    # tv.configure_source_packet()
    # tv.configure_up_volume_packet()
    # tv.configure_down_volume_packet()
    # tv.configure_ok_packet()
    # tv.configure_channel_up_packet()
    # tv.configure_channel_down_packet()

def check():
    print("HEYYYYYYYYY")

if __name__ == '__main__':
    tv = TV_handler("ir_tv", "i")
    tv.configure_device()
    for x in range(30):
        print(tv.state_dictionry)
        print(tv.chrome_check.off_counter)
        sleep(5)


