import cv2

# Coba ganti dengan 0, 1, atau -1
cap = cv2.VideoCapture(0) 

if not cap.isOpened():
    print("Error: Tidak bisa membuka kamera.")
    exit()

while True:
    # Baca frame dari kamera
    ret, frame = cap.read()

    # Jika frame berhasil dibaca
    if not ret:
        print("Error: Tidak bisa menerima frame (stream berakhir?). Keluar ...")
        break

    # Tampilkan frame dalam sebuah jendela
    cv2.imshow('Tes Kamera - Tekan Q untuk Keluar', frame)

    # Tunggu tombol 'q' ditekan untuk keluar
    if cv2.waitKey(1) == ord('q'):
        break

# Lepaskan kamera dan tutup semua jendela
cap.release()
cv2.destroyAllWindows()