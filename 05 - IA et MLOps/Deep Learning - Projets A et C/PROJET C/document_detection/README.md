# Document Detection API

## Démarrage

```bash
# 1. Installer les dépendances
cd document_detection
pip install -r requirements.txt

# 2. Lancer l'API
uvicorn api.main:app --reload --port 8000
```

## Endpoints

| Méthode | Route | Description |
|--------|-------|------------|
| GET | `/` | Health check |
| GET | `/health` | Status API + CUDA |
| POST | `/detect` | Détection par fichier |
| POST | `/detect-base64` | Détection par base64 |

## Exemple React

```tsx
import { useDocumentDetection } from './src/useDocumentDetection';

function DocumentScanner() {
  const { detect, loading } = useDocumentDetection();

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const result = await detect(file);
      console.log(result);
    }
  };

  return <input type="file" onChange={handleFile} disabled={loading} />;
}
```

## Réponse

```json
{
  "detections": [
    {
      "class_name": "id_card",
      "confidence": 0.92,
      "bbox": [120, 50, 380, 240]
    }
  ],
  "inference_time": 0.045,
  "model": "document_detector"
}
```