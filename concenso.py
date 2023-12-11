import socket
import threading
import pickle

class ConsensusNode:
    def __init__(self, node_id, port, initial_data):
        self.node_id = node_id
        self.port = port
        self.data = initial_data
        self.peers = [("localhost", p) for p in range(8000, 8005) if p != port]
        self.current_command = None

    def start(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()
        self.run()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.port))
        server.listen(5)
        while True:
            client, addr = server.accept()
            data = client.recv(1024)
            if data:
                command = pickle.loads(data)
                self.handle_command(command)
            client.close()

    def run(self):
        while True:
            # Aquí puedes solicitar al usuario que ingrese el comando de actualización
            update_command = {"101": {"cantidad": 55}, "102": {"precio": 1100}}
            self.broadcast_command(update_command)

    def broadcast_command(self, command):
        self.current_command = command
        for peer in self.peers:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            client.sendall(pickle.dumps(command))
            client.close()

    def handle_command(self, command):
        print(f"Node {self.node_id} applying command: {command}")
        for item_id, update_data in command.items():
            if item_id in self.data:
                self.data[item_id].update(update_data)

if __name__ == "__main__":
    initial_data = {
        "101": {"articulo": "Playera", "categoria": "Ropa", "precio": 500, "cantidad": 50, "Inv1": 0, "Inv2": 0, "Inv3": 0, "Inv4": 0, "Inv5": 0},
        # ... (otros artículos)
    }

    nodes = [ConsensusNode(i, 8000 + i, initial_data.copy()) for i in range(5)]

    for node in nodes:
        node.start()
