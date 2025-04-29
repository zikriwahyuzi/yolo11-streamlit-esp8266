import cv2
import streamlit as st
from ultralytics import YOLO
import requests
import time  # Untuk pengaturan jeda waktu

# Load YOLO model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Fungsi untuk mengirim sinyal ke NodeMCU
def send_to_nodemcu(action):
    url = f"http://192.168.148.41/{action}"  # Ganti dengan IP NodeMCU Anda
    try:
        requests.get(url, timeout=3)  # Timeout diatur menjadi 3 detik
    except requests.exceptions.RequestException as e:
        st.error(f"Kesalahan koneksi ke NodeMCU: {e}")

# Proses hasil deteksi (hanya untuk "person")
def detect_person(image, results):
    boxes = results.boxes.xyxy.cpu().numpy()
    scores = results.boxes.conf.cpu().numpy()
    labels = results.boxes.cls.cpu().numpy()
    names = results.names
    
    orang_terdeteksi = False
    jumlah_orang = 0  # Variabel untuk jumlah orang yang terdeteksi

    for i in range(len(boxes)):
        if scores[i] > 0.4:  # Confidence threshold
            label = names[int(labels[i])]
            if label == "person":  # Fokus hanya pada "person"
                x1, y1, x2, y2 = boxes[i].astype(int)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"{label}: {scores[i]:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                orang_terdeteksi = True
                jumlah_orang += 1  # Hitung jumlah "person" yang terdeteksi
    
    return image, orang_terdeteksi, jumlah_orang

# Aplikasi Streamlit
def main():
    st.title("Deteksi Objek YOLOv11 x IoT")
    st.sidebar.title("Pengaturan")
    
    model_path = "yolo11n.pt"  # Path ke YOLO model
    model = load_model(model_path)

    # Pilih salah satu dari dua kamera yang tersedia
    st.sidebar.markdown("### Pilih Kamera")
    available_cameras = [0, 1]  # Daftar kamera yang tersedia (indeks)
    selected_camera = st.sidebar.radio("Pilih Kamera", options=available_cameras, format_func=lambda x: f"Kamera {x}")

    st.sidebar.write(f"Kamera yang digunakan: Kamera {selected_camera}")

    # Tombol start/stop
    run_detection = st.sidebar.checkbox("Mulai/Pause Deteksi Objek", key="detection_control")

    # Placeholder untuk tampilan kamera dan deteksi
    st_frame = st.empty()
    st.sidebar.markdown("### Informasi Deteksi")
    detection_info_placeholder = st.sidebar.empty()

    # Variabel untuk melacak status lampu sebelumnya dan waktu jeda
    previous_orang_terdeteksi = False
    waktu_terakhir_terdeteksi = None  # Untuk menyimpan waktu terakhir tidak ada deteksi

    if run_detection:
        cap = cv2.VideoCapture(selected_camera)  # Gunakan kamera yang dipilih
        
        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning(f"Pengambilan gambar dari Kamera {selected_camera} gagal.")
                break
            
            # Deteksi YOLO
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model.predict(frame_rgb, imgsz=320)  # Tetap gunakan ukuran gambar 320
            frame, orang_terdeteksi, jumlah_orang = detect_person(frame_rgb, results[0])
            
            # Tampilkan frame kamera
            st_frame.image(frame, channels="RGB", use_column_width=True)
            
            # Update sidebar untuk informasi deteksi
            if orang_terdeteksi:
                detection_info = f"Jumlah orang terdeteksi: {jumlah_orang}"
            else:
                detection_info = "Tidak ada objek terdeteksi."
            detection_info_placeholder.text(detection_info)

            # Logika kontrol lampu dengan jeda waktu
            waktu_sekarang = time.time()  # Waktu sekarang

            if orang_terdeteksi:
                # Dari kondisi mati ke terdeteksi, langsung nyalakan lampu
                send_to_nodemcu("lampOn")
                waktu_terakhir_terdeteksi = None  # Reset waktu jeda
            elif not orang_terdeteksi:
                # Jika dari terdeteksi ke tidak terdeteksi, tunggu 3 detik sebelum mematikan lampu
                if waktu_terakhir_terdeteksi is None:
                    waktu_terakhir_terdeteksi = waktu_sekarang  # Catat waktu pertama kali tidak ada deteksi
                elif waktu_sekarang - waktu_terakhir_terdeteksi >= 3:  # 3 detik
                    send_to_nodemcu("lampOff")
                    waktu_terakhir_terdeteksi = None  # Reset waktu jeda

            # Update status sebelumnya
            previous_orang_terdeteksi = orang_terdeteksi
            
            # Berhenti jika checkbox dimatikan
            if not st.session_state.detection_control:
                send_to_nodemcu("lampOff")
                break
        
        cap.release()

if __name__ == "__main__":
    main()