import { Router, Request, Response } from 'express';
import { Payout, User } from '../database';
import { PayoutRequest } from '../types';

const router = Router();

const MINIMUM_PAYOUT_AMOUNT = 5.0; // $5 minimum

// Request a payout
router.post('/request', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const { amount }: PayoutRequest = req.body;
    const userId = req.user.id;

    // Validate amount
    if (!amount || amount < MINIMUM_PAYOUT_AMOUNT) {
      return res.status(400).json({ 
        error: `Minimum payout amount is $${MINIMUM_PAYOUT_AMOUNT}` 
      });
    }

    if (amount > req.user.balance) {
      return res.status(400).json({ 
        error: 'Insufficient balance' 
      });
    }

    // Create payout record
    const payout = await Payout.create({
      userId,
      amount,
      method: 'paypal',
      status: 'pending',
      paymentDetails: {
        paypalEmail: req.user.paypalEmail,
      },
    });

    // Update user balance
    await (req.user as User).update({
      balance: req.user.balance - amount,
    });

    res.status(201).json({
      success: true,
      message: 'Payout request submitted successfully',
      payout: {
        id: payout.id,
        amount: payout.amount,
        status: payout.status,
        requestedAt: payout.requestedAt,
      },
    });
  } catch (error) {
    console.error('Payout request error:', error);
    res.status(500).json({ error: 'Failed to request payout' });
  }
});

// Get payout history
router.get('/history', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const userId = req.user.id;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const offset = (page - 1) * limit;

    const { count, rows: payouts } = await Payout.findAndCountAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit,
      offset,
    });

    res.json({
      payouts,
      pagination: {
        page,
        limit,
        total: count,
        pages: Math.ceil(count / limit),
      },
    });
  } catch (error) {
    console.error('Payout history error:', error);
    res.status(500).json({ error: 'Failed to get payout history' });
  }
});

// Get payout info
router.get('/info', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    res.json({
      minimumPayout: MINIMUM_PAYOUT_AMOUNT,
      availableBalance: req.user.balance,
      paypalEmail: req.user.paypalEmail,
      canPayout: req.user.balance >= MINIMUM_PAYOUT_AMOUNT,
    });
  } catch (error) {
    console.error('Payout info error:', error);
    res.status(500).json({ error: 'Failed to get payout info' });
  }
});

export default router;
