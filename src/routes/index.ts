import { Router, Request, Response } from 'express';

const router = Router();

interface Prediction {
  month: string;
  recession_prob: number;
  recession_predict: boolean;
  signal: "HIGH" | "LOW";
}

const RECESSION_API = "https://recession-model-413903143998.us-central1.run.app";

router.get('/', (req: Request, res: Response) => {
    res.render('index', { title: 'Home' });
});

router.get('/eda', (req: Request, res: Response) => {
    res.render('eda', { title: 'Exploratory Data Analysis' });
});

router.get('/analysis-methods', (req: Request, res: Response) => {
    res.render('analysis_methods', { title: 'Analysis Methods' });
});

router.get('/ml-models', (req: Request, res: Response) => {
    res.render('ml_models', { title: 'Machine Learning Models' });
});

// ── Single /ml-inference route with logging + 30s timeout ──
router.get('/ml-inference', async (req: Request, res: Response) => {
  let prediction: Prediction | null = null;

  try {
    console.log("Fetching prediction from Cloud Run...");

    const response = await fetch(`${RECESSION_API}/predict`, {
      signal: AbortSignal.timeout(30000)   // 30 second timeout for cold starts
    });

    console.log("Response status:", response.status);

    if (response.ok) {
      prediction = await response.json() as Prediction;
      console.log("Prediction received:", prediction);
    } else {
      const text = await response.text();
      console.error("API error:", response.status, text);
    }
  } catch (err: any) {
    if (err.name === 'TimeoutError') {
      console.error("Request timed out — Cloud Run cold start took too long");
    } else {
      console.error("Fetch failed:", err.message);
    }
  }

  res.render("ml_inference", {
    title: "ML Inference",
    prediction
  });
});

router.get('/major-findings', (req: Request, res: Response) => {
    res.render('major_findings', { title: 'Major Findings' });
});

export default router;