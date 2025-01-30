import socket

# Global can sayısı
lives = 3

def udp_server():
    global lives  # Global can değişkenini kullan
    # Server configuration
    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f"Server listening on {host}:{port}")

    # En son gönderilen değerler
    last_sent_seq = None
    last_sent_ack = None
    last_sent_length = None

    # "1" seçimi sayaç
    choice_counter = 0

    while True:
        # İstemciden veri al
        data, addr = server_socket.recvfrom(1024)  # Buffer size is 1024 bytes
        message = data.decode('utf-8')

        if message == "Paket alınamadı":
            print("Client mesajı: Paket alınamadı.")

            while True:
                send_choice = input("Paket gönderilsin mi? (1: Hayır, 'Paket alınamadı' gönder; 2: Evet, SEQ, ACK ve LENGTH gir): ")

                if send_choice == "1":
                    choice_counter += 1
                    if choice_counter >= 4:
                        lives -= 1
                        print(f"4 kez '1' seçildi. Bir can kaybettiniz! Kalan can: {lives}")
                        if lives == 0:
                            print("You lost!")
                            server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                            return
                        continue
                    server_socket.sendto("Paket alınamadı".encode('utf-8'), addr)
                    print("Paket alınamadı mesajı gönderildi.")
                    break
                elif send_choice == "2":
                    choice_counter = 0  # Sayaç sıfırlanır
                    while lives > 0:
                        try:
                            server_seq = int(input("You (Server - SEQ): "))
                            server_ack = int(input("You (Server - ACK): "))
                            server_length = int(input("You (Server - LENGTH): "))

                            expected_seq = last_sent_seq + last_sent_length if last_sent_seq is not None else 0
                            expected_ack = last_sent_ack if last_sent_ack is not None else 0

                            if server_seq != expected_seq or server_ack != expected_ack or server_length <= 0:
                                lives -= 1
                                print(f"Hatalı giriş! Kalan can: {lives}")
                                if lives == 0:
                                    print("You lost!")
                                    server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                                    return
                            else:
                                server_message = f"{server_seq},{server_ack},{server_length}"
                                server_socket.sendto(server_message.encode('utf-8'), addr)
                                last_sent_seq = server_seq
                                last_sent_ack = server_ack
                                last_sent_length = server_length
                                break
                        except ValueError:
                            lives -= 1
                            print(f"Invalid input. Kalan can: {lives}")
                            if lives == 0:
                                print("You lost!")
                                server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                                return
                    break
                else:
                    print("Geçersiz seçim. Lütfen 1 veya 2'yi seçin.")
            continue

        try:
            client_seq, client_ack, client_length = map(int, message.split(','))
        except ValueError:
            print("You won! (Server)")
            server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
            continue

        print(f"Received - SEQ: {client_seq}, ACK: {client_ack}, LENGTH: {client_length}")

        expected_seq = client_ack
        expected_ack = client_seq + client_length

        while True:
            send_choice = input("Paket gönderilsin mi? (1: Hayır, 'Paket alınamadı' gönder; 2: Evet, SEQ, ACK ve LENGTH gir): ")

            if send_choice == "1":
                choice_counter += 1
                if choice_counter >= 4:
                    lives -= 1
                    print(f"4 kez '1' seçildi. Bir can kaybettiniz! Kalan can: {lives}")
                    if lives == 0:
                        print("You lost!")
                        server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                        return
                    continue
                server_socket.sendto("Paket alınamadı".encode('utf-8'), addr)
                print("Paket alınamadı mesajı gönderildi.")
                break
            elif send_choice == "2":
                choice_counter = 0  # Sayaç sıfırlanır
                while lives > 0:
                    try:
                        server_seq = int(input("You (Server - SEQ): "))
                        server_ack = int(input("You (Server - ACK): "))
                        server_length = int(input("You (Server - LENGTH): "))

                        if server_seq != expected_seq or server_ack != expected_ack or server_length <= 0:
                            lives -= 1
                            print(f"Hatalı giriş! Kalan can: {lives}")
                            if lives == 0:
                                print("You lost!")
                                server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                                return
                        else:
                            server_message = f"{server_seq},{server_ack},{server_length}"
                            server_socket.sendto(server_message.encode('utf-8'), addr)
                            last_sent_seq = server_seq
                            last_sent_ack = server_ack
                            last_sent_length = server_length
                            break
                    except ValueError:
                        lives -= 1
                        print(f"Invalid input. Kalan can: {lives}")
                        if lives == 0:
                            print("You lost!")
                            server_socket.sendto("You won! (Client)".encode('utf-8'), addr)
                            return
                break
            else:
                print("Geçersiz seçim. Lütfen 1 veya 2'yi seçin.")

if __name__ == "__main__":
    udp_server()
