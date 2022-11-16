import socket   
import threading
import tkinter
from tkinter import simpledialog
from tkinter import filedialog
import tkinter.scrolledtext
from tkinter import filedialog
import pymysql
import time


connection = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "",
    db = "clientes" #nombr de base de datos
)
cursor = connection.cursor()

#host y puerto del cliente
HOST = '127.0.0.1'
PORT = 55555



class Client:

    def __init__(self, host, port,nombre):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        #Crea la ventana que se usara como interfaz grafica
        msg = tkinter.Tk()
        msg.withdraw()

        print("bienvenido: ",nombre)
        #self.username = simpledialog.askstring("Username",nombre,parent = msg)
        self.username = nombre

        self.gui_done = False
        self.running = True

        #Inicia el hilo y manda a ejecutar la funcion receive
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.gui_loop()
        
    #Construye la interfaz gráfica
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)
        

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

      
    # Lee el mensaje y lo envia al servidor
    def write(self):
        message = f"{self.username}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    #Destruye la ventana
    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    #Envia el username al servidor o envia el texto
    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == "USERNAME":
                    self.sock.send(self.username.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

def main():

    print("1. Iniciar sesion")
    print("2. Registrarse")
    opcion = input("ingrese una opcion: ")
    print("\n")

    if opcion == "1":
        login = input("ingrese una cuenta de acceso: ")
        password = input("Agregue una contraseña: ")

        sql = f'SELECT login_cl,password_cl,nombre_cl FROM informacion where login_cl = "{login}" '
        cursor.execute(sql)
        r = cursor.fetchall()  #en r se almaceno el valr que llega de la base de datos

        if r == ():
            print("El usuario no se encuentra en la base de datos...\n")
            time.sleep(4)
            main()
        else:
            if r[0][0] == login and r[0][1] == password:
                nombre = r[0][2]
                client = Client(HOST,PORT,nombre)
            else:
                print("Datos incorrectos...\n")
                time.sleep(4)
                main()
    
    if opcion == "2":
        nombre = input("Ingrese su nombre: ")
        apellido = input("Ingrese su apellido: ")
        login = input("ingrese una cuenta de acceso: ")
        password = input("Agregue una contraseña: ")
        edad = input("Ingrese su edad: ")
        genero = input("Ingrese su genero: ")

        sql = "INSERT INTO informacion(nombre_cl,apellido_cl,login_cl,password_cl,edad_cl,genero_cl) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (nombre,apellido,login,password,edad,genero)

        cursor.execute(sql,val)
        connection.commit()

        print("Usuario registrado...\n")
        time.sleep(4)
        client = Client(HOST,PORT,nombre)

main()


