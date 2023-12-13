import socket
import threading
import time
import subprocess

mensajes_para_guardar = []
base_de_datos = {}
votos_recibidos = {}

def obtener_direccion_ip(interface):
    try:
        resultado = subprocess.check_output(['ip', 'addr', 'show', interface]).decode('utf-8')

        for linea in resultado.split('\n'):
            if 'inet' in linea:
                partes = linea.strip().split()
                inet_index = partes.index('inet')
                direccion_ip = partes[inet_index + 1].split('/')[0]
                return direccion_ip

    except subprocess.CalledProcessError:
        return "\n No se pudo obtener la dirección IP"

def revisar_mensaje(mensaje):
    # Agrega aquí la lógica para revisar si el mensaje contiene comandos específicos
    comandos_permitidos = ["Add", "Drop", "Edit"]
    for comando in comandos_permitidos:
        if comando.lower() in mensaje.lower():
            return f"\n ADVERTENCIA: El mensaje contiene el comando '{comando}'."
    return ""

def recibir_mensajes():
    mensaje_confirmado = False
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            mensaje_decodificado = mensaje_recibido.decode('utf-8')
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            advertencia = revisar_mensaje(mensaje_decodificado)
            if advertencia:
                print(advertencia)

            mensaje_completo = f"\n {timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
            mensajes_para_guardar.append(mensaje_completo)

            # Inicia el proceso de votación
            if mensaje_decodificado not in votos_recibidos:
                votos_recibidos[mensaje_decodificado] = 1
            else:
                votos_recibidos[mensaje_decodificado] += 1

                # Verifica si se alcanzó la mayoría de votos
                if votos_recibidos[mensaje_decodificado] >= len(NODOS) // 2 + 1:
                    aplicar_cambio(mensaje_decodificado)
                    votos_recibidos.clear()

            if not mensaje_confirmado:
                confirmacion = "\n Confirmo la recepcion de tu mensaje"
                s.sendto(confirmacion.encode('utf-8'), direccion)
                print(mensaje_completo)
                mensaje_confirmado = True
        except socket.timeout:
            mensaje_confirmado = False

def aplicar_cambio(mensaje):
    # Implementa aquí la lógica para aplicar el cambio en la base de datos
    print(f"\n Cambio aplicado en la base de datos: {mensaje}")
    base_de_datos["comando"] = mensaje

def guardar_mensajes():
    while True:
        if mensajes_para_guardar:
            mensaje_para_guardar = mensajes_para_guardar.pop(0)
            with open("logMensajes.txt", "a") as log_file:
                log_file.write(mensaje_para_guardar + "\n")
            time.sleep(1)

def enviar_mensajes():
    ultima_destino_ip = ""
    
    while True:
        # Solicitar la dirección IP solo una vez antes del bucle del mensaje
        destino_ip = input(f"\n Ingrese la dirección IP de destino (o presione Enter para usar la última: {ultima_destino_ip}): ")
        if not destino_ip:
            destino_ip = ultima_destino_ip

        # Validar la dirección IP
        while True:
            if destino_ip.count('.') == 3 and all(0 <= int(num) < 256 for num in destino_ip.rstrip().split('.')):
                break
            else:
                print("\n Dirección IP no válida. Ingrese una dirección IP válida.")
                destino_ip = input("\n Ingrese la dirección IP de destino: ")

        # Actualizar la última dirección IP utilizada
        ultima_destino_ip = destino_ip

        # Validar el mensaje
        mensaje = input("\n Ingrese su mensaje: ")
        while not mensaje.strip():
            print("\n El mensaje no puede estar vacío.")
            mensaje = input("\n Ingrese su mensaje: ")

        advertencia = revisar_mensaje(mensaje)
        if advertencia:
            print(advertencia)

        timestamp = time.strftime("\n %Y-%m-%d %H:%M:%S", time.localtime())
        mensaje_completo = f"\n {timestamp} - Mensaje ENVIADO a {destino_ip}: {mensaje}"
        
        destino_puerto = 12345
        s.sendto(mensaje.encode('utf-8'), (destino_ip, destino_puerto))
        mensajes_para_guardar.append(mensaje_completo)

NODOS = ["192.168.242.129", "192.168.242.130"]  # Agrega aquí las direcciones IP de los nodos
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)

if mi_ip:
    print(f"\n La dirección IP (inet) de la interfaz {interfaz} es: {mi_ip}")
else:
    print("\n No se pudo obtener la dirección IP.")
mi_puerto = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(1)

thread_recibir = threading.Thread(target=recibir_mensajes)
thread_enviar = threading.Thread(target=enviar_mensajes)
thread_guardar = threading.Thread(target=guardar_mensajes)

thread_recibir.daemon = True
thread_enviar.daemon = True
thread_guardar.daemon = True

thread_recibir.start()
thread_enviar.start()
thread_guardar.start()

while True:
    pass
