import cv2

def detect_faces():
    webcam = cv2.VideoCapture(0)
    filterimage = cv2.imread(image_path2, cv2.IMREAD_UNCHANGED)
    resizeImage = cv2.resize(filterimage, dsize=(200, 200))

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')

    while True:
        ret, frame = webcam.read()

        if not ret:
            print("Failed to capture frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1, minNeighbors=8)

        for (x, y, w, h) in faces:
            face_region = frame[y:y+h, x:x+w]

            resized_filter = cv2.resize(filterimage, (w, h))

            alpha_channel = resized_filter[:, :, 3] / 255.0
            for c in range(0, 3):
                face_region[:, :, c] = (1 - alpha_channel) * face_region[:, :, c] + alpha_channel * resized_filter[:, :, c] * 255.0

        cv2.imshow('test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    webcam.release()
    cv2.destroyAllWindows()

image_path2 = 'C:/Users/Samsung/Downloads/flask_chat-main/flask_chat/static/image/bear.png'
detect_faces()
