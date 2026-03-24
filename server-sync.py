import socket
import os

HOST = '127.0.0.1'
PORT = 65432
SERVER_DIR = 'server_files'

# Buat folder penyimpanan server jika belum ada
os.makedirs(SERVER_DIR, exist_ok=True)

def handle_client(conn, addr):
    print(f"\n[KONEKSI BARU] {addr} terhubung.")
    # Menggunakan makefile agar kita bisa membaca per baris (readline)
    # Ini sangat penting agar kita tidak kebablasan membaca raw bytes dari file
    reader = conn.makefile('rb')
    
    while True:
        try:
            line = reader.readline()
            if not line:
                break # Client terputus
            
            request = line.decode('utf-8').strip()
            if not request:
                continue

            # Command: /list
            if request == 'CMD:LIST':
                files = os.listdir(SERVER_DIR)
                file_str = ",".join(files) if files else "Tidak ada file di server."
                conn.sendall(f"LIST:{file_str}\n".encode('utf-8'))

            # Command: /upload
            elif request.startswith('CMD:UPLOAD|'):
                parts = request.split('|')
                filename = parts[1]
                size = int(parts[2])
                
                filepath = os.path.join(SERVER_DIR, filename)
                received = 0
                print(f"[MENERIMA FILE] {filename} ({size} bytes)...")
                
                with open(filepath, 'wb') as f:
                    while received < size:
                        # Baca data sesuai ukuran yang tersisa
                        chunk = reader.read(min(4096, size - received))
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)
                
                conn.sendall(b"UPLOAD_ACK:File berhasil diunggah ke server.\n")
                print(f"[SELESAI] File {filename} disimpan.")

            # Command: /download
            elif request.startswith('CMD:DOWNLOAD|'):
                parts = request.split('|')
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)
                
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    # Kirim header download ke client
                    conn.sendall(f"DOWNLOAD:{filename}:{size}\n".encode('utf-8'))
                    
                    # Kirim raw bytes file
                    with open(filepath, 'rb') as f:
                        while (chunk := f.read(4096)):
                            conn.sendall(chunk)
                    print(f"[MENGIRIM FILE] {filename} terkirim ke client.")
                else:
                    conn.sendall(f"ERR:File '{filename}' tidak ditemukan di server.\n".encode('utf-8'))

            # Pesan Chat Biasa
            elif request.startswith('MSG:'):
                msg = request[4:]
                # Karena ini server sinkron (1 client aktif), broadcast = memantulkan kembali ke client
                # Pada server-select/thread, Anda akan meloop list semua connected clients di sini.
                conn.sendall(f"MSG:[Broadcast] {msg}\n".encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] {addr}: {e}")
            break

    print(f"[TERPUTUS] {addr} telah keluar.")
    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Izinkan port langsung digunakan ulang setelah server mati
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server SINKRON berjalan di {HOST}:{PORT}")
    print("Menunggu client...")
    
    while True:
        conn, addr = server.accept()
        # Menangani 1 client secara blocking (sinkron)
        handle_client(conn, addr)

if __name__ == "__main__":
    main()