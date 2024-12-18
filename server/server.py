import os
import socket
import threading
import json
from time import sleep
import uuid

from player import ServerPlayer
from transfer_messages import DisconnectError, send_message, receive_message

SERVER_IP = 'localhost'
SERVER_PORT = 19560
SERVER_PASSWORD = ''
MAP_PATH = './maps_conf/map.json'
MAX_CONNECTIONS = 2
DATA_SIZE = 1024
PLAYERS = []


def wait_very_small_time_between_requests():
    sleep(0.005)


def auth(client: socket.socket) -> None:
    current_player = ServerPlayer()

    try:
        while True:
            msgs: list[dict] = receive_message(client, DATA_SIZE)
            for msg in msgs:
                if msg['type'] == "auth":
                    match msg['action']:
                        case "connect":
                            # if len(PLAYERS) >= MAX_CONNECTIONS:
                            #     send_message(client, "auth", "field_full")
                            #     break
                            # else:
                            send_message(client, "auth", "request_password")
                        case "response_password":
                            if msg['parameters'] == SERVER_PASSWORD:
                                send_message(client, "auth", "success_password")
                                send_message(client, "auth", "request_name")
                            else:
                                send_message(client, "auth", "wrong_password")
                                break
                        case "response_name":
                            name_is_taken = False
                            for i in range(0, len(PLAYERS)):
                                if PLAYERS[i].name == msg['parameters']:
                                    send_message(client, "auth", "name_taken")
                                    name_is_taken = True
                                    break

                            if name_is_taken:
                                break
                            
                            send_message(client, "auth", "success_name")
                            wait_very_small_time_between_requests()
                            
                            current_player.name = msg['parameters']
                            current_player.uuid = str(uuid.uuid4())
                            current_player.client = client
                            send_message(client, "auth", "uuid", current_player.uuid)
                            PLAYERS.append(current_player)
                            send_message(client, "auth", "success")
    except DisconnectError:
        print(f'Connection from {client.getpeername()} has been lost.')
        client.close()

            



def main():
    global SERVER_IP, SERVER_PORT, SERVER_PASSWORD, MAP_PATH, MAX_CONNECTIONS

    try:
        with open('server/server_conf.json', 'r') as file:
            data = json.load(file)
            SERVER_IP = data['ip']
            SERVER_PORT = data['port']
            SERVER_PASSWORD = data['password']
            MAP_PATH = data['map_path']
    except FileNotFoundError:
        print('No server_conf.json file found. Please provide values: ip, port, password.')
        SERVER_IP = input('Server IP: ')
        SERVER_PORT = int(input('Server port: '))
        SERVER_PASSWORD = input('Server password: ')
        MAP_PATH = input('Map path: ')
    
    with open(MAP_PATH, 'r') as file:
        map_data = json.load(file)
        MAX_CONNECTIONS = len(map_data['catcher_start_pos']) + len(map_data['runner_start_pos'])
    print(f'Max connections: {MAX_CONNECTIONS}')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()

        print(f'Server listening on {SERVER_IP}:{SERVER_PORT}...')

        while True:
            client, address = server_socket.accept()
            print(f'Connection from {address} has been established.')

            threading.Thread(target=auth, args=(client,)).start()


if __name__ == '__main__':
    main()