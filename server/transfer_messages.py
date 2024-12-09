import time
from datetime import datetime

class DisconnectError(Exception):
    def __init__(self, sock):
        super().__init__(sock)
        self.sock = sock

def receive_message(sock, length=1024, DEBUG=True):
    try:
        messages = sock.recv(length).decode("utf-8").split("\0")[:-1]
    except ConnectionResetError:
        raise DisconnectError(sock)

    messages_dict = []
    for message in messages:
        message = message.split("\1")
        sending_time = message[0]
        mes_type = message[1]
        action = message[2]
        parameters = ' '.join(message[3:]) if len(message) > 3 else None

        if DEBUG:
            reading_time = datetime.utcfromtimestamp(float(sending_time)).strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
            diff = round(time.time() - float(sending_time), 4)
            if parameters:
                print(f"RECEIVE [{reading_time}] ({diff}). Type: {mes_type}, action: {action}, parameters: {parameters}")
            else:
                print(f"RECEIVE [{reading_time}] ({diff}). Type: {message[1]}, action: {message[2]}")

        messages_dict.append({"time": sending_time, "type": mes_type, "action": action, "parameters": parameters})
    
    return messages_dict

def send_message(sock, mes_type, action, parameters=None, length=1024, DEBUG=True):
    now = time.time()
    if parameters:
        message = f"{now}\1{mes_type}\1{action}\1{parameters}\0"
    else:
        message = f"{now}\1{mes_type}\1{action}\1\0"

    try:
        sock.send(message.encode("utf-8"))
    except ConnectionResetError:
        DisconnectError(sock)

    if DEBUG:
        reading_time = datetime.utcfromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
        if parameters:
            print(f"SEND [{reading_time}]. Type: {mes_type}, action: {action}, parameters: {parameters}")
        else:
            print(f"SEND [{reading_time}]. Type: {mes_type}, action: {action}")