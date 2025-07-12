# Virtual Glasses Try-On

This project is a real-time virtual glasses try-on application built with Python, Flask, and dlib. It uses a webcam to detect faces and overlay different models of glasses onto the user's face in real-time.

## Features

- **Real-Time Video Streaming**: The application streams video from your webcam to the browser.
- **Face Detection**: It uses dlib's face detector to accurately locate faces in the video stream.
- **Facial Landmark Detection**: It identifies 68 key points on the face to precisely position the virtual glasses.
- **Switchable Glasses Models**: Users can switch between different glasses models in real-time.
- **Web-Based UI**: The user interface is built with HTML, CSS, and JavaScript, and it communicates with the Flask server using WebSockets.

## Requirements

- Python 3.6+
- OpenCV
- dlib
- Flask
- Flask-SocketIO
- A webcam

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/virtual-glasses-try-on.git
   cd virtual-glasses-try-on
   ```

2. **Install the required Python libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dlib shape predictor model:**
   - Download the `shape_predictor_68_face_landmarks.dat.bz2` file from [here](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2).
   - Extract the `shape_predictor_68_face_landmarks.dat` file and place it in the root directory of the project.

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

5. **Open your web browser and go to `http://127.0.0.1:5000` to see the application in action.**

## Project Structure

```
.
├── app.py                          # The main Flask application file
├── shape_predictor_68_face_landmarks.dat # dlib's pre-trained facial landmark predictor
├── static
│   └── images
│       ├── glasses1.png
│       ├── glasses2.png
│       ├── glasses3.png
│       └── glasses4.png
├── templates
│   └── index.html                  # The HTML template for the web interface
└── test-camera.py                  # A simple script to test your webcam
```

## Troubleshooting

- **Camera not working**:
  - Make sure your webcam is properly connected and not being used by another application.
  - If you have multiple webcams, you may need to change the camera index in `app.py`. Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`.
  - You can use the `test-camera.py` script to check if your webcam is working with OpenCV.

- **`shape_predictor_68_face_landmarks.dat` not found**:
  - Make sure you have downloaded the file and placed it in the root directory of the project.

- **Other issues**:
  - If you encounter any other issues, please open an issue on the GitHub repository.
