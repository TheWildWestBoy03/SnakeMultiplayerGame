import socket
import threading
import json
import uuid

import pygame

import message
import random
import math

server_ip = "127.0.0.1"
server_port = 3001
MAXIMUM_CLIENTS = 2
login_token = "12345"
current_clients = 0

threads = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(MAXIMUM_CLIENTS)

game_screen = None
player1_snake = []
player2_snake = []
game_fruits = []
player_winner = "NONE"
player_loser = "NONE"

player1_score = 0
player2_score = 0

print("Waiting for connection...")

# rect collision detection function
def handle_rect_collision(rect1, rect2):
    [left_corner1_x, left_corner1_y, height1, width1] = rect1
    [left_corner2_x, left_corner2_y, height2, width2] = rect2

    return (left_corner1_x <= left_corner2_x + width2) and (left_corner1_x + width1 >= left_corner2_x) and (left_corner1_y <= left_corner2_y + height2) and (left_corner1_y + height1 >= left_corner2_y)

def handle_client(connection):
    global player1_snake, player2_snake, player1_score, player2_score, player_winner, player_loser
    while True:
        bytes = connection.recv(2048)

        if bytes != b"":
            new_message = json.loads(bytes.decode('utf-8'))

            if new_message["type"] == "LOGIN":
                client_token = new_message["message"]

                # when the login token is wrong, the match can't happen, so the server closes the socket
                if client_token != login_token:
                    if (new_message["player"] == "player2"):
                        player_winner = "player1"
                        player_loser = "player2"
                    else:
                        player_winner = "player2"
                        player_loser = "player1"

                    response = message.Message(new_message["id"], new_message["player"], "Invalid token", "RESPONSE")
                    encoded_response = json.dumps(response.return_dictionary()).encode('utf-8')
                    connection.send(encoded_response)
                else:
                    tail = {}

                    # initialization of snakes
                    if new_message["player"] == "player1":
                        tail = {"x": 200, "y": 200}
                    else:
                        tail = {"x": 500, "y": 200}

                    player_coordinates = [tail]

                    for i in range(0, 3):
                        snake_body_part = {"x": tail["x"], "y": tail["y"] + (i + 1) * 30}
                        player_coordinates.append(snake_body_part)

                    if (new_message["player"] == "players1"):
                        player1_snake = player_coordinates
                    else:
                        player2_snake = player_coordinates

                    response = message.Message(new_message["id"], new_message["player"], player_coordinates, "RESPONSE")
                    encoded_response = json.dumps(response.return_dictionary()).encode('utf-8')
                    connection.send(encoded_response)
            elif new_message["type"] == "GAMEMODE":
                response = message.Message(new_message["id"], new_message["player"], "CONTINUOUS", "RESPONSE")
                connection.send(json.dumps(response.return_dictionary()).encode('utf-8'))
            elif new_message["type"] == "MOVE":
                player_coordinates = new_message["message"]["currentPositions"]
                last_direction = new_message["message"]["lastDirection"]
                current_direction = new_message["message"]["type"]

                # deciding the snake position based on the last direction and the current inputed direction
                if current_direction == "":
                    response = message.Message(new_message["id"], new_message["player"], player_coordinates, "RESPONSE")
                    encoded_response = json.dumps(response.return_dictionary()).encode('utf-8')
                    connection.send(encoded_response)
                else:
                    player_coordinates_before_move = [p.copy() for p in player_coordinates]

                    former_tail = player_coordinates[0]
                    player_coordinates.pop(0)

                    if last_direction == "DOWN":
                        if current_direction == "LEFT":
                            head_position = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"]}
                            new_head_position = {"x": head_position["x"] - 30, "y": head_position["y"]}
                            player_coordinates.append(new_head_position)
                        elif current_direction == "RIGHT":
                            head_position = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"]}
                            new_head_position = {"x": head_position["x"] + 30, "y": head_position["y"]}
                            player_coordinates.append(new_head_position)
                        elif current_direction == "DOWN":
                            head_position = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"]}
                            new_head_position = {"x": head_position["x"], "y": head_position["y"] + 30}
                            player_coordinates.append(new_head_position)
                        elif current_direction == "UP":
                            player_coordinates.insert(0, former_tail)
                            player_coordinates.pop()
                            player_coordinates.insert(0, {"x": player_coordinates[0]["x"], "y": player_coordinates[0]["y"] - 30})
                    elif last_direction == "RIGHT":
                        if current_direction == "RIGHT":
                            new_head = {"x": player_coordinates[2]["x"] + 30, "y": player_coordinates[2]["y"]}
                            player_coordinates.append(new_head)
                        if current_direction == "UP":
                            new_head = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"] - 30}
                            player_coordinates.append(new_head)
                        if current_direction == "DOWN":
                            new_head = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"] + 30}
                            player_coordinates.append(new_head)
                        if current_direction == "LEFT":
                            player_coordinates.insert(0, former_tail)
                            player_coordinates.pop()
                            player_coordinates.insert(0, {"x": former_tail["x"], "y": former_tail["y"] - 30})
                    elif last_direction == "UP":
                        if current_direction == "LEFT":
                            new_head = {"x": player_coordinates[2]["x"] - 30, "y": player_coordinates[2]["y"]}
                            player_coordinates.append(new_head)
                        if current_direction == "RIGHT":
                            new_head = {"x": player_coordinates[2]["x"] + 30, "y": player_coordinates[2]["y"]}
                            player_coordinates.append(new_head)
                        if current_direction == "UP":
                            new_head = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"] - 30}
                            player_coordinates.append(new_head)
                        if current_direction == "DOWN":
                            player_coordinates.insert(0, former_tail)
                            player_coordinates.pop()
                            player_coordinates.insert(0, {"x": former_tail["x"], "y": former_tail["y"] + 30})
                    elif last_direction == "LEFT":
                        if current_direction == "LEFT":
                            new_head = {"x": player_coordinates[2]["x"] - 30, "y": player_coordinates[2]["y"]}
                            player_coordinates.append(new_head)
                        if current_direction == "DOWN":
                            new_head = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"] + 30}
                            player_coordinates.append(new_head)
                        if current_direction == "UP":
                            new_head = {"x": player_coordinates[2]["x"], "y": player_coordinates[2]["y"] - 30}
                            player_coordinates.append(new_head)
                        if current_direction == "RIGHT":
                            player_coordinates.insert(0, former_tail)
                            player_coordinates.pop()
                            player_coordinates.insert(0, {"x": former_tail["x"] + 30, "y": former_tail["y"]})
                    else:
                        print("Invalid direction")

                    snake_head = player_coordinates[3]
                    snake_head_rect = [player_coordinates[3]["x"], player_coordinates[3]["y"], 30, 30]

                    # checks for wall detection
                    if snake_head["x"] < 30 or snake_head["x"] > 770 or snake_head["y"] < 30 or snake_head["y"] > 570:
                        if (new_message["player"] == "player2"):
                            player_winner = "player1"
                            player_loser = "player2"
                        else:
                            player_winner = "player2"
                            player_loser = "player1"

                    # checks for collision with fruits
                    fruits_to_delete = []
                    for fruit in game_fruits:
                        fruit_rect = [fruit[0], fruit[1], 10, 10]
                        if handle_rect_collision(snake_head_rect, fruit_rect) == True:
                            fruits_to_delete.append(fruit)
                            if (new_message["player"] == "player1"):
                                player1_score += 100
                            else:
                                player2_score += 100

                        # match finishing condition
                        if player1_score >= 1000:
                            player_winner = "player1"
                            player_loser = "player2"
                        if player2_score >= 1000:
                            player_winner = "player2"
                            player_loser = "player1"

                    blocked = False

                    # handles snakes collision
                    if new_message["player"] == "player1":
                        for part in player2_snake:
                            other_rect = [part["x"], part["y"], 30, 30]
                            if handle_rect_collision(snake_head_rect, other_rect):
                                blocked = True
                                break
                    else:
                        for part in player1_snake:
                            other_rect = [part["x"], part["y"], 30, 30]
                            if handle_rect_collision(snake_head_rect, other_rect):
                                blocked = True
                                break

                    if blocked:
                        player_coordinates = [p.copy() for p in player_coordinates_before_move]

                    for fruit in fruits_to_delete:
                        game_fruits.remove(fruit)

                    if new_message["player"] == "player1":
                        player1_snake = player_coordinates
                    else:
                        player2_snake = player_coordinates

                    response = message.Message(new_message["id"], new_message["player"], player_coordinates, "RESPONSE")
                    encoded_response = json.dumps(response.return_dictionary()).encode('utf-8')
                    connection.send(encoded_response)
            elif new_message["type"] == "FRUIT_REQUEST":
                to_generate = False
                fruit_position = []

                # random fruit generation to make sure no one spawns on snakes or walls
                while to_generate == False:
                    fruit_position = [random.random() * 500 + 200, random.random() * 400 + 100]
                    to_generate = True

                    if (player1_snake != []):
                        for i in range(0, len(player1_snake)):
                            snake_body_rect = [player1_snake[i]["x"], player1_snake[i]["y"], 30, 30]
                            fruit_rect = [fruit_position[0], fruit_position[1], 10, 10]

                            if (handle_rect_collision(snake_body_rect, fruit_rect)):
                                to_generate = False
                                break

                    if player2_snake != []:
                        for i in range(0, len(player2_snake)):
                            snake_body_rect = [player2_snake[i]["x"], player2_snake[i]["y"], 30, 30]
                            fruit_rect = [fruit_position[0], fruit_position[1], 10, 10]

                            if (handle_rect_collision(snake_body_rect, fruit_rect)):
                                to_generate = False
                                break

                game_fruits.append(fruit_position)
                response = message.Message(str(uuid.uuid4()), new_message["player"], fruit_position, "RESPONSE")
                connection.send(json.dumps(response.return_dictionary()).encode("utf-8"))
            elif new_message["type"] == "GET_FRUITS":
                response_message = message.Message(new_message["id"], new_message["player"], game_fruits, "RESPONSE")
                connection.send(json.dumps(response_message.return_dictionary()).encode("utf-8"))
            elif new_message["type"] == "GET_SCORES":
                response_message = message.Message(new_message["id"], new_message["player"], [player1_score, player2_score], "RESPONSE")
                connection.send(json.dumps(response_message.return_dictionary()).encode("utf-8"))

            elif new_message["type"] == "GET_MATCH_STATE":
                match_result = []

                print(player_winner)
                if (player_winner == "NONE"):
                    match_result.append("RUNNING")
                else:
                    match_result.append("STOPPED")
                    match_result.append(player_winner)
                    match_result.append(player_loser)

                response_message = message.Message(new_message["id"], new_message["player"],
                                                   match_result, "RESPONSE")
                connection.send(json.dumps(response_message.return_dictionary()).encode("utf-8"))

                if (match_result[0] == "STOPPED"):
                    connection.shutdown(socket.SHUT_RDWR)
                    connection.close()
                    break
            else:
                response = message.Message(new_message["id"], new_message["player"], "INVALID COMMAND", "RESPONSE")
                response_json = json.dumps(response.return_dictionary()).encode("utf-8")
                connection.send(response_json)


for i in range(MAXIMUM_CLIENTS):
    conn, addr = server_socket.accept()
    print("Connected by", addr)
    current_clients += 1

    t = threading.Thread(target=handle_client, args=(conn,))
    threads.append(t)
    t.start()

for thread in threads:
    thread.join()

print("done")