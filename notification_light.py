import yeelight as yl
from time import sleep
from sun_time import get_sun_times
import datetime
bulb = None
l = yl.discover_bulbs(timeout=5)
if l:
    bulb_data = l[0]
    ip = bulb_data["ip"]
    bulb = yl.Bulb(ip)

def find_bulb():
    l = yl.discover_bulbs(timeout=5)
    if l:
        print("found bulb")
        bulb_data = l[0]
        ip = bulb_data["ip"]
        bulb = yl.Bulb(ip)
        return bulb
    return None

def toggle(bulb):
    bulb.toggle()

def flash(bulb, type):
    if "notify" in type:
        call_notify(bulb)
        return "notify"
    elif "long" in type:
        call_flash(bulb)
        return "long flash"
    else:
        flash_do(bulb)
        return "default flash"

def broadlink_switch(bulb):
    cur_time = datetime.datetime.now().hour + (datetime.datetime.now().minute/60)
    srise, sset = get_sun_times()
    if not (srise < cur_time < sset):
        return False
    try:
        bulb.turn_off()
    except:
        if bulb == None:
            for i in range(30):
                l = yl.discover_bulbs(timeout=2)
                if len(l) > 0: break
            if len(l) == 0:
                return False
            bulb_data = l[0]
            ip = bulb_data["ip"]
            bulb = yl.Bulb(ip)
            bulb.turn_off()
            return True
        return False

def call_notify(bulb):
    flash_do(bulb, repeat=2, sleep_time=0.2)

def call_flash(bulb):
    flash_do(bulb, repeat=5)

def flash_do(bulb,repeat=3, sleep_time = 0.4):

    prop = bulb.get_properties()
    pre_bright = int(prop['bright'])
    pre_state = prop['power']
    bulb.turn_on()
    for x in range(repeat):
        bulb.set_brightness(100)
        sleep(sleep_time)
        bulb.set_brightness(0)
        sleep(sleep_time)
    bulb.set_brightness(pre_bright)
    if pre_state != bulb.get_properties()['power']:
        bulb.toggle()