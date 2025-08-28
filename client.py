import random
import socket
import pygame
import message
import uuid
import json

threads = []
players = []
generated_fruits = []

# represents the current client, whose main role is just drawing on a window. The window is share
# among all players(currently limited to maximum 2 players)
class Player:
    def __init__(self, name, color, login_token, screen, keys, last_direction):
        self.name = name
        self.server = "127.0.0.1"
        self.last_direction = last_direction
        self.port = 3000
        self.color = color
        self.snake_positions = []
        self.score = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.login_token = login_token
        self.play = False
        self.screen = screen
        self.positions = {}
        self.keys = keys
        self.current_direction = ""

    def connect(self):
        self.socket.connect((self.server, self.port))

    def send_login_token(self):
        new_message = message.Message(str(uuid.uuid4()), self.name, self.login_token, "LOGIN")
        encoded_message = json.dumps(new_message.return_dictionary()).encode("utf-8")
        self.socket.send(encoded_message)

        response = json.loads(self.socket.recv(2048).decode("utf-8"))
        return response["message"]

    def update_function(self):
        self.snake_positions = self.send_login_token()

        if self.send_login_token() == "Invalid token":
            print("Invalid token")
        else:
            self.play = True

        for i in range(0, len(self.snake_positions)):
            pygame.draw.rect(self.screen, self.color, pygame.Rect(int(self.snake_positions[i]["x"]), int(self.snake_positions[i]["y"]), 30, 30))

    def display_player(self):
        print(self.server, self.port)
        print(self.color)
        print(self.snake_positions)
        print(self.score)
        print(self.socket)
        print("Last direction " + self.last_direction)

def configure_pygame():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Snake Multiplayer Game")
    screen.fill((255, 255, 255))
    screen.fill((0, 0, 0), (30, 30, screen.get_width() - 2 * 30, screen.get_height() - 2 * 30))

    return screen

def thread_function(player):
    player.update_function()

def stop_other_players(running_player):
    for player in players:
        if running_player.name != player.name:
            player.current_direction = ""

def handle_input(game_screen, event):
    for player in players:
        stop_other_players(player)
        if player.last_direction == "":
            player.last_direction = "DOWN"

        if event.key == player.keys[0]:
            player.current_direction = "UP"
        elif event.key == player.keys[1]:
            player.current_direction = "LEFT"
        elif event.key == player.keys[2]:
            player.current_direction = "DOWN"
        elif event.key == player.keys[3]:
            player.current_direction = "RIGHT"

        if player.current_direction != "":
            message_object = {
                "lastDirection": player.last_direction,
                "type": player.current_direction,
                "currentPositions": player.snake_positions,
            }

            new_message = message.Message(str(uuid.uuid4()), player.name, message_object, "MOVE")
            player.socket.send(json.dumps(new_message.return_dictionary()).encode("utf-8"))

            response = json.loads(player.socket.recv(2048).decode("utf-8"))
            player.snake_positions = response["message"]
            player.last_direction = player.current_direction

def generate_fruits(player):
    generate_fruits_message = message.Message(str(uuid.uuid4()), player.name, "GENERATE_FRUITS", "FRUIT_REQUEST")
    player.socket.send(json.dumps(generate_fruits_message.return_dictionary()).encode("utf-8"))
    response = json.loads(player.socket.recv(2048).decode("utf-8"))

def get_scene_fruits(player):
    global generated_fruits

    get_fruits_message = message.Message(str(uuid.uuid4()), player.name, "GET_FRUITS", "GET_FRUITS")
    player.socket.send(json.dumps(get_fruits_message.return_dictionary()).encode("utf-8"))
    response = json.loads(player.socket.recv(2048).decode("utf-8"))
    generated_fruits = response["message"]
    print(generated_fruits)

def draw_scene(game_screen):
    game_screen.fill((255, 255, 255))
    game_screen.fill((0, 0, 0), (30, 30, game_screen.get_width() - 2 * 30, game_screen.get_height() - 2 * 30))

    for player in players:
        if len(player.snake_positions) == 4:
            for i in range(0, 4):
                pygame.draw.rect(game_screen, player.color,
                                 pygame.Rect(int(player.snake_positions[i].get("x", 0)),
                                             int(player.snake_positions[i].get("y", 0)), 30, 30))

    for i in range(0, len(generated_fruits)):
        pygame.draw.rect(game_screen, (255, 255, 0), pygame.Rect(generated_fruits[i][0], generated_fruits[i][1], 10, 10))

def main():
    game_screen = configure_pygame()

    player1_keys =[pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]
    player2_keys =[pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]

    player1 = Player("player1", "red", "12345", game_screen, player1_keys, "DOWN")
    player2 = Player("player2", "blue", "12345", game_screen, player2_keys, "DOWN")

    players.append(player1)
    players.append(player2)

    player1.connect()
    player2.connect()

    configure_pygame()

    player1.update_function()
    player2.update_function()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_input(game_screen, event)

            if random.random() < 0.05:
                generate_fruits(player1)

            get_scene_fruits(player1)
            draw_scene(game_screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

main()