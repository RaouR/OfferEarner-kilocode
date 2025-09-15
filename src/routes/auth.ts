import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { createUser, authenticateUser, createAccessToken } from '../middleware/auth';
import { UserRegister, UserLogin, TokenResponse, UserResponse } from '../types';

const router = Router();

// Validation middleware
const registerValidation = [
  body('username')
    .isLength({ min: 3, max: 50 })
    .withMessage('Username must be between 3 and 50 characters')
    .matches(/^[a-zA-Z0-9_]+$/)
    .withMessage('Username can only contain letters, numbers, and underscores'),
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long'),
  body('paypalEmail')
    .isEmail()
    .withMessage('Please provide a valid PayPal email address'),
];

const loginValidation = [
  body('email')
    .isEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .notEmpty()
    .withMessage('Password is required'),
];

// Register new user
router.post('/register', registerValidation, async (req: Request, res: Response) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        error: 'Validation failed', 
        details: errors.array() 
      });
    }

    const userData: UserRegister = req.body;

    // Create user
    const user = await createUser(userData);

    // Create access token
    const accessToken = createAccessToken({ sub: user.id.toString() });

    // Prepare user response (exclude sensitive data)
    const userResponse: UserResponse = {
      id: user.id,
      username: user.username,
      email: user.email,
      paypalEmail: user.paypalEmail,
      balance: user.balance,
      totalEarned: user.totalEarned,
      tasksCompleted: user.tasksCompleted,
      isActive: user.isActive,
      createdAt: user.createdAt,
    };

    const response: TokenResponse = {
      accessToken,
      tokenType: 'bearer',
      user: userResponse,
    };

    res.status(201).json(response);
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('already registered') || error.message.includes('already taken')) {
        return res.status(400).json({ error: error.message });
      }
    }
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Registration failed' });
  }
});

// Login user
router.post('/login', loginValidation, async (req: Request, res: Response) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        error: 'Validation failed', 
        details: errors.array() 
      });
    }

    const userData: UserLogin = req.body;

    // Authenticate user
    const user = await authenticateUser(userData.email, userData.password);
    if (!user) {
      return res.status(401).json({ 
        error: 'Incorrect email or password' 
      });
    }

    // Create access token
    const accessToken = createAccessToken({ sub: user.id.toString() });

    // Prepare user response (exclude sensitive data)
    const userResponse: UserResponse = {
      id: user.id,
      username: user.username,
      email: user.email,
      paypalEmail: user.paypalEmail,
      balance: user.balance,
      totalEarned: user.totalEarned,
      tasksCompleted: user.tasksCompleted,
      isActive: user.isActive,
      createdAt: user.createdAt,
    };

    const response: TokenResponse = {
      accessToken,
      tokenType: 'bearer',
      user: userResponse,
    };

    res.json(response);
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Login failed' });
  }
});

// Get current user info
router.get('/me', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    const userResponse: UserResponse = {
      id: req.user.id,
      username: req.user.username,
      email: req.user.email,
      paypalEmail: req.user.paypalEmail,
      balance: req.user.balance,
      totalEarned: req.user.totalEarned,
      tasksCompleted: req.user.tasksCompleted,
      isActive: req.user.isActive,
      createdAt: req.user.createdAt,
    };

    res.json(userResponse);
  } catch (error) {
    console.error('Get user info error:', error);
    res.status(500).json({ error: 'Failed to get user info' });
  }
});

export default router;
