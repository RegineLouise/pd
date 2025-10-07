import React, { useRef, useState, useEffect } from 'react';

const Camera = () => {
  const restartCamera = () => {
    setImageSrc(null);
    startCamera();
  };
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(null);

  const startCamera = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        alert('Camera access denied or not available.');
      }
    }
  };

  useEffect(() => {
    startCamera();
    // eslint-disable-next-line
  }, []);

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video && canvas) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/png');
      setImageSrc(dataUrl);
    }
  };

  return (
    <div style={{ margin: '2rem auto', textAlign: 'center' }}>
  <h3 style={{ color: 'black' }}>Align Your Foot here!</h3>
      {!imageSrc ? (
        <>
          <video ref={videoRef} width="480" height="360" autoPlay style={{ border: '1px solid #ccc' }} />
          <br />
          <button onClick={captureImage} style={{ marginTop: '1rem' }}>Scan</button>
        </>
      ) : (
        <>
          <img src={imageSrc} alt="Captured" style={{ maxWidth: '480px', border: '1px solid #ccc' }} />
          <br />
          <a
            href={imageSrc}
            download={`captured-image-${Date.now()}.png`}
            style={{ marginTop: '1rem', display: 'inline-block', padding: '0.5rem 1rem', background: '#282c34', color: 'white', borderRadius: '4px', textDecoration: 'none' }}
          >
            Save Image
          </a>
          <br />
          <button onClick={restartCamera} style={{ marginTop: '1rem', marginLeft: '1rem', padding: '0.5rem 1rem', background: '#61dafb', color: '#282c34', borderRadius: '4px', border: 'none' }}>
            Restart Camera
          </button>
        </>
      )}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};

export default Camera;
