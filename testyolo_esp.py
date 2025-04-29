import cv2
import streamlit as st
import numpy as np
from PIL import Image
from ultralytics import YOLO
from collections import Counter
import requests  # Library untuk mengirim HTTP request

# Load YOLO model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Fungsi untuk mengirim sinyal ke NodeMCU
def send_to_nodemcu(action):
    url = f"http://192.168.148.41/{action}"  # Ganti <IP_NodeMCU> dengan IP NodeMCU Anda
    try:
        requests.get(url)
    except Exception as e:
        st.error(f"Error connecting to NodeMCU: {e}")

# Process and display the detection results (Deteksi semua objek, tapi kontrol lampu hanya untuk "person")
def display_results(image, results):
    boxes = results.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
    scores = results.boxes.conf.cpu().numpy()  # Confidence scores
    labels = results.boxes.cls.cpu().numpy()  # Class indices
    names = results.names  # Class names
    
    detected_objects = []
    person_detected = False  # Menandai apakah "person" terdeteksi

    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Confidence threshold
            x1, y1, x2, y2 = boxes[i].astype(int)
            label = names[int(labels[i])]
            score = scores[i]
            detected_objects.append(label)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if label == "person":  # Cek apakah "person" terdeteksi
                person_detected = True
    
    return image, detected_objects, person_detected

# Main Streamlit app
def main():
    st.title("YOLOv11 Object Detection x IoT")
    st.sidebar.title("Settings")
    
    model_path = "yolo11n.pt"  # Path to your YOLO model
    model = load_model(model_path)

    # Langsung gunakan kamera dengan indeks 1
    camera_index = 1  # Default kamera eksternal, indeks 1

    st.sidebar.write(f"Kamera yang digunakan: Kamera {camera_index}")

    # Checkbox untuk memulai deteksi (Diletakkan di atas informasi deteksi)
    run_detection = st.sidebar.checkbox("Start/Stop Object Detection", key="detection_control")

    # Placeholder untuk informasi deteksi di sidebar
    st.sidebar.markdown("### Informasi Deteksi")
    detection_info_placeholder = st.sidebar.empty()

    # Open video capture jika checkbox aktif
    if run_detection:
        cap = cv2.VideoCapture(camera_index)  # Gunakan kamera dengan indeks 1
        st_frame = st.empty()  # Placeholder untuk video frames

        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture image. Pastikan kamera dengan indeks 1 terhubung.")
                break

            # Run YOLO detection
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert ke RGB untuk display
            results = model.predict(frame, imgsz=640)  # Lakukan deteksi
            
            # Proses hasil deteksi
            frame, detected_objects, person_detected = display_results(frame, results[0])

            # Tampilkan video feed
            st_frame.image(frame, channels="RGB", use_column_width=True)
            
            # Update informasi deteksi di sidebar
            if detected_objects:
                object_counts = Counter(detected_objects)
                detection_info = "\n".join([f"{obj}: {count}" for obj, count in object_counts.items()])
            else:
                detection_info = "No objects detected."

            detection_info_placeholder.text(detection_info)  # Tampilkan informasi deteksi di sidebar

            # Kontrol lampu hanya jika "person" terdeteksi
            if person_detected:
                send_to_nodemcu("lampOn")  # Hidupkan lampu jika "person" terdeteksi
            else:
                send_to_nodemcu("lampOff")  # Matikan lampu jika "person" tidak terdeteksi

            # Break the loop jika checkbox dimatikan
            if not st.session_state.detection_control:
                send_to_nodemcu("lampOff")  # Matikan lampu saat deteksi berhenti
                break
        
        cap.release()

if __name__ == "__main__":
    main()