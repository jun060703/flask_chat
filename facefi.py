from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

def generate_frames():
    image='C:/Users/407/flask_chat/static/image/bear.png'
    webcam = cv2.VideoCapture(0)
    filterImage=cv2.imread(image,cv2.IMREAD_UNCHANGED)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + '\\haarcascade_frontalface_alt.xml')

    while True:
        ret, frame = webcam.read()

        if not ret:
            print("Failed to capture frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8)

        for (x, y, w, h) in faces:
            face_region = frame[y:y+h, x:x+w]

            resized_filter = cv2.resize(filterImage, (w, h))
            
            alpha_channel = resized_filter[:, :, 3] / 255.0


            for c in range(0, 3):
                face_region[:, :, c] = (1 - alpha_channel) * face_region[:, :, c] + alpha_channel * resized_filter[:, :, c] * 255.0

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    webcam.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/chat')
def chat():
    return render_template('chatting.html')

if __name__ == "__main__":
    app.run(debug=True)
