import { Router, Request, Response } from 'express';

const router = Router();

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

router.get('/major-findings', (req: Request, res: Response) => {
    res.render('major_findings', { title: 'Major Findings' });
});

export default router;
