import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 65432
CLIENT_DIR = 'client_files'

# Buat folder penyimpanan client jika belum ada
os.makedirs(CLIENT_DIR, exist_ok=True)

def receive_handler(sock, reader):
    """Thread background untuk menerima pesan/file dari server."""
    while True:
        try:
            line = reader.readline()
            if not line:
                print("\n[TERPUTUS] Koneksi ditutup oleh server.")
                os._exit(0)
            
            response = line.decode('utf-8').strip()
            
            # Menerima Pesan Broadcast
            if response.startswith('MSG:'):
                print(f"\n{response[4:]}")
            
            # Menerima respon /list
            elif response.startswith('LIST:'):
                files = response[5:].split(',')
                print("\n=== Daftar File di Server ===")
                for f in files:
                    print(f"- {f}")
                print("=============================")
            
            # Menerima respon /download dan memulai proses unduh
            elif response.startswith('DOWNLOAD:'):
                parts = response.split(':')
                filename = parts[1]
                size = int(parts[2])
                
                filepath = os.path.join(CLIENT_DIR, filename)
                received = 0
                print(f"\n[MENGUNDUH] {filename} ({size} bytes)...")
                
                with open(filepath, 'wb') as f:
                    while received < size:
                        chunk = reader.read(min(4096, size - received))
                        if not chunk: break
                        f.write(chunk)
                        received += len(chunk)
                print(f"\n[SUKSES] File tersimpan di direktori '{CLIENT_DIR}/'")
            
            # Menerima respon /upload sukses
            elif response.startswith('UPLOAD_ACK:'):
                print(f"\n[SERVER] {response[11:]}")
            
            # Menerima pesan error
            elif response.startswith('ERR:'):
                print(f"\n[ERROR] {response[4:]}")

            # Tampilkan kembali prompt input setelah mencetak respon
            print("> ", end="", flush=True)

        except Exception as e:
            print(f"\n[ERROR] Thread penerima bermasalah: {e}")
            os._exit(1)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except Exception as e:
        print(f"Gagal terhubung ke server: {e}")
        return

    reader = client.makefile('rb')
    
    # Jalankan thread penerima pesan di background
    recv_thread = threading.Thread(target=receive_handler, args=(client, reader), daemon=True)
    recv_thread.start()

    print("Terhubung ke server TCP!")
    print("Command: /list, /upload <filename>, /download <filename>")
    print("Ketik pesan apa saja dan tekan Enter untuk chat (Broadcast).\n")

    while True:
        try:
            cmd = input("> ")
            if not cmd.strip():
                continue

            if cmd == '/list':
                client.sendall(b"CMD:LIST\n")

            elif cmd.startswith('/upload'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Cara penggunaan: /upload <filename>")
                    continue
                
                filename = parts[1]
                filepath = os.path.join(CLIENT_DIR, filename)
                
                if not os.path.exists(filepath):
                    print(f"File '{filename}' tidak ditemukan di lokal folder '{CLIENT_DIR}/'")
                    continue
                
                # Kirim header upload beserta ukurannya
                size = os.path.getsize(filepath)
                client.sendall(f"CMD:UPLOAD|{filename}|{size}\n".encode('utf-8'))
                
                # Segera setelah header terkirim, kirim raw bytes file-nya
                print(f"[MENGUNGGAH] Mengirim {filename} ke server...")
                with open(filepath, 'rb') as f:
                    while (chunk := f.read(4096)):
                        client.sendall(chunk)

            elif cmd.startswith('/download'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Cara penggunaan: /download <filename>")
                    continue
                
                filename = parts[1]
                client.sendall(f"CMD:DOWNLOAD|{filename}\n".encode('utf-8'))

            else:
                # Anggap teks biasa sebagai pesan chat broadcast
                client.sendall(f"MSG:{cmd}\n".encode('utf-8'))

        except KeyboardInterrupt:
            print("\nMemutus koneksi...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    client.close()

if __name__ == "__main__":
    main()