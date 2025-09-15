import { Router, Request, Response } from 'express';
import { User, UserOffer, Earning } from '../database';
import { DashboardStats, EarningResponse, UserOfferResponse } from '../types';

const router = Router();

// Get dashboard statistics
router.get('/stats', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    const userId = req.user.id;

    // Get recent earnings (last 10)
    const recentEarnings = await Earning.findAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit: 10,
    });

    // Get recent offers (last 10)
    const recentOffers = await UserOffer.findAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit: 10,
      include: [{ model: User, as: 'user' }],
    });

    // Count pending offers
    const pendingOffers = await UserOffer.count({
      where: {
        userId,
        status: ['started', 'in_progress'],
      },
    });

    // Prepare earnings response
    const earningsResponse: EarningResponse[] = recentEarnings.map(earning => ({
      id: earning.id,
      amount: earning.amount,
      type: earning.type,
      description: earning.description,
      createdAt: earning.createdAt,
    }));

    // Prepare offers response
    const offersResponse: UserOfferResponse[] = recentOffers.map(offer => ({
      id: offer.id,
      offerId: offer.offerId,
      status: offer.status,
      rewardAmount: offer.rewardAmount || 0,
      startedAt: offer.startedAt,
      completedAt: offer.completedAt,
    }));

    const stats: DashboardStats = {
      totalEarnings: req.user.totalEarned,
      completedOffers: req.user.tasksCompleted,
      pendingOffers,
      accountBalance: req.user.balance,
      recentEarnings: earningsResponse,
      recentOffers: offersResponse,
    };

    res.json(stats);
  } catch (error) {
    console.error('Dashboard stats error:', error);
    res.status(500).json({ error: 'Failed to get dashboard statistics' });
  }
});

// Get user's recent activity
router.get('/activity', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    const userId = req.user.id;
    const limit = parseInt(req.query.limit as string) || 20;

    // Get recent earnings and offers combined
    const recentEarnings = await Earning.findAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit: Math.floor(limit / 2),
    });

    const recentOffers = await UserOffer.findAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit: Math.floor(limit / 2),
      include: [{ model: User, as: 'user' }],
    });

    // Combine and sort by date
    const activities = [
      ...recentEarnings.map(earning => ({
        type: 'earning' as const,
        data: earning,
        date: earning.createdAt,
      })),
      ...recentOffers.map(offer => ({
        type: 'offer' as const,
        data: offer,
        date: offer.createdAt,
      })),
    ].sort((a, b) => b.date.getTime() - a.date.getTime());

    res.json({
      activities: activities.slice(0, limit),
      total: activities.length,
    });
  } catch (error) {
    console.error('Activity error:', error);
    res.status(500).json({ error: 'Failed to get activity' });
  }
});

// Get user's earnings history
router.get('/earnings', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    const userId = req.user.id;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const offset = (page - 1) * limit;

    const { count, rows: earnings } = await Earning.findAndCountAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit,
      offset,
    });

    const earningsResponse: EarningResponse[] = earnings.map(earning => ({
      id: earning.id,
      amount: earning.amount,
      type: earning.type,
      description: earning.description,
      createdAt: earning.createdAt,
    }));

    res.json({
      earnings: earningsResponse,
      pagination: {
        page,
        limit,
        total: count,
        pages: Math.ceil(count / limit),
      },
    });
  } catch (error) {
    console.error('Earnings history error:', error);
    res.status(500).json({ error: 'Failed to get earnings history' });
  }
});

// Get user's offer history
router.get('/offers', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    const userId = req.user.id;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const offset = (page - 1) * limit;

    const { count, rows: offers } = await UserOffer.findAndCountAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
      limit,
      offset,
      include: [{ model: User, as: 'user' }],
    });

    const offersResponse: UserOfferResponse[] = offers.map(offer => ({
      id: offer.id,
      offerId: offer.offerId,
      status: offer.status,
      rewardAmount: offer.rewardAmount || 0,
      startedAt: offer.startedAt,
      completedAt: offer.completedAt,
    }));

    res.json({
      offers: offersResponse,
      pagination: {
        page,
        limit,
        total: count,
        pages: Math.ceil(count / limit),
      },
    });
  } catch (error) {
    console.error('Offer history error:', error);
    res.status(500).json({ error: 'Failed to get offer history' });
  }
});

export default router;
