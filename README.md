# YOLO Object Detection with ESP8266 Integration
**Overview**
This repository contains a Streamlit-based Python application integrated with YOLOv11 for real-time object detection. The system utilizes the ESP8266 microcontroller for IoT actions, such as controlling devices based on object detection events. This project is tailored to detect "person" objects efficiently and manage actions like switching lights on and off.

**Features**
* **YOLOv11 Object Detection:** Real-time detection of "person" objects with the YOLO model.
* **Streamlit Interface:** Interactive UI for live camera feeds and detection results.
* **ESP8266 Integration:** Direct interaction with IoT devices via HTTP requests to control external hardware.
* **Customizable Camera Inputs:** Option to choose between two available cameras for object detection.

**Installation**
1. **Clone repository:**
   ```bash
   git clone https://github.com/zikriwahyuzi/yolo11-streamlit-esp8266.git
   cd test-yolo-esp

2. **Install dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt

3. **Run the app:**
   Start the Streamlit app using:
   ```bash
   streamlit run testyolo_esp.py
   
**Usage**
a. Connect your ESP8266 to the same network as the system.
b. Access the Streamlit application via localhost or deployed URL.
c. Choose your preferred camera input in the sidebar.
d. Monitor real-time detection results and control actions triggered by the ESP8266.

**Note:**
*'Camera Permissions' You may need to grant camera permissions to the app when you run it for the first time.
*Make sure the ESP8266 microcontroller is programmed to respond to HTTP requests sent by the system.
