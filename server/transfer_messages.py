import time
from datetime import datetime

class DisconnectError(Exception):
    def __init__(self, sock):
        super().__init__(sock)
        self.sock = sock

SEPARATOR = "NEXT"
END = "END"
CONTINUE = "CON"

def receive_message(sock, length=1024, DEBUG=True):
    global SEPARATOR, END, CONTINUE

    try:
        recv_message = f"{CONTINUE}"
        while recv_message[-len(CONTINUE):] == CONTINUE:
            recv_message = recv_message[:-len(CONTINUE)]
            recv_message += sock.recv(length).decode("utf-8")
    except ConnectionResetError:
        raise DisconnectError(sock)

    for i in range(len(recv_message)-len(CONTINUE)):
        if recv_message[i:i+len(CONTINUE)] == CONTINUE:
            recv_message = recv_message[:i] + recv_message[i+len(CONTINUE):]

    messages = recv_message.split(END)[:-1]

    messages_dict = []
    for message in messages:
        message = message.split(SEPARATOR)
        sending_time = message[0]
        mes_type = message[1]
        action = message[2]
        parameters = ''.join(message[3:]) if len(message) > 3 else None

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
    '''ATTENSION: Don't use syntax words like "CON", "NEXT" or "END" in messages'''
    global SEPARATOR, END, CONTINUE

    now = time.time()
    if parameters:
        message = f"{now}{SEPARATOR}{mes_type}{SEPARATOR}{action}{SEPARATOR}{parameters}{END}"
    else:
        message = f"{now}{SEPARATOR}{mes_type}{SEPARATOR}{action}{SEPARATOR}{END}"

    chunks_amount = (len(message)-1) // (length-len(CONTINUE))

    try:
        for i in range(chunks_amount):
            start_idx = i*length-i*len(CONTINUE)
            end_idx = i*length-i-len(CONTINUE)+length-i*(len(CONTINUE)-1)

            chunk_message = f"{message[start_idx:end_idx]}{CONTINUE}"
            sock.send(chunk_message.encode('utf-8'))

        last_chunk_message = f"{message[chunks_amount*length-chunks_amount*len(CONTINUE):]}"
        sock.send(last_chunk_message.encode('utf-8'))
    except ConnectionResetError:
        DisconnectError(sock)

    if DEBUG:
        reading_time = datetime.utcfromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
        if parameters:
            print(f"SEND [{reading_time}]. Type: {mes_type}, action: {action}, parameters: {parameters}")
        else:
            print(f"SEND [{reading_time}]. Type: {mes_type}, action: {action}")