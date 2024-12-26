import os
import socket
import threading
import json
from time import sleep
import uuid
import random

from player import ServerPlayer
from transfer_messages import DisconnectError, send_message, receive_message

SERVER_IP = 'localhost'
SERVER_PORT = 19560
SERVER_PASSWORD = ''
MAP_PATH = './maps_conf/map.json'
MAX_CONNECTIONS = 2
DATA_SIZE = 1024
PLAYERS = []
PLAYER_POS = [i for i in range(MAX_CONNECTIONS)]
CATCHER_AMOUNT = 1
RUNNER_AMOUNT = 1
GAME_COUNT = 0
WINNERS = []

def broadcast_to_all(type, action, parameters=None):
    global PLAYERS, PLAYER_POS, WINNERS
    
    for player in PLAYERS:
        send_message(player.client, type, action, parameters)


def broadcast_to_all_except_one(client: socket.socket, type, action, parameters=None):
    global PLAYERS
    
    for p in PLAYERS:
        if p.client != client:
            send_message(p.client, type, action, parameters)


def game(player: ServerPlayer) -> None:
    global PLAYERS, PLAYER_POS, MAX_CONNECTIONS, DATA_SIZE

    with open(MAP_PATH, 'r') as file:
        map_data = json.load(file)
        raw_data = json.dumps(map_data, separators=(',', ':'))
        send_message(player.client, "game", "map", raw_data)

    start_pos = PLAYER_POS[len(PLAYERS)-1]
    if start_pos < CATCHER_AMOUNT:
        player.is_catcher = True
    else:
        player.is_catcher = False
    send_message(player.client, "game", "game_pos", str(start_pos))

    for p in PLAYERS:
        if p != player:
            # Send to player all other players data
            send_message(player.client, "game", "new_player", f"{p.uuid} {int(p.is_ready)} {int(p.is_catcher)} {p.name}")
    # Send to other players this player data
    broadcast_to_all_except_one(player.client, "game", "new_player", f"{player.uuid} {int(player.is_ready)} {int(player.is_catcher)} {player.name}")
    
    while True:
        try:
            msgs: list[dict] = receive_message(player.client, DATA_SIZE)
            for msg in msgs:
                if msg['type'] == "game":
                    match msg['action']:
                        case "ready":
                            broadcast_to_all_except_one(player.client, "game", "switch_ready_status", f"{player.uuid} {msg['parameters']}")
                            player.is_ready = bool(int(msg['parameters']))
                            if all([user.is_ready for user in PLAYERS]) and len(PLAYERS) == MAX_CONNECTIONS:
                                broadcast_to_all("game", "start_countdown")
                        case "movement":
                            player.movement = msg["parameters"]
                            broadcast_to_all_except_one(player.client, "game", "other_movement", f"{player.uuid}!{player.movement}")

                            if all([user.movement for user in PLAYERS]):
                                broadcast_to_all("game", "start_simulation")
                        case "result":
                            pass
                    
        except DisconnectError as de:
            print(f'Connection from {player.client.getpeername()} has been lost.')
            # Delete player from PLAYERS
            for i in range(0, len(PLAYERS)):
                if PLAYERS[i].client == de.sock:
                    del PLAYERS[i]
                    break
            player.client.close()
            broadcast_to_all("game", "player_disconnected", player.uuid)
            break


def auth(client: socket.socket) -> None:
    current_player = ServerPlayer()

    try:
        while True:
            msgs: list[dict] = receive_message(client, DATA_SIZE)
            for msg in msgs:
                if msg['type'] == "auth":
                    match msg['action']:
                        case "connect":
                            if len(PLAYERS) >= MAX_CONNECTIONS:
                                send_message(client, "auth", "field_full")
                                break
                            else:
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
                            
                            current_player.name = msg['parameters']
                            current_player.uuid = str(uuid.uuid4())
                            current_player.client = client
                            current_player.is_ready = False
                            send_message(client, "auth", "uuid", current_player.uuid)
                            PLAYERS.append(current_player)
                            send_message(client, "auth", "success")
                            game(current_player)
                            break
    except DisconnectError:
        print(f'Connection from {client.getpeername()} has been lost.')
        client.close()
    except OSError:
        print(f'Connection has been lost.')
        client.close()


def main():
    global SERVER_IP, SERVER_PORT, SERVER_PASSWORD, MAP_PATH, MAX_CONNECTIONS, PLAYER_POS, CATCHER_AMOUNT, RUNNER_AMOUNT

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
        CATCHER_AMOUNT = len(map_data['catcher_start_pos'])
        RUNNER_AMOUNT = len(map_data['runner_start_pos'])
        MAX_CONNECTIONS = CATCHER_AMOUNT + RUNNER_AMOUNT
        
        PLAYER_POS = [i for i in range(MAX_CONNECTIONS)]
        random.shuffle(PLAYER_POS)
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