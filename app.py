import cv2
import dlib
import numpy as np
import math
import os
import base64
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit

# --- INISIALISASI APLIKASI FLASK ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_flask_app'
socketio = SocketIO(app)

# --- INISIALISASI KAMERA ---
# Coba ganti angka 0 dengan 1 jika kamera default tidak berfungsi
cap = cv2.VideoCapture(0) 
if not cap.isOpened():
    print("FATAL ERROR: Tidak bisa membuka kamera. Pastikan kamera tidak digunakan aplikasi lain.")
    exit()

# --- MEMUAT MODEL DAN GAMBAR (HANYA SEKALI SAAT SERVER START) ---
print("Memuat model dlib...")
if not os.path.exists("shape_predictor_68_face_landmarks.dat"):
    print("FATAL ERROR: File 'shape_predictor_68_face_landmarks.dat' tidak ditemukan.")
    exit()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

print("Memuat gambar kacamata...")
glasses_images = {
    '1': cv2.imread("static/images/glasses1.png", -1),
    '2': cv2.imread("static/images/glasses2.png", -1),
    '3': cv2.imread("static/images/glasses3.png", -1),
    '4': cv2.imread("static/images/glasses4.png", -1)
}

# Cek jika ada gambar yang gagal dimuat
for key, img in glasses_images.items():
    if img is None:
        print(f"FATAL ERROR: Gagal memuat gambar 'glasses{key}.png'. Pastikan file ada di 'static/images/'.")
        exit()

# Variabel global untuk menyimpan pilihan kacamata saat ini
current_glasses_id = '1'

# --- FUNGSI BANTUAN ---
def overlay_image_alpha(img, img_overlay, pos):
    try:
        x, y = pos
        h_overlay, w_overlay, _ = img_overlay.shape
        alpha_mask = img_overlay[:, :, 3] / 255.0
        img_overlay_rgb = img_overlay[:, :, :3]

        y1, y2 = max(0, y), min(img.shape[0], y + h_overlay)
        x1, x2 = max(0, x), min(img.shape[1], x + w_overlay)

        roi = img[y1:y2, x1:x2]
        
        overlay_cut = img_overlay_rgb[0:y2-y1, 0:x2-x1]
        mask_cut = alpha_mask[0:y2-y1, 0:x2-x1]
        mask_cut_bgr = cv2.merge([mask_cut, mask_cut, mask_cut])

        if roi.shape != overlay_cut.shape:
            return

        roi_bg = cv2.multiply(roi.astype(float), 1.0 - mask_cut_bgr)
        roi_fg = cv2.multiply(overlay_cut.astype(float), mask_cut_bgr)
        dst = cv2.add(roi_bg, roi_fg)
        img[y1:y2, x1:x2] = dst.astype(np.uint8)
    except Exception as e:
        print(f"Overlay error: {e}")

def calculate_inclination(point1, point2):
    return math.degrees(math.atan2(point2[1] - point1[1], point2[0] - point1[0]))

def generate_frames():
    """Generator yang membaca dari kamera, memproses, dan menghasilkan frame."""
    global current_glasses_id
    while True:
        success, frame = cap.read()
        if not success:
            print("Gagal membaca frame dari kamera.")
            break
        
        # Logika utama pemrosesan frame
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        
        current_glasses = glasses_images[current_glasses_id]

        for face in faces:
            landmarks = predictor(gray, face)
            left_eye = (landmarks.part(36).x, landmarks.part(36).y)
            right_eye = (landmarks.part(45).x, landmarks.part(45).y)
            
            angle = calculate_inclination(left_eye, right_eye)
            
            glasses_width = int(math.hypot(left_eye[0] - right_eye[0], left_eye[1] - right_eye[1]) * 1.8)
            
            if glasses_width == 0: continue

            scale = glasses_width / current_glasses.shape[1]
            h_orig, w_orig, _ = current_glasses.shape
            center_orig = (w_orig // 2, h_orig // 2)
            rot_mat = cv2.getRotationMatrix2D(center_orig, -angle, 1.0)
            
            cos_val, sin_val = np.abs(rot_mat[0, 0]), np.abs(rot_mat[0, 1])
            new_w = int((h_orig * sin_val) + (w_orig * cos_val))
            new_h = int((h_orig * cos_val) + (w_orig * sin_val))
            
            rot_mat[0, 2] += (new_w / 2) - center_orig[0]
            rot_mat[1, 2] += (new_h / 2) - center_orig[1]

            rotated_glasses = cv2.warpAffine(current_glasses, rot_mat, (new_w, new_h))

            h_rot, w_rot, _ = rotated_glasses.shape
            new_scaled_h = int(h_rot * scale)
            new_scaled_w = int(w_rot * scale)

            if new_scaled_w > 0 and new_scaled_h > 0:
                scaled_rotated_glasses = cv2.resize(rotated_glasses, (new_scaled_w, new_scaled_h), interpolation=cv2.INTER_AREA)
                
                eye_center_x = (left_eye[0] + right_eye[0]) // 2
                eye_center_y = (left_eye[1] + right_eye[1]) // 2
                
                pos_x = eye_center_x - (new_scaled_w // 2)
                pos_y = eye_center_y - (new_scaled_h // 2)
                
                overlay_image_alpha(frame, scaled_rotated_glasses, (pos_x, pos_y))
        
        # Encode frame ke JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Hasilkan (yield) frame untuk streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- ROUTE DAN WEBSOCKET ---
@app.route('/')
def index():
    """Menyajikan halaman utama."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Endpoint untuk streaming video."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('change_glasses')
def handle_change_glasses(data):
    """Mengubah model kacamata yang digunakan."""
    global current_glasses_id
    glasses_id = data.get('id')
    if glasses_id in glasses_images:
        current_glasses_id = glasses_id
        print(f"Kacamata diubah ke model: {glasses_id}")

if __name__ == '__main__':
    print("Server Flask dimulai. Buka http://127.0.0.1:5000 di browser Anda.")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
