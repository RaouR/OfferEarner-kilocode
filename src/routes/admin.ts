import { Router, Request, Response } from 'express';
import { User, Offer, UserOffer, Earning, Payout } from '../database';
import { PlatformStats } from '../types';

const router = Router();

// Get platform statistics
router.get('/platform-stats', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Get total users
    const totalUsers = await User.count();

    // Get total earnings
    const totalEarningsResult = await Earning.findOne({
      attributes: [[Earning.sequelize!.fn('SUM', Earning.sequelize!.col('amount')), 'total']],
      raw: true,
    });
    const totalEarnings = parseFloat((totalEarningsResult as any)?.total as string) || 0;

    // Get total payouts
    const totalPayoutsResult = await Payout.findOne({
      attributes: [[Payout.sequelize!.fn('SUM', Payout.sequelize!.col('amount')), 'total']],
      where: { status: 'completed' },
      raw: true,
    });
    const totalPayouts = parseFloat((totalPayoutsResult as any)?.total as string) || 0;

    // Get active offers
    const activeOffers = await Offer.count({
      where: { isActive: true },
    });

    // Calculate platform revenue (difference between total earnings and payouts)
    const platformRevenue = totalEarnings - totalPayouts;

    const stats: PlatformStats = {
      totalUsers,
      totalEarnings,
      totalPayouts,
      activeOffers,
      platformRevenue,
    };

    res.json(stats);
  } catch (error) {
    console.error('Platform stats error:', error);
    res.status(500).json({ error: 'Failed to get platform statistics' });
  }
});

// Get payout statistics
router.get('/payouts/stats', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // Get payout statistics by status
    const pendingPayouts = await Payout.count({
      where: { status: 'pending' },
    });

    const processingPayouts = await Payout.count({
      where: { status: 'processing' },
    });

    const completedPayouts = await Payout.count({
      where: { status: 'completed' },
    });

    const failedPayouts = await Payout.count({
      where: { status: 'failed' },
    });

    // Get total payout amounts by status
    const pendingAmount = await Payout.findOne({
      attributes: [[Payout.sequelize!.fn('SUM', Payout.sequelize!.col('amount')), 'total']],
      where: { status: 'pending' },
      raw: true,
    });

    const processingAmount = await Payout.findOne({
      attributes: [[Payout.sequelize!.fn('SUM', Payout.sequelize!.col('amount')), 'total']],
      where: { status: 'processing' },
      raw: true,
    });

    const completedAmount = await Payout.findOne({
      attributes: [[Payout.sequelize!.fn('SUM', Payout.sequelize!.col('amount')), 'total']],
      where: { status: 'completed' },
      raw: true,
    });

    res.json({
      counts: {
        pending: pendingPayouts,
        processing: processingPayouts,
        completed: completedPayouts,
        failed: failedPayouts,
      },
      amounts: {
        pending: parseFloat((pendingAmount as any)?.total as string) || 0,
        processing: parseFloat((processingAmount as any)?.total as string) || 0,
        completed: parseFloat((completedAmount as any)?.total as string) || 0,
      },
    });
  } catch (error) {
    console.error('Payout stats error:', error);
    res.status(500).json({ error: 'Failed to get payout statistics' });
  }
});

// Get recent activity
router.get('/recent-activity', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const limit = parseInt(req.query.limit as string) || 50;

    // Get recent registrations
    const recentUsers = await User.findAll({
      order: [['createdAt', 'DESC']],
      limit: Math.floor(limit / 3),
      attributes: ['id', 'username', 'email', 'createdAt'],
    });

    // Get recent earnings
    const recentEarnings = await Earning.findAll({
      order: [['createdAt', 'DESC']],
      limit: Math.floor(limit / 3),
      include: [{ model: User, as: 'user', attributes: ['id', 'username'] }],
    });

    // Get recent payouts
    const recentPayouts = await Payout.findAll({
      order: [['createdAt', 'DESC']],
      limit: Math.floor(limit / 3),
      include: [{ model: User, as: 'user', attributes: ['id', 'username'] }],
    });

    res.json({
      recentUsers,
      recentEarnings,
      recentPayouts,
    });
  } catch (error) {
    console.error('Recent activity error:', error);
    res.status(500).json({ error: 'Failed to get recent activity' });
  }
});

// Sync offers from Lootably
router.post('/sync-lootably-offers', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // This would call the Lootably sync endpoint
    const response = await fetch(`${req.protocol}://${req.get('host')}/api/callback/lootably/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const result = await response.json();

    res.json(result);
  } catch (error) {
    console.error('Sync Lootably offers error:', error);
    res.status(500).json({ error: 'Failed to sync Lootably offers' });
  }
});

export default router;
