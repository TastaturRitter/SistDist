import socket
import threading
import time
import subprocess

mensajes_para_guardar = []

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

def limpiar_buffer():
    try:
        import msvcrt  # Para sistemas Windows
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys
        import termios  # Para sistemas Unix (Linux/macOS)
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def recibir_mensajes():
    mensaje_confirmado = False
    while True:
        try:
            mensaje_recibido, direccion = s.recvfrom(1024)
            mensaje_decodificado = mensaje_recibido.decode('utf-8')
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            mensaje_completo = f"\n{timestamp} - Mensaje RECIBIDO de {direccion}: {mensaje_decodificado}"
            mensajes_para_guardar.append(mensaje_completo)
            print("mensaje guardado:", mensaje_completo)
            
            if not mensaje_confirmado:
                confirmacion = "\nConfirmo la recepción de tu mensaje"
                s.sendto(confirmacion.encode('utf-8'), direccion)
                print(mensaje_completo)
                mensaje_confirmado = True
        except socket.timeout:
            mensaje_confirmado = False

def guardar_mensajes():
    while True:
        if mensajes_para_guardar:
            mensaje_para_guardar = mensajes_para_guardar.pop(0)
            with open("\nlogMensajes.txt", "a") as log_file:
                log_file.write(mensaje_para_guardar + "\n")
            time.sleep(1)

def enviar_mensajes():
    while True:
        destino_ip = input("\nIngrese la dirección IP de destino: ")
        
        mensaje = ""
        while True:
            caracter = input("Ingrese su mensaje (presione Enter para enviar): ")
            if not caracter:
                break
            mensaje += caracter + "\n"

        timestamp = time.strftime("\n%Y-%m-%d %H:%M:%S", time.localtime())
        mensaje_completo = f"{timestamp} - Mensaje ENVIADO a {destino_ip}:\n{mensaje}"
        
        destino_puerto = 12345
        s.sendto(mensaje_completo.encode('utf-8'), (destino_ip, destino_puerto))
        mensajes_para_guardar.append(mensaje_completo)

        limpiar_buffer()

# Configuración de la dirección y el puerto en esta máquina virtual
interfaz = "ens33"
mi_ip = obtener_direccion_ip(interfaz)
if mi_ip:
    print(f"\nLa dirección IP (inet) de la interfaz {interfaz} es: {mi_ip}")
else:
    print("\nNo se pudo obtener la dirección IP.")
mi_puerto = 12345 

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((mi_ip, mi_puerto))
s.settimeout(1)

# Creación de hilos para recibir, enviar y guardar mensajes
thread_recibir = threading.Thread(target=recibir_mensajes)
thread_enviar = threading.Thread(target=enviar_mensajes)
thread_guardar = threading.Thread(target=guardar_mensajes)

# Ejecución en segundo plano
thread_recibir.daemon = True
thread_enviar.daemon = True
thread_guardar.daemon = True

# Inicialización de los hilos
thread_recibir.start()
thread_enviar.start()
thread_guardar.start()

# El programa principal no hace nada más que esperar
while True:
    pass
