import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3

def countdown(engine, seconds):
    """Geri sayım yapar, ekranda gösterir ve sesli komut verir."""
    for i in range(seconds, 0, -1):
        # Siyah bir ekran oluştur
        frame = np.zeros((400, 800, 3), dtype=np.uint8)
        
        # Geri sayım sayısını ekrana yaz
        cv2.putText(frame, f"{i}", (350, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 10, cv2.LINE_AA)
        cv2.putText(frame, "Hazir olun!", (200, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Görüntüyü göster
        cv2.imshow('Geri Sayim', frame)
        
        # Sesli olarak sayıyı söyle
        engine.say(str(i))
        engine.runAndWait()
        
        # 1 saniye bekle
        time.sleep(1)

        # 'q' tuşuna basılırsa çık
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Geri sayım penceresini kapat
    cv2.destroyWindow('Geri Sayim')

def calculate_angle(a, b, c):
    """Üç nokta arasındaki açıyı hesaplar."""
    a = np.array(a)  # Omuz noktası
    b = np.array(b)  # Dirsek noktası
    c = np.array(c)  # El noktası

    # Vektörleri hesapla
    ab = a - b
    cb = c - b

    # Açı hesapla
    radians = np.arccos(
        np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    )
    angle = np.degrees(radians)

    return angle

# Text-to-Speech (TTS) motorunu başlat
engine = pyttsx3.init()

# MediaPipe kurulumları
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Kamera başlatma
cap = cv2.VideoCapture(0)

# Geri sayım ve hazırlık mesajı
engine.say("Hazır olun. Beşten geriye sayıyoruz.")
engine.runAndWait()
countdown(engine, 5)

start_time = time.time()
correct_count = 0
total_count = 0
full_repeats = 0
previous_angle = None
is_moving_up = False
fps_limit = 0.05  # Döngü başına minimum 50ms bekleme

# Sesli komut durumunu kontrol etmek için bayrak
last_command = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Kamera açılamadı!")
        break

    # Görüntüyü RGB'ye dönüştür
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Poz algılama ve çizim
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        # Anahtar noktaları al
        landmarks = results.pose_landmarks.landmark

        # Sağ kol noktalarını al
        shoulder = [
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y,
        ]
        elbow = [
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y,
        ]
        wrist = [
            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y,
        ]

        # Açı hesapla
        angle = calculate_angle(shoulder, elbow, wrist)

        # Açıyı ekrana yazdır
        cv2.putText(
            frame,
            f"Aci: {int(angle)}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Egzersiz doğruluğunu kontrol et
        if 80 <= angle <= 100:
            correct_count += 1
            cv2.putText(
                frame,
                "Dogru Pozisyon",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            if last_command != "correct":
                engine.say("Doğru pozisyon")
                engine.runAndWait()
                last_command = "correct"
        else:
            cv2.putText(
                frame,
                "Hatali Pozisyon",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            if last_command != "incorrect":
                engine.say("Hatalı pozisyon")
                engine.runAndWait()
                last_command = "incorrect"
        total_count += 1

        # Tam hareket algılama
        if previous_angle is not None:
            if angle > 100 and not is_moving_up:
                is_moving_up = True
            elif angle < 80 and is_moving_up:
                is_moving_up = False
                full_repeats += 1

        previous_angle = angle

    # Görüntüyü göster
    cv2.imshow('Egzersiz Takip Sistemi', frame)

    # Döngü hızını sınırlamak için bekleme
    time.sleep(fps_limit)

    # 15 saniye sonra çıkış yap
    if time.time() - start_time > 15:
        break

    # 'q' tuşuna basıldığında çıkış
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Kamera temizleme
cap.release()
cv2.destroyAllWindows()

# Sonuçları hesapla
accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
result_text = (
    f"Toplam Kare: {total_count}\n"
    f"Dogru Pozisyon Kareleri: {correct_count}\n"
    f"Tam Hareketler: {full_repeats}\n"
    f"Basari Orani: {accuracy:.2f}%"
)

# Sonuçları yeni bir ekranda göster
result_frame = np.zeros((400, 800, 3), dtype=np.uint8)
cv2.putText(result_frame, "Sonuclar:", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(result_frame, f"Toplam Kare: {total_count}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(result_frame, f"Dogru Pozisyon Kareleri: {correct_count}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(result_frame, f"Tam Hareketler: {full_repeats}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(result_frame, f"Basari Orani: {accuracy:.2f}%", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
cv2.putText(result_frame, "Cikis icin 'q'ya basin", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

while True:
    cv2.imshow('Sonuclar', result_frame)
    # 'q' tuşu ile çıkış
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
