class Message:
    def __init__(self, message_id, player, message, message_type):
        self.player = player
        self.message = message
        self.id = message_id
        self.type = message_type

    def display_message(self):
        print(self.player)
        print(self.message)
        print(self.id)
        print(self.type)

    def return_dictionary(self):
        return {"id": self.id, "type": self.type, "message": self.message, "player": self.player}