import express from 'express';
import path from 'path';
import router from './routes/index';

const app = express();

// View engine setup
app.set('views', path.join(__dirname, '../views'));
app.set('view engine', 'ejs');

// Static files
app.use(express.static(path.join(__dirname, '../public')));

// Routes
app.use('/', router);

export default app;
