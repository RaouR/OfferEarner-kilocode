import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import path from 'path';
import dotenv from 'dotenv';
import { initDatabase } from './database';
import { authenticateToken, optionalAuth } from './middleware/auth';
import authRoutes from './routes/auth';
import dashboardRoutes from './routes/dashboard';
import offersRoutes from './routes/offers';
import payoutsRoutes from './routes/payouts';
import lootablyRoutes from './routes/lootably';
import adminRoutes from './routes/admin';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8001;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
});
app.use(limiter);

// CORS
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://offerearner.raour.site', 'https://www.offerearner.raour.site']
    : true,
  credentials: true,
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Static files
app.use('/static', express.static(path.join(__dirname, '../public')));

// View engine setup (for serving HTML pages)
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views'));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/dashboard', authenticateToken, dashboardRoutes);
app.use('/api/offers', offersRoutes);
app.use('/api/payouts', authenticateToken, payoutsRoutes);
app.use('/api/callback/lootably', lootablyRoutes);
app.use('/api/admin', authenticateToken, adminRoutes);

// Web routes (HTML pages)
app.get('/', optionalAuth, (req, res) => {
  res.render('index', { 
    user: req.user,
    title: 'Home - OfferEarner'
  });
});

app.get('/register', (req, res) => {
  res.render('register', { 
    title: 'Register - OfferEarner'
  });
});

app.get('/login', (req, res) => {
  res.render('login', { 
    title: 'Login - OfferEarner'
  });
});

app.get('/dashboard', authenticateToken, (req, res) => {
  res.render('dashboard', { 
    user: req.user,
    title: 'Dashboard - OfferEarner'
  });
});

app.get('/offers', optionalAuth, (req, res) => {
  res.render('offers', { 
    user: req.user,
    title: 'Offers - OfferEarner'
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message 
  });
});

// Start server
async function startServer() {
  try {
    // Initialize database
    await initDatabase();
    
    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 OfferEarner server running on port ${PORT}`);
      console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log(`🔗 Health check: http://localhost:${PORT}/health`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();

export default app;
