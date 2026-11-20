import { useState, useCallback } from 'react';

interface Detection {
  class_name: string;
  confidence: number;
  bbox: number[];
}

interface DetectionResult {
  detections: Detection[];
  inference_time: number;
  model: string;
}

interface UseDocumentDetectionReturn {
  detect: (file: File) => Promise<DetectionResult | null>;
  detectFromBase64: (base64: string) => Promise<DetectionResult | null>;
  loading: boolean;
  error: string | null;
}

const API_URL = 'http://localhost:8000';

export function useDocumentDetection(): UseDocumentDetectionReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const detect = useCallback(async (file: File): Promise<DetectionResult | null> => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result: DetectionResult = await response.json();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const detectFromBase64 = useCallback(async (base64: string): Promise<DetectionResult | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/detect-base64`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64 }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result: DetectionResult = await response.json();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { detect, detectFromBase64, loading, error };
}

export function useWebcamDetection() {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [videoRef, setVideoRef] = useState<HTMLVideoElement | null>(null);

  const startWebcam = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      setStream(mediaStream);
      return mediaStream;
    } catch (err) {
      console.error('Webcam error:', err);
      return null;
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  }, [stream]);

  return { startWebcam, stopWebcam, videoRef, setVideoRef };
}