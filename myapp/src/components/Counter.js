import React, { useRef, useEffect, useState } from 'react';

function Counter() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [processedFrame, setProcessedFrame] = useState(null);

    useEffect(() => {
        let stream;

        async function startWebcam() {
            try {
                // Access the webcam
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                const videoElement = videoRef.current;

                if (videoElement) {
                    videoElement.srcObject = stream;
                    videoElement.onloadedmetadata = () => {
                        videoElement.play().catch(err => console.error("Play error: ", err));
                    };
                }
            } catch (err) {
                console.error("Error accessing webcam: ", err);
            }
        }

        startWebcam();

        return () => {
            // Stop all video tracks when the component unmounts
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current && canvasRef.current) {
                const canvas = canvasRef.current;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

                // Send the current frame to the backend
                const frameData = canvas.toDataURL('image/jpeg');
                fetch('http://127.0.0.1:5000/process_video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ frame: frameData }),
                })
                    .then(response => response.json())
                    .then(data => setProcessedFrame(data.frame))
                    .catch(err => console.error("Error sending frame: ", err));
            }
        }, 100); // Adjust interval as needed (100ms = 10 FPS)

        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <h1>Pushup Counter</h1>
            <video ref={videoRef} style={{ display: 'none' }}></video>
            <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }}></canvas>
            {processedFrame && (
                <img
                    src={`data:image/jpeg;base64,${processedFrame}`}
                    alt="Processed"
                    style={{ width: '640px', height: '480px' }}
                />
            )}
        </div>
    );
}

export default Counter;
