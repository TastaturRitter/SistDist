import socket
import threading

def nodo(ip, puerto):
    nodo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nodo_socket.bind((ip, puerto))
    nodo_socket.listen(5)

    while True:
        client_socket, client_address = nodo_socket.accept()
        print(f"Conexión establecida con {client_address}")

        # Recibe datos del nodo remoto
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Mensaje recibido de {client_address}: {data}")

        # Puedes almacenar o procesar el mensaje aquí según tus necesidades

        # Envía una respuesta al nodo remoto
        response = "Mensaje recibido correctamente"
        client_socket.send(response.encode('utf-8'))

        # Cierra la conexión con el nodo remoto
        client_socket.close()

def comunicacion_con_nodos(ip_destino, puerto_destino, mensaje):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_destino, puerto_destino))

    # Envía el mensaje al nodo remoto
    client_socket.send(mensaje.encode('utf-8'))

    # Recibe la respuesta del nodo remoto
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Respuesta del nodo remoto: {response}")

    # Cierra la conexión con el nodo remoto
    client_socket.close()

if __name__ == "__main__":
    # Configuración de nodos
    nodos = [
        {"ip": "192.168.242.129", "puerto": 5001},
        #{"ip": "192.168.0.102", "puerto": 5002},
        #{"ip": "192.168.0.103", "puerto": 5003},
        #{"ip": "192.168.0.104", "puerto": 5004}
    ]

    # Inicia un hilo para cada nodo
    for nodo_info in nodos:
        threading.Thread(target=nodo, args=(nodo_info["ip"], nodo_info["puerto"])).start()

    # Ejemplo de comunicación entre nodos
    nodo_origen = {"ip": "192.168.0.101", "puerto": 5001}
    for nodo_destino in nodos:
        if nodo_destino != nodo_origen:
            mensaje = f"Hola desde {nodo_origen['ip']}:{nodo_origen['puerto']}"
            threading.Thread(target=comunicacion_con_nodos, args=(nodo_destino["ip"], nodo_destino["puerto"], mensaje)).start()
