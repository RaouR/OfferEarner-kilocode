import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { User } from '../database';
import { JWTPayload } from '../types';

const SECRET_KEY = process.env.SECRET_KEY || 'fallback-secret-key-change-in-production';
const ACCESS_TOKEN_EXPIRE_MINUTES = parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES || '30');

export function hashPassword(password: string): string {
  return bcrypt.hashSync(password, 10);
}

export function verifyPassword(plainPassword: string, hashedPassword: string): boolean {
  return bcrypt.compareSync(plainPassword, hashedPassword);
}

export function createAccessToken(data: { sub: string }): string {
  const payload: JWTPayload = {
    ...data,
    exp: Math.floor(Date.now() / 1000) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    iat: Math.floor(Date.now() / 1000),
  };
  return jwt.sign(payload, SECRET_KEY, { algorithm: 'HS256' });
}

export function verifyToken(token: string): string {
  try {
    const payload = jwt.verify(token, SECRET_KEY) as JWTPayload;
    return payload.sub;
  } catch (error) {
    throw new Error('Invalid token');
  }
}

export async function authenticateToken(req: Request, res: Response, next: NextFunction): Promise<void> {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    res.status(401).json({ error: 'Access token required' });
    return;
  }

  try {
    const userId = verifyToken(token);
    const user = await User.findByPk(parseInt(userId));
    
    if (!user) {
      res.status(401).json({ error: 'User not found' });
      return;
    }

    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

export async function optionalAuth(req: Request, res: Response, next: NextFunction): Promise<void> {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    next();
    return;
  }

  try {
    const userId = verifyToken(token);
    const user = await User.findByPk(parseInt(userId));
    req.user = user;
  } catch (error) {
    // Token is invalid, but we don't want to block the request
    req.user = null;
  }

  next();
}

export async function getUserByEmail(email: string): Promise<User | null> {
  return await User.findOne({ where: { email } });
}

export async function getUserByUsername(username: string): Promise<User | null> {
  return await User.findOne({ where: { username } });
}

export async function authenticateUser(email: string, password: string): Promise<User | null> {
  const user = await getUserByEmail(email);
  if (!user) {
    return null;
  }
  
  if (!verifyPassword(password, user.hashedPassword)) {
    return null;
  }
  
  return user;
}

export async function createUser(userData: {
  username: string;
  email: string;
  password: string;
  paypalEmail: string;
}): Promise<User> {
  // Check if user already exists
  const existingUserByEmail = await getUserByEmail(userData.email);
  if (existingUserByEmail) {
    throw new Error('Email already registered');
  }

  const existingUserByUsername = await getUserByUsername(userData.username);
  if (existingUserByUsername) {
    throw new Error('Username already taken');
  }

  // Create new user
  const hashedPassword = hashPassword(userData.password);
  return await User.create({
    username: userData.username,
    email: userData.email,
    hashedPassword,
    paypalEmail: userData.paypalEmail,
  });
}
