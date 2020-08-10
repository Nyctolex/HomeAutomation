from flask import (Flask, request, make_response)
from flask import request
import broadlinkIRHandler as br
import notification_light as nl
import datetime
import yeelight as yl
from subprocess import call
import json

from time import sleep
BULB = None
BULB = nl.find_bulb()

tv = br.TV_handler("ir_tv", "ir")

class Qeue_fifo():
    def __init__(self):
        self.qeue = []

    def put(self, arg):
        self.qeue.append(arg)

    def get(self):
        if self.is_not_empty():
            data = self.qeue[0]
            self.qeue.pop(0)
            return data
        else:
            return None

    def is_empty(self):
        if len(self.qeue) == 0:
            return True
        else:
            return False

    def is_not_empty(self):
        return not self.is_empty()

    def print_qeue(self):
        print(self.qeue)

    def get_qeue(self):
        return self.qeue

html_file = '<html><table style="width:100%"  cellpadding="0" cellspacing="0" border="1"> {} </table></html>'

def add_row(*args):
    if len(args) != 0:
        add_to_html = "<tr>"
        for box in args:
            add_to_html += "<td>{}</td>".format(box)
        add_to_html += "/<tr>"
        return add_to_html


command_qeue = Qeue_fifo()
old_command_qeue = Qeue_fifo()
app = Flask(__name__)
BULB = nl.find_bulb()


@app.route('/')
def home():
    return '<h1>hello!</h1>'

@app.route('/webhook')
def webhook():
    req = request.get_json(silent=True, force=True)
    res = proccesRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    return r

def proccesRequest(req):
    speech = "Home and stuff"
    return {"fulfilmentText": speech, }
    # queryResponse = request["QueryResult"]
    # print(queryResponse)
    # text = query_response
    # text = queryResponse.get('parameters', None)


@app.route('/LIGHT', methods=['GET', 'POST'])
def light_handle():
    global BULB
    bulb = BULB
    if not bulb:
        bulb = nl.find_bulb()
        BULB = bulb
    args_dict = request.args.to_dict()
    if "broadlink" in args_dict:
            nl.broadlink_switch(bulb, datetime.datetime.now().hour)
            return '<h1>Done</h1>'
    if bulb:
        if "type" in args_dict:
            type = nl.flash(bulb, args_dict["type"])
            old_command_qeue.put('Flash type: {0}</h1>'.format(type))
            print('Flash type: {0}</h1>'.format(type))
            return '<h1>Flashing Light type: {0}</h1>'.format(type)
        elif "toggle" in args_dict:
            bulb.toggle()
            return '<h1>Toggle</h1>'
        elif 'state' in args_dict:
            if args_dict["state"].lower() == "on":
                bulb.turn_on()
            else:
                bulb.turn_off()
        elif "brightness" in args_dict:
            bulb.set_brightness(int(args_dict["brightness"]))
    return '<h1>bulb is unavalibe rn</h1>'

@app.route('/IR', methods=['GET', 'POST'])
def add_commane():
    print("Got Something")
    args_dict = request.args.to_dict()
    if "cmd" in args_dict:
        command_qeue.put(args_dict["cmd"])
        command_qeue.print_qeue()
        command = command_qeue.get()
        old_command_qeue.put(command)
        tv.activate(args_dict["cmd"])
        return '<h1>instrted command ' + args_dict["cmd"] + ' </h1>'

    else:
        print("sending command to user")
        if command_qeue.is_not_empty():
            command = command_qeue.get()
            old_command_qeue.put(command)
            return "<h1>" + str(command) + "</h1>"
        else:
            return '<h1>No commands</h1>'

@app.route('/GET')
def get_qeue_file():
    html_copy = html_file
    add_to = add_row('<span style="font-weight:bold">Commands:</span>')
    command_list = command_qeue.get_qeue()
    for x in range(len(command_list)):
        add_to += add_row('<span style="font-weight:bold">{}{}:</span>{}'.format(x + 1, '. ', command_list[x]))
    add_to += add_row('<span style="font-weight:bold">Old Commands:</span>')
    command_list = old_command_qeue.get_qeue()
    for x in range(len(command_list)):
        add_to += add_row('<span style="font-weight:bold">{}{}:</span>{}'.format(x + 1, '. ', command_list[x]))
    return html_copy.format(add_to)

@app.route('/CLEAROLD')
def clear_old_qeue():
    while old_command_qeue.is_not_empty():
        old_command_qeue.get()
    return '<h1>OLD COMMAND QEUE HAS BEEN FLUSHED</h1>'

@app.route('/CLEAR')
def clear_qeue():
    while command_qeue.is_not_empty():
        command_qeue.get()
    return '<h1>COMMAND QEUE HAS BEEN FLUSHED</h1>'

@app.route('/REBOOT')
def reboot_pc():
    call("reboot.sh")
    return '<h1>Shutting down server.</h1>'

# @app.route('/EXIT')
# def reboot_pc():
#     exit(0)
#     return '<h1>exiting server.</h1>'



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)