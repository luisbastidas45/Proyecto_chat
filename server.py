import socket   
import threading


host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((host, port))
server.listen()
print(f"Server running on {host}:{port}")


clients = []
usernames = []

#Funcion que envía el mensaje a todos los clientes
def broadcast(message):
    for client in clients:
        client.send(message)

#Funcion que recibe el mensaje y ordena hacer broadcast
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{usernames[clients.index(client)]} says {message}")
            broadcast(message)
        #Si el cliente se desconecta, se elimina de la lista de clientes junto con su username
        except:
            index = client.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            usernames.remove(username)
            break


def receive():
    while True:
        #Se conecta con el cliente
        client, address = server.accept()
        print(f"Conectado con {str(address)}!")
        #Le envia al cliente la peticion de obtener USERNAME
        client.send("USERNAME".encode("utf-8"))
        username = client.recv(1024)
        # Agrega el cliente y username a la lista
        clients.append(client)
        usernames.append(username)

        print(f"Username del cliente es {username}")
        # Le avisa a todos los clientes quien se sonecto al servidor
        broadcast(f"{username.decode()} conectado con el servidor!\n".encode('utf-8'))
        client.send("Conectado con el servidor!\n".encode('utf-8'))
        #Crea un hilo y  manda a ejecutar handle
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Servidor ejecutandose....")
receive()

