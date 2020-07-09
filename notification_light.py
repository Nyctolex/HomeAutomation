import yeelight as yl
from time import sleep
bulb = None
l = yl.discover_bulbs(timeout=5)
if l:
    bulb_data = l[0]
    ip = bulb_data["ip"]
    bulb = yl.Bulb(ip)

def toggle(bulb):
    pass

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