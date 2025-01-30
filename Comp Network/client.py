import socket

# Global can sayısı
lives = 3

def udp_client():
    global lives  # Global can değişkenini kullan
    server_host = "127.0.0.1"
    server_port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (server_host, server_port)

    # İlk değerler
    last_sent_seq = None
    last_sent_ack = None
    last_sent_length = None

    # "1" seçimi sayaç
    choice_counter = 0

    # İlk mesaj
    while True:
        try:
            last_sent_seq = int(input("You (Client - Initial SEQ): "))
            last_sent_ack = int(input("You (Client - Initial ACK): "))
            last_sent_length = int(input("You (Client - Initial LENGTH): "))
            client_message = f"{last_sent_seq},{last_sent_ack},{last_sent_length}"
            break
        except ValueError:
            print("Invalid input. Enter numeric values for SEQ, ACK, and LENGTH.")

    client_socket.sendto(client_message.encode('utf-8'), server_address)

    while True:
        # Sunucudan yanıt alınması
        data, _ = client_socket.recvfrom(1024)
        server_response = data.decode('utf-8')
        print(f"Server: {server_response}")

        # "Paket alınamadı" kontrolü
        if server_response == "Paket alınamadı":
            print("Server returned: Paket alınamadı.")

            while True:
                send_choice = input("Paket gönderilsin mi? (1: Hayır, 'Paket alınamadı' gönder; 2: Evet, SEQ, ACK ve LENGTH gir): ")

                if send_choice == "1":
                    choice_counter += 1
                    if choice_counter >= 4:
                        lives -= 1
                        print(f"4 kez '1' seçildi. Bir can kaybettiniz! Kalan can: {lives}")
                        if lives == 0:
                            print("You lost!")
                            client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                            return
                        continue
                    client_socket.sendto("Paket alınamadı".encode('utf-8'), server_address)
                    print("Paket alınamadı mesajı gönderildi.")
                    break
                elif send_choice == "2":
                    choice_counter = 0  # Sayaç sıfırlanır
                    while lives > 0:
                        try:
                            client_seq = int(input("You (Client - SEQ): "))
                            client_ack = int(input("You (Client - ACK): "))
                            client_length = int(input("You (Client - LENGTH): "))

                            expected_seq = last_sent_seq + last_sent_length
                            expected_ack = last_sent_ack

                            if client_seq != expected_seq or client_ack != expected_ack or client_length <= 0:
                                lives -= 1
                                print(f"Hatalı giriş! Kalan can: {lives}")
                                if lives == 0:
                                    print("You lost!")
                                    client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                                    return
                            else:
                                client_message = f"{client_seq},{client_ack},{client_length}"
                                client_socket.sendto(client_message.encode('utf-8'), server_address)
                                last_sent_seq = client_seq
                                last_sent_ack = client_ack
                                last_sent_length = client_length
                                break
                        except ValueError:
                            lives -= 1
                            print(f"Invalid input. Kalan can: {lives}")
                            if lives == 0:
                                print("You lost!")
                                client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                                return
                    break
                else:
                    print("Geçersiz seçim. Lütfen 1 veya 2'yi seçin.")
            continue

        if "won" in server_response.lower() or "lost" in server_response.lower():
            break

        # Gelen yanıtın işlenmesi
        try:
            server_seq, server_ack, server_length = map(int, server_response.split(','))
        except ValueError:
            print(f"Invalid response from server: {server_response}")
            break

        print(f"Server Sent - SEQ: {server_seq}, ACK: {server_ack}, LENGTH: {server_length}")

        expected_seq = server_ack
        expected_ack = server_seq + server_length

        while True:
            send_choice = input("Paket gönderilsin mi? (1: Hayır, 'Paket alınamadı' gönder; 2: Evet, SEQ, ACK ve LENGTH gir): ")

            if send_choice == "1":
                choice_counter += 1
                if choice_counter >= 4:
                    lives -= 1
                    print(f"4 kez '1' seçildi. Bir can kaybettiniz! Kalan can: {lives}")
                    if lives == 0:
                        print("You lost!")
                        client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                        return
                    continue
                client_socket.sendto("Paket alınamadı".encode('utf-8'), server_address)
                print("Paket alınamadı mesajı gönderildi.")
                break
            elif send_choice == "2":
                choice_counter = 0  # Sayaç sıfırlanır
                while lives > 0:
                    try:
                        client_seq = int(input("You (Client - SEQ): "))
                        client_ack = int(input("You (Client - ACK): "))
                        client_length = int(input("You (Client - LENGTH): "))

                        if client_seq != expected_seq or client_ack != expected_ack or client_length <= 0:
                            lives -= 1
                            print(f"Hatalı giriş! Kalan can: {lives}")
                            if lives == 0:
                                print("You lost!")
                                client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                                return
                        else:
                            client_message = f"{client_seq},{client_ack},{client_length}"
                            client_socket.sendto(client_message.encode('utf-8'), server_address)
                            last_sent_seq = client_seq
                            last_sent_ack = client_ack
                            last_sent_length = client_length
                            break
                    except ValueError:
                        lives -= 1
                        print(f"Invalid input. Kalan can: {lives}")
                        if lives == 0:
                            print("You lost!")
                            client_socket.sendto("You won! (Server)".encode('utf-8'), server_address)
                            return
                break
            else:
                print("Geçersiz seçim. Lütfen 1 veya 2'yi seçin.")

if __name__ == "__main__":
    udp_client()
