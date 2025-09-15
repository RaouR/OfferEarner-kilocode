export interface User {
  id: number;
  username: string;
  email: string;
  hashedPassword: string;
  paypalEmail: string;
  balance: number;
  totalEarned: number;
  tasksCompleted: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Offer {
  id: number;
  title: string;
  description: string;
  provider: string;
  category: string;
  rewardAmount: number;
  userPayout: number;
  timeEstimate?: string;
  requirements?: any;
  externalOfferId?: string;
  callbackUrl?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserOffer {
  id: number;
  userId: number;
  offerId: number;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  progressData?: any;
  startedAt: Date;
  completedAt?: Date;
  rewardAmount?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Earning {
  id: number;
  userId: number;
  userOfferId?: number;
  amount: number;
  type: 'task_completion' | 'bonus' | 'referral';
  description: string;
  createdAt: Date;
}

export interface Payout {
  id: number;
  userId: number;
  amount: number;
  method: 'paypal' | 'gift_card' | 'crypto';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  paymentDetails?: any;
  requestedAt: Date;
  processedAt?: Date;
  transactionId?: string;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface OfferCallback {
  id: number;
  provider: string;
  userId?: number;
  externalOfferId?: string;
  externalUserId?: string;
  status?: string;
  rewardAmount?: number;
  callbackData?: any;
  processed: boolean;
  processedAt?: Date;
  createdAt: Date;
}

// API Request/Response Types
export interface UserRegister {
  username: string;
  email: string;
  password: string;
  paypalEmail: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
  user: UserResponse;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  paypalEmail: string;
  balance: number;
  totalEarned: number;
  tasksCompleted: number;
  isActive: boolean;
  createdAt: Date;
}

export interface DashboardStats {
  totalEarnings: number;
  completedOffers: number;
  pendingOffers: number;
  accountBalance: number;
  recentEarnings: EarningResponse[];
  recentOffers: UserOfferResponse[];
}

export interface EarningResponse {
  id: number;
  amount: number;
  type: string;
  description: string;
  createdAt: Date;
}

export interface UserOfferResponse {
  id: number;
  offerId: number;
  status: string;
  rewardAmount?: number;
  startedAt: Date;
  completedAt?: Date;
}

export interface OfferResponse {
  id: number;
  title: string;
  description: string;
  provider: string;
  category: string;
  rewardAmount: number;
  userPayout: number;
  timeEstimate?: string;
  requirements?: any;
  isActive: boolean;
}

export interface PayoutRequest {
  amount: number;
}

export interface PlatformStats {
  totalUsers: number;
  totalEarnings: number;
  totalPayouts: number;
  activeOffers: number;
  platformRevenue: number;
}

// PayPal Types
export interface PayPalPayoutRequest {
  amount: number;
  paypalEmail: string;
}

export interface PayPalPayoutResponse {
  success: boolean;
  message: string;
  payoutId?: string;
  grossAmount?: number;
  transactionFee?: number;
  netAmount?: number;
  error?: string;
}

// Lootably Types
export interface LootablyOffer {
  offerId: string;
  name: string;
  description: string;
  currencyReward: number;
  categories: string[];
  link: string;
  image?: string;
  conversionRate?: number;
}

export interface LootablyPostbackData {
  [key: string]: string | number;
}

// JWT Payload
export interface JWTPayload {
  sub: string;
  exp: number;
  iat: number;
}

// Express Request Extensions
declare global {
  namespace Express {
    interface Request {
      user?: User | null;
    }
  }
}
