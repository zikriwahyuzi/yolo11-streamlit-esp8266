import cv2
import streamlit as st
from ultralytics import YOLO
import requests

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
        st.error(f"Error connecting to NodeMCU: {e}")

# Proses hasil deteksi (hanya untuk "person")
def detect_person(image, results):
    boxes = results.boxes.xyxy.cpu().numpy()
    scores = results.boxes.conf.cpu().numpy()
    labels = results.boxes.cls.cpu().numpy()
    names = results.names
    
    person_detected = False
    detected_objects = []

    for i in range(len(boxes)):
        if scores[i] > 0.3:  # Confidence threshold
            label = names[int(labels[i])]
            if label == "person":  # Fokus hanya pada "person"
                x1, y1, x2, y2 = boxes[i].astype(int)
                detected_objects.append(label)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"{label}: {scores[i]:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                person_detected = True
    
    return image, detected_objects, person_detected

# Aplikasi Streamlit
def main():
    st.title("YOLOv11 Object Detection x IoT")
    st.sidebar.title("Settings")
    
    model_path = "yolo11n.pt"  # Path ke YOLO model
    model = load_model(model_path)

    # Pilih salah satu dari dua kamera yang tersedia
    st.sidebar.markdown("### Pilih Kamera")
    available_cameras = [0, 1]  # Daftar kamera yang tersedia (indeks)
    selected_camera = st.sidebar.radio("Pilih Kamera", options=available_cameras, format_func=lambda x: f"Kamera {x}")

    st.sidebar.write(f"Kamera yang digunakan: Kamera {selected_camera}")

    # Tombol start/stop
    run_detection = st.sidebar.checkbox("Start/Stop Object Detection", key="detection_control")

    # Placeholder untuk tampilan kamera dan deteksi
    st_frame = st.empty()
    st.sidebar.markdown("### Informasi Deteksi")
    detection_info_placeholder = st.sidebar.empty()

    # Variabel untuk melacak status lampu sebelumnya
    previous_person_detected = False

    if run_detection:
        cap = cv2.VideoCapture(selected_camera)  # Gunakan kamera yang dipilih
        
        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning(f"Failed to capture image from Kamera {selected_camera}.")
                break
            
            # Deteksi YOLO
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model.predict(frame_rgb, imgsz=320)  # Tetap gunakan ukuran gambar 640
            frame, detected_objects, person_detected = detect_person(frame_rgb, results[0])
            
            # Tampilkan frame kamera
            st_frame.image(frame, channels="RGB", use_column_width=True)
            
            # Update sidebar untuk informasi deteksi
            if detected_objects:
                detection_info = f"Person detected!" if person_detected else "No objects detected."
            else:
                detection_info = "No objects detected."
            detection_info_placeholder.text(detection_info)

            # Kontrol lampu tetap menggunakan logika awal
            if person_detected and not previous_person_detected:
                send_to_nodemcu("lampOn")  # Hidupkan lampu jika "person" terdeteksi
            elif not person_detected and previous_person_detected:
                send_to_nodemcu("lampOff")  # Matikan lampu jika "person" tidak lagi terdeteksi

            # Update status sebelumnya
            previous_person_detected = person_detected
            
            # Berhenti jika checkbox dimatikan
            if not st.session_state.detection_control:
                send_to_nodemcu("lampOff")
                break
        
        cap.release()

if __name__ == "__main__":
    main()