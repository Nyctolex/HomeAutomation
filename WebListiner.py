import urllib3
import broadlinkIRHandler
import logging
import time
import datetime
import time
import socket
REQ = "http://chrisch202.pythonanywhere.com/IR"
HOST = "chrisch202.pythonanywhere.com"
REQ_TYPLE = "GET"
HTTP_REQ = "/IR"
# REQ = "http://10.0.0.3/IR"
# HOST = "http://10.0.0.3"
def fetch_data(http_handler):
    response = http_handler.request(REQ_TYPLE, REQ)
    return str(response.data.decode()).lower()

def save_protoccol(txt):
    with open("Protocol.txt", 'r') as protocol_file:
        file_data = protocol_file.read()
    file_data = file_data + txt
    with open("Protocol.txt", 'w') as protocol_file:
        protocol_file.write(file_data)


def socket_listiner():
    pass

if __name__ == "__main__":
    # broadlinkIRHandler.lunching("set tv state to off")
    # broadlinkIRHandler.lunching("turn on tv")
    # broadlinkIRHandler.lunching("set tv state source to yes")
    # broadlinkIRHandler.lunching("<h1>set tv volume state to 29</h1>")
    # broadlinkIRHandler.lunching("<h1>turn volume to 45</h1>")
    # exit(0)
    print("Starting")
    logger = logging.getLogger('my-logger')
    logger.propagate = False
    http = urllib3.PoolManager()
    data = fetch_data(http)
    doal = True
    old_command = ""
    while not "close server" in data:
        if not "no commands" in data:
            protocol_recorder = "\n\n{}:\n{}".format(str(datetime.datetime.now()), data)
            save_protoccol(protocol_recorder)
            save_protoccol(protocol_recorder)
            print("Got Command From Server: {}".format(data))
            try:
                broadlinkIRHandler.lunching(data)
            except Exception:
                print (Exception)
                save_protoccol(str(Exception))
            old_command = data
        logging.disable(1)
        data = fetch_data(http)
        time.sleep(0.5)
    print(data)
