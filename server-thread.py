import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 65432
SERVER_DIR = 'server_files'

# Buat folder penyimpanan server jika belum ada
os.makedirs(SERVER_DIR, exist_ok=True)

# List untuk menyimpan semua client yang terhubung
clients = []
lock = threading.Lock()

def broadcast(msg, sender=None):
    # Mengirim pesan ke semua client kecuali pengirim.
    # Karena menggunakan banyak thread, perlu lock agar aman.
    with lock:
        for c in clients:
            if c != sender:
                try: c.sendall(msg)
                except: pass

def handle_client(conn, addr):
    print(f"[THREAD] {addr} connected")
    # Fungsi untuk menangani satu client.
    # Setiap client berjalan di thread terpisah.
    reader = conn.makefile('rb')

    # Tambahkan client ke list global
    with lock:
        clients.append(conn)

    try:
        while True:
            line = reader.readline()
            if not line: break
            request = line.decode().strip()

            # Command: /list
            if request == 'CMD:LIST':
                files = os.listdir(SERVER_DIR)
                file_str = ",".join(files) if files else "Tidak ada file"
                conn.sendall(f"LIST:{file_str}\n".encode())

            # Command: /upload
            elif request.startswith('CMD:UPLOAD|'):
                _, filename, size = request.split('|')
                size = int(size)
                path = os.path.join(SERVER_DIR, filename)

                with open(path, 'wb') as f:
                    received = 0
                    while received < size:
                        chunk = reader.read(min(4096, size - received))
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)

                conn.sendall(b"UPLOAD_ACK:OK\n")

            # Command: /download
            elif request.startswith('CMD:DOWNLOAD|'):
                _, filename = request.split('|')
                path = os.path.join(SERVER_DIR, filename)

                if os.path.exists(path):
                    size = os.path.getsize(path)
                    conn.sendall(f"DOWNLOAD:{filename}:{size}\n".encode())

                    with open(path, 'rb') as f:
                        while (chunk := f.read(4096)):
                            conn.sendall(chunk)
                else:
                    conn.sendall(b"ERR:File tidak ditemukan\n")

            # Broadcast
            elif request.startswith('MSG:'):
                msg = request[4:]
                broadcast(f"MSG:[{addr}] {msg}\n".encode(), conn)

    finally:
        # Hapus client saat disconnect
        with lock:
            clients.remove(conn)
        conn.close()
        print(f"[THREAD] {addr} disconnected")

def main():
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen()
    print(f"[THREAD] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        # Setiap client dibuatkan thread baru
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

main()