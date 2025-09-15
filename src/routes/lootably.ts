import { Router, Request, Response } from 'express';
import { Offer, OfferCallback, User, UserOffer, Earning } from '../database';
import { LootablyPostbackData } from '../types';

const router = Router();

// Handle Lootably postback/callback
router.get('/', async (req: Request, res: Response) => {
  try {
    // Get all query parameters from the postback
    const postbackData: LootablyPostbackData = req.query as any;
    
    // Log the postback data
    console.log('Lootably postback received:', postbackData);

    // Store callback data
    const callback = await OfferCallback.create({
      provider: 'lootably',
      externalOfferId: postbackData.offer_id as string,
      externalUserId: postbackData.user_id as string,
      status: postbackData.status as string,
      rewardAmount: parseFloat(postbackData.amount as string) || 0,
      callbackData: postbackData,
      processed: false,
    });

    // Process the callback
    const result = await processLootablyPostback(postbackData);
    
    if (result.success) {
      // Mark as processed
      await callback.update({
        processed: true,
        processedAt: new Date(),
      });
      
      // Return "1" as required by Lootably for successful processing
      res.send('1');
    } else {
      res.send(`ERROR: ${result.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error('Lootably postback processing failed:', error);
    res.send(`ERROR: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
});

// Process Lootably postback data
async function processLootablyPostback(postbackData: LootablyPostbackData) {
  try {
    const userId = parseInt(postbackData.user_id as string);
    const offerId = postbackData.offer_id as string;
    const status = postbackData.status as string;
    const amount = parseFloat(postbackData.amount as string) || 0;

    // Find user
    const user = await User.findByPk(userId);
    if (!user) {
      return { success: false, error: 'User not found' };
    }

    // Find offer by external ID
    const offer = await Offer.findOne({
      where: { 
        externalOfferId: offerId,
        provider: 'lootably',
        isActive: true,
      },
    });

    if (!offer) {
      return { success: false, error: 'Offer not found' };
    }

    // Find or create user offer
    let userOffer = await UserOffer.findOne({
      where: { userId, offerId: offer.id },
    });

    if (!userOffer) {
      userOffer = await UserOffer.create({
        userId,
        offerId: offer.id,
        status: 'started',
        rewardAmount: amount,
      });
    }

    // Update user offer status
    await userOffer.update({
      status: status === 'completed' ? 'completed' : 'in_progress',
      completedAt: status === 'completed' ? new Date() : null,
    });

    // If completed, add earning and update user balance
    if (status === 'completed' && userOffer.status === 'completed') {
      // Add earning
      await Earning.create({
        userId,
        userOfferId: userOffer.id,
        amount,
        type: 'task_completion',
        description: `Completed Lootably offer: ${offer.title}`,
      });

      // Update user balance and stats
      await user.update({
        balance: user.balance + amount,
        totalEarned: user.totalEarned + amount,
        tasksCompleted: user.tasksCompleted + 1,
      });
    }

    return { success: true };
  } catch (error) {
    console.error('Error processing Lootably postback:', error);
    return { success: false, error: 'Processing failed' };
  }
}

// Sync offers from Lootably (admin endpoint)
router.post('/sync', async (req: Request, res: Response) => {
  try {
    // This would integrate with Lootably API to sync offers
    // For now, we'll create some demo offers
    
    const demoOffers = [
      {
        title: 'Complete Survey - Gaming',
        description: 'Take a 5-minute survey about gaming preferences',
        provider: 'lootably',
        category: 'survey',
        rewardAmount: 2.0,
        userPayout: 1.0,
        timeEstimate: '5 mins',
        externalOfferId: 'lootably_survey_001',
      },
      {
        title: 'Download Mobile App',
        description: 'Download and try our mobile app for 30 seconds',
        provider: 'lootably',
        category: 'app',
        rewardAmount: 1.5,
        userPayout: 0.75,
        timeEstimate: '2 mins',
        externalOfferId: 'lootably_app_001',
      },
      {
        title: 'Sign Up for Newsletter',
        description: 'Subscribe to our newsletter for exclusive offers',
        provider: 'lootably',
        category: 'signup',
        rewardAmount: 1.0,
        userPayout: 0.5,
        timeEstimate: '1 min',
        externalOfferId: 'lootably_signup_001',
      },
    ];

    let syncedCount = 0;
    for (const demoOffer of demoOffers) {
      const existingOffer = await Offer.findOne({
        where: { externalOfferId: demoOffer.externalOfferId },
      });

      if (!existingOffer) {
        await Offer.create(demoOffer);
        syncedCount++;
      }
    }

    res.json({
      success: true,
      message: `Successfully synchronized ${syncedCount} offers from Lootably`,
      syncedCount,
    });
  } catch (error) {
    console.error('Sync offers error:', error);
    res.status(500).json({ error: 'Failed to sync offers' });
  }
});

export default router;
