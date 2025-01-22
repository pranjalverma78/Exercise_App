from flask import Flask, Response, request
import cv2
import numpy as np
import PoseModule as pm
from flask_cors import CORS
import base64

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

detector = pm.poseDetector()

# Push-up counter state
count = 0
direction = 0
form = 0
feedback = "Fix Form"


@app.route('/process_video', methods=['POST'])
def process_video():
    """Process video frames sent from the frontend."""
    global count, direction, form, feedback

    # Decode the base64-encoded image
    data = request.json.get('frame')
    img_data = base64.b64decode(data.split(',')[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

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

    # Encode processed frame back to base64
    _, buffer = cv2.imencode('.jpg', img)
    processed_frame = base64.b64encode(buffer).decode('utf-8')

    return {'frame': processed_frame}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
