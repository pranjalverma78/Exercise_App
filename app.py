from flask import Flask, render_template, Response
import cv2
import numpy as np
import PoseModule as pm
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Set up camera capture
cap = cv2.VideoCapture(0)
detector = pm.poseDetector()

# Push-up counter state
count = 0
direction = 0
form = 0
feedback = "Fix Form"


def gen_frames():
    """Generate frames for the video stream."""
    global count, direction, form, feedback
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break
        
        # Process the image
        img = detector.findPose(img, False)
        lmList = detector.findPosition(img, False)
        
        if len(lmList) != 0:
            elbow = detector.findAngle(img, 11, 13, 15)
            shoulder = detector.findAngle(img, 13, 11, 23)
            hip = detector.findAngle(img, 11, 23, 25)

            # Percentage of success of push-up
            per = np.interp(elbow, (90, 160), (0, 100))
            
            # Bar to show push-up progress
            bar = np.interp(elbow, (90, 160), (380, 50))

            # Check to ensure correct form before starting the program
            if elbow > 160 and shoulder > 40 and hip > 160:
                form = 1

            # Check for full range of motion for the push-up
            if form == 1:
                if elbow <= 90 and hip > 160:
                    feedback = "Up"
                    if direction == 0:
                        count += 0.5
                        direction = 1
                elif elbow > 160 and shoulder > 40 and hip > 160:
                    feedback = "Down"
                    if direction == 1:
                        count += 0.5
                        direction = 0
                else:
                    feedback = "Fix Form"

            # Draw the push-up progress bar
            if form == 1:
                cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
                cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            # Push-up counter display
            cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)
            
            # Feedback display
            cv2.rectangle(img, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, feedback, (500, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @app.route('/')
# def index():
#     """Render the main page."""
#     return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Returns the video feed to the client."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
