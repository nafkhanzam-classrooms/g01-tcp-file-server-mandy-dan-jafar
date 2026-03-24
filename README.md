[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Ja'far Balyan Al Karim  | 5025241040   | D |
| Mandy Alphafyn Imanuel Tjandra  | 5025241173    | D |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```text
[https://youtu.be/](https://youtu.be/)[GANTI_DENGAN_ID_VIDEO_ANDA]
````

## Penjelasan Program

Tugas ini adalah implementasi aplikasi **TCP File Server** berbasis terminal yang mendukung arsitektur *multi-client*. Aplikasi ini mengkombinasikan fitur pertukaran pesan (chat/broadcast) dan transfer file dalam satu koneksi TCP yang sama.

Untuk memisahkan antara teks perintah/chat dengan data mentah (raw bytes) dari file, program ini menggunakan protokol sederhana di mana setiap perintah dikirim sebagai string berakhiran *newline* (`\n`), dan transfer data dilakukan tepat setelah *header* perintah diterima.

Program terdiri dari **satu file client** dan **empat jenis implementasi server** yang berbeda:

### 1\. File Client

  * **`client.py`**: Aplikasi sisi klien yang menggunakan *multithreading* sederhana. Satu *thread* utama menangani input dari pengguna (terminal), sementara satu *thread* berjalan di *background* (`daemon`) untuk terus mendengarkan respon pesan atau kiriman file dari server tanpa memblokir antarmuka input.

### 2\. Implementasi Server

  * **`server-sync.py` (Synchronous)**: Server yang berjalan secara sekuensial (*blocking*). Hanya melayani satu klien pada satu waktu. Jika klien lain mencoba terhubung, koneksinya akan tertahan (*pending*) sampai klien pertama terputus.
  * **`server-thread.py` (Threading)**: Server *multi-client* yang membuat *thread* baru (`threading.Thread`) untuk setiap klien yang terhubung. Sangat responsif namun mengkonsumsi lebih banyak sumber daya jika klien sangat banyak.
  * **`server-select.py` (Select)**: Server *multi-client* berbasis *I/O multiplexing* menggunakan fungsi `select()`. Menggunakan satu *thread* utama yang memonitor banyak *socket* sekaligus secara *non-blocking*. Kompatibel secara lintas *platform* (Windows, macOS, Linux).
  * **`server-poll.py` (Poll)**: Server *multi-client* berbasis *I/O multiplexing* menggunakan *syscall* `poll()`. Lebih efisien dari `select` untuk jumlah koneksi yang sangat besar. **Catatan:** Modul `select.poll()` hanya tersedia di sistem operasi berbasis UNIX (Linux, macOS, atau WSL).

### Fitur yang Didukung

  * **Broadcast Chat**: Mengetikkan teks biasa di terminal klien akan mengirim pesan tersebut ke server, yang kemudian disebarkan (di-broadcast) ke seluruh klien lain yang terhubung.
  * **`/list`**: Menampilkan daftar file yang tersedia di penyimpanan server (`server_files/`).
  * **`/upload <filename>`**: Mengunggah file dari penyimpanan klien (`client_files/`) ke server.
  * **`/download <filename>`**: Mengunduh file dari server dan menyimpannya ke penyimpanan klien lokal.

-----

## Screenshot Hasil

1a. ![sync-Koneksi Multi-Client & Chat Broadcast](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_1/server-sync.png)<br>
1b. ![select-Koneksi Multi-Client & Chat Broadcast](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_1/server-select.png)<br>
1c. ![poll-Koneksi Multi-Client & Chat Broadcast](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_1/server-poll.png)<br>
1d. ![thread-Koneksi Multi-Client & Chat Broadcast](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_1/server-thread.png)<br>
2.  ![Fitur Upload & List](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_2/upload-list.png)<br>
3.  ![Fitur Download](https://github.com/nafkhanzam-classrooms/g01-tcp-file-server-mandy-dan-jafar/blob/JafKrim/image/no_3/download.png)<br>
