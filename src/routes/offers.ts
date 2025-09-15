import { Router, Request, Response } from 'express';
import { Offer, UserOffer, User } from '../database';
import { OfferResponse } from '../types';

const router = Router();

// Get available offers
router.get('/', async (req: Request, res: Response) => {
  try {
    const provider = req.query.provider as string;
    const category = req.query.category as string;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const offset = (page - 1) * limit;

    // Build where clause
    const whereClause: any = { isActive: true };
    if (provider) {
      whereClause.provider = provider;
    }
    if (category) {
      whereClause.category = category;
    }

    const { count, rows: offers } = await Offer.findAndCountAll({
      where: whereClause,
      order: [['userPayout', 'DESC']],
      limit,
      offset,
    });

    const offersResponse: OfferResponse[] = offers.map(offer => ({
      id: offer.id,
      title: offer.title,
      description: offer.description,
      provider: offer.provider,
      category: offer.category,
      rewardAmount: offer.rewardAmount,
      userPayout: offer.userPayout,
      timeEstimate: offer.timeEstimate,
      requirements: offer.requirements,
      isActive: offer.isActive,
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
    console.error('Get offers error:', error);
    res.status(500).json({ error: 'Failed to get offers' });
  }
});

// Get offer by ID
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const offerId = parseInt(req.params.id);
    
    if (isNaN(offerId)) {
      return res.status(400).json({ error: 'Invalid offer ID' });
    }

    const offer = await Offer.findByPk(offerId);
    
    if (!offer) {
      return res.status(404).json({ error: 'Offer not found' });
    }

    if (!offer.isActive) {
      return res.status(404).json({ error: 'Offer is not available' });
    }

    const offerResponse: OfferResponse = {
      id: offer.id,
      title: offer.title,
      description: offer.description,
      provider: offer.provider,
      category: offer.category,
      rewardAmount: offer.rewardAmount,
      userPayout: offer.userPayout,
      timeEstimate: offer.timeEstimate,
      requirements: offer.requirements,
      isActive: offer.isActive,
    };

    res.json(offerResponse);
  } catch (error) {
    console.error('Get offer error:', error);
    res.status(500).json({ error: 'Failed to get offer' });
  }
});

// Start an offer (for authenticated users)
router.post('/:id/start', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const offerId = parseInt(req.params.id);
    const userId = req.user.id;
    
    if (isNaN(offerId)) {
      return res.status(400).json({ error: 'Invalid offer ID' });
    }

    // Check if offer exists and is active
    const offer = await Offer.findByPk(offerId);
    if (!offer || !offer.isActive) {
      return res.status(404).json({ error: 'Offer not found or not available' });
    }

    // Check if user already started this offer
    const existingUserOffer = await UserOffer.findOne({
      where: { userId, offerId },
    });

    if (existingUserOffer) {
      return res.status(400).json({ 
        error: 'You have already started this offer',
        status: existingUserOffer.status,
      });
    }

    // Create user offer record
    const userOffer = await UserOffer.create({
      userId,
      offerId,
      status: 'started',
      rewardAmount: offer.userPayout,
    });

    res.status(201).json({
      success: true,
      message: 'Offer started successfully',
      userOffer: {
        id: userOffer.id,
        status: userOffer.status,
        rewardAmount: userOffer.rewardAmount,
        startedAt: userOffer.startedAt,
      },
    });
  } catch (error) {
    console.error('Start offer error:', error);
    res.status(500).json({ error: 'Failed to start offer' });
  }
});

// Complete an offer (for future offerwall callback integration)
router.post('/:id/complete', async (req: Request, res: Response) => {
  try {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const offerId = parseInt(req.params.id);
    const userId = req.user.id;
    
    if (isNaN(offerId)) {
      return res.status(400).json({ error: 'Invalid offer ID' });
    }

    // Find user offer
    const userOffer = await UserOffer.findOne({
      where: { userId, offerId },
      include: [{ model: Offer, as: 'offer' }],
    });

    if (!userOffer) {
      return res.status(404).json({ error: 'Offer not found or not started' });
    }

    if (userOffer.status === 'completed') {
      return res.status(400).json({ error: 'Offer already completed' });
    }

    // Update user offer status
    await userOffer.update({
      status: 'completed',
      completedAt: new Date(),
    });

    // Add earning
    const earning = await UserOffer.sequelize!.models.Earning.create({
      userId,
      userOfferId: userOffer.id,
      amount: userOffer.rewardAmount || 0,
      type: 'task_completion',
      description: `Completed offer: ${userOffer.offer?.title || 'Unknown offer'}`,
    });

    // Update user balance and stats
    const user = await User.findByPk(userId);
    if (user) {
      const earnedAmount = userOffer.rewardAmount || 0;
      await user.update({
        balance: user.balance + earnedAmount,
        totalEarned: user.totalEarned + earnedAmount,
        tasksCompleted: user.tasksCompleted + 1,
      });
    }

    res.json({
      success: true,
      message: `Offer completed! You earned $${userOffer.rewardAmount?.toFixed(2) || '0.00'}`,
      earnedAmount: userOffer.rewardAmount,
      newBalance: user?.balance || 0,
    });
  } catch (error) {
    console.error('Complete offer error:', error);
    res.status(500).json({ error: 'Failed to complete offer' });
  }
});

// Get offer categories
router.get('/categories', async (req: Request, res: Response) => {
  try {
    const categories = await Offer.findAll({
      attributes: [[Offer.sequelize!.fn('DISTINCT', Offer.sequelize!.col('category')), 'category']],
      where: { isActive: true },
      raw: true,
    });

    const categoryList = categories.map(cat => cat.category).filter(Boolean);
    
    res.json({ categories: categoryList });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({ error: 'Failed to get categories' });
  }
});

// Get offer providers
router.get('/providers', async (req: Request, res: Response) => {
  try {
    const providers = await Offer.findAll({
      attributes: [[Offer.sequelize!.fn('DISTINCT', Offer.sequelize!.col('provider')), 'provider']],
      where: { isActive: true },
      raw: true,
    });

    const providerList = providers.map(prov => prov.provider).filter(Boolean);
    
    res.json({ providers: providerList });
  } catch (error) {
    console.error('Get providers error:', error);
    res.status(500).json({ error: 'Failed to get providers' });
  }
});

export default router;
