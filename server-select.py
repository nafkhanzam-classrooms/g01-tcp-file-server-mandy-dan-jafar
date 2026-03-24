import socket
import select
import os

HOST = '127.0.0.1'
PORT = 65432
SERVER_DIR = 'server_files'

# Buat folder penyimpanan server jika belum ada
os.makedirs(SERVER_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

# Set non-blocking agar bisa dipakai oleh select
server.setblocking(False)

# Menyimpan state client
clients = {}
buffers = {}

print(f"[SELECT] {HOST}:{PORT}")

while True:
    # select akan memonitor socket mana yang siap dibaca
    readable, _, _ = select.select([server] + list(clients.keys()), [], [])

    for s in readable:
        if s is server:
            conn, addr = server.accept()
            conn.setblocking(False)
            clients[conn] = {"mode": "cmd"}
            buffers[conn] = b""
            print("[SELECT] connected", addr)

        else:
            # Terima data dari client
            data = s.recv(4096)
            if not data:
                # Terima data dari client
                del clients[s]
                del buffers[s]
                s.close()
                continue

            buffers[s] += data

            # COMMAND MODE
            if clients[s]["mode"] == "cmd":
                if b'\n' not in buffers[s]:
                    continue

                line, buffers[s] = buffers[s].split(b'\n', 1)
                request = line.decode().strip()

                # Command: /list
                if request == 'CMD:LIST':
                    files = os.listdir(SERVER_DIR)
                    s.sendall(f"LIST:{','.join(files)}\n".encode())

                # Command: /upload
                elif request.startswith('CMD:UPLOAD|'):
                    _, name, size = request.split('|')
                    clients[s] = {
                        "mode": "upload",
                        "filename": name,
                        "remaining": int(size),
                        "file": open(os.path.join(SERVER_DIR, name), 'wb')
                    }

                # Command: /download
                elif request.startswith('CMD:DOWNLOAD|'):
                    _, name = request.split('|')
                    path = os.path.join(SERVER_DIR, name)

                    if os.path.exists(path):
                        size = os.path.getsize(path)
                        s.sendall(f"DOWNLOAD:{name}:{size}\n".encode())

                        with open(path, 'rb') as f:
                            while (chunk := f.read(4096)):
                                s.sendall(chunk)
                    else:
                        s.sendall(b"ERR:File tidak ditemukan\n")

                # Broadcast
                elif request.startswith('MSG:'):
                    for c in clients:
                        if c != s:
                            c.sendall(f"MSG:{request[4:]}\n".encode())

            # UPLOAD MODE
            elif clients[s]["mode"] == "upload":
                info = clients[s]
                chunk = buffers[s][:info["remaining"]]

                info["file"].write(chunk)
                info["remaining"] -= len(chunk)
                buffers[s] = buffers[s][len(chunk):]

                if info["remaining"] <= 0:
                    info["file"].close()
                    s.sendall(b"UPLOAD_ACK:OK\n")
                    clients[s] = {"mode": "cmd"}