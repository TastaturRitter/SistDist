import socket
import threading
import pickle

class ConsensusNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.data = {}  # Base de datos del nodo
        self.peers = [("localhost", p) for p in range(8000, 8005) if p != port]
        self.current_command = None

    def start(self):
        # Iniciar servidor en un hilo separado
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

        # Iniciar loop principal para manejar comandos
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
            command = input(f"Node {self.node_id}: Enter command ('exit' to quit): ")
            if command == 'exit':
                break

            # Envía el comando a todos los nodos
            self.broadcast_command(command)

            # Espera a que todos los nodos confirmen el comando
            consensus_reached = self.wait_for_consensus()

            if consensus_reached:
                print(f"Consensus reached. Command '{command}' applied to all nodes.")
            else:
                print("Consensus not reached. Retrying...")

    def broadcast_command(self, command):
        self.current_command = command
        for peer in self.peers:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(peer)
            client.sendall(pickle.dumps(command))
            client.close()

    def handle_command(self, command):
        # Aplica el comando a la base de datos local
        # Aquí deberías implementar la lógica específica para tu aplicación
        print(f"Node {self.node_id} applying command: {command}")
        self.data = command

    def wait_for_consensus(self):
        # Espera a que todos los nodos confirmen el comando
        while True:
            if all(self.current_command == node.data for node in self.get_other_nodes()):
                return True

    def get_other_nodes(self):
        # Devuelve todos los nodos excepto el actual
        return [node for node in nodes if node.node_id != self.node_id]

if __name__ == "__main__":
    nodes = [ConsensusNode(i, 8000 + i) for i in range(5)]

    for node in nodes:
        node.start()
