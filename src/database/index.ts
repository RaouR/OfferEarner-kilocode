import { Sequelize, DataTypes, Model, Optional } from 'sequelize';
import dotenv from 'dotenv';

dotenv.config();

const DATABASE_URL = process.env.DATABASE_URL || 'sqlite:./offerwall.db';

export const sequelize = new Sequelize(DATABASE_URL, {
  dialect: DATABASE_URL.startsWith('sqlite') ? 'sqlite' : 'postgres',
  logging: process.env.NODE_ENV === 'development' ? console.log : false,
  define: {
    timestamps: true,
    underscored: true,
  },
});

// User Model
export interface UserAttributes {
  id: number;
  username: string;
  email: string;
  hashedPassword: string;
  paypalEmail: string;
  balance: number;
  totalEarned: number;
  tasksCompleted: number;
  isActive: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface UserCreationAttributes extends Optional<UserAttributes, 'id' | 'balance' | 'totalEarned' | 'tasksCompleted' | 'isActive'> {}

export class User extends Model<UserAttributes, UserCreationAttributes> implements UserAttributes {
  public id!: number;
  public username!: string;
  public email!: string;
  public hashedPassword!: string;
  public paypalEmail!: string;
  public balance!: number;
  public totalEarned!: number;
  public tasksCompleted!: number;
  public isActive!: boolean;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

User.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    username: {
      type: DataTypes.STRING(50),
      allowNull: false,
      unique: true,
    },
    email: {
      type: DataTypes.STRING(100),
      allowNull: false,
      unique: true,
    },
    hashedPassword: {
      type: DataTypes.STRING(200),
      allowNull: false,
    },
    paypalEmail: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    balance: {
      type: DataTypes.FLOAT,
      defaultValue: 0.0,
    },
    totalEarned: {
      type: DataTypes.FLOAT,
      defaultValue: 0.0,
    },
    tasksCompleted: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true,
    },
  },
  {
    sequelize,
    tableName: 'users',
  }
);

// Offer Model
export interface OfferAttributes {
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
  createdAt?: Date;
  updatedAt?: Date;
}

export interface OfferCreationAttributes extends Optional<OfferAttributes, 'id' | 'isActive'> {}

export class Offer extends Model<OfferAttributes, OfferCreationAttributes> implements OfferAttributes {
  public id!: number;
  public title!: string;
  public description!: string;
  public provider!: string;
  public category!: string;
  public rewardAmount!: number;
  public userPayout!: number;
  public timeEstimate?: string;
  public requirements?: any;
  public externalOfferId?: string;
  public callbackUrl?: string;
  public isActive!: boolean;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

Offer.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    title: {
      type: DataTypes.STRING(200),
      allowNull: false,
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    provider: {
      type: DataTypes.STRING(50),
      allowNull: false,
    },
    category: {
      type: DataTypes.STRING(50),
      allowNull: false,
    },
    rewardAmount: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
    userPayout: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
    timeEstimate: {
      type: DataTypes.STRING(20),
    },
    requirements: {
      type: DataTypes.JSON,
    },
    externalOfferId: {
      type: DataTypes.STRING(100),
    },
    callbackUrl: {
      type: DataTypes.STRING(500),
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true,
    },
  },
  {
    sequelize,
    tableName: 'offers',
  }
);

// UserOffer Model
export interface UserOfferAttributes {
  id: number;
  userId: number;
  offerId: number;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  progressData?: any;
  startedAt: Date;
  completedAt?: Date;
  rewardAmount?: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface UserOfferCreationAttributes extends Optional<UserOfferAttributes, 'id' | 'status' | 'startedAt'> {}

export class UserOffer extends Model<UserOfferAttributes, UserOfferCreationAttributes> implements UserOfferAttributes {
  public id!: number;
  public userId!: number;
  public offerId!: number;
  public status!: 'started' | 'in_progress' | 'completed' | 'failed';
  public progressData?: any;
  public startedAt!: Date;
  public completedAt?: Date;
  public rewardAmount?: number;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

UserOffer.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: User,
        key: 'id',
      },
    },
    offerId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: Offer,
        key: 'id',
      },
    },
    status: {
      type: DataTypes.ENUM('started', 'in_progress', 'completed', 'failed'),
      defaultValue: 'started',
    },
    progressData: {
      type: DataTypes.JSON,
    },
    startedAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
    completedAt: {
      type: DataTypes.DATE,
    },
    rewardAmount: {
      type: DataTypes.FLOAT,
    },
  },
  {
    sequelize,
    tableName: 'user_offers',
  }
);

// Earning Model
export interface EarningAttributes {
  id: number;
  userId: number;
  userOfferId?: number;
  amount: number;
  type: 'task_completion' | 'bonus' | 'referral';
  description: string;
  createdAt?: Date;
}

export interface EarningCreationAttributes extends Optional<EarningAttributes, 'id'> {}

export class Earning extends Model<EarningAttributes, EarningCreationAttributes> implements EarningAttributes {
  public id!: number;
  public userId!: number;
  public userOfferId?: number;
  public amount!: number;
  public type!: 'task_completion' | 'bonus' | 'referral';
  public description!: string;
  public readonly createdAt!: Date;
}

Earning.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: User,
        key: 'id',
      },
    },
    userOfferId: {
      type: DataTypes.INTEGER,
      references: {
        model: UserOffer,
        key: 'id',
      },
    },
    amount: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
    type: {
      type: DataTypes.ENUM('task_completion', 'bonus', 'referral'),
      allowNull: false,
    },
    description: {
      type: DataTypes.STRING(500),
      allowNull: false,
    },
  },
  {
    sequelize,
    tableName: 'earnings',
  }
);

// Payout Model
export interface PayoutAttributes {
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
  createdAt?: Date;
  updatedAt?: Date;
}

export interface PayoutCreationAttributes extends Optional<PayoutAttributes, 'id' | 'status' | 'requestedAt'> {}

export class Payout extends Model<PayoutAttributes, PayoutCreationAttributes> implements PayoutAttributes {
  public id!: number;
  public userId!: number;
  public amount!: number;
  public method!: 'paypal' | 'gift_card' | 'crypto';
  public status!: 'pending' | 'processing' | 'completed' | 'failed';
  public paymentDetails?: any;
  public requestedAt!: Date;
  public processedAt?: Date;
  public transactionId?: string;
  public notes?: string;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

Payout.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: User,
        key: 'id',
      },
    },
    amount: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
    method: {
      type: DataTypes.ENUM('paypal', 'gift_card', 'crypto'),
      allowNull: false,
    },
    status: {
      type: DataTypes.ENUM('pending', 'processing', 'completed', 'failed'),
      defaultValue: 'pending',
    },
    paymentDetails: {
      type: DataTypes.JSON,
    },
    requestedAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
    processedAt: {
      type: DataTypes.DATE,
    },
    transactionId: {
      type: DataTypes.STRING(100),
    },
    notes: {
      type: DataTypes.TEXT,
    },
  },
  {
    sequelize,
    tableName: 'payouts',
  }
);

// OfferCallback Model
export interface OfferCallbackAttributes {
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
  createdAt?: Date;
}

export interface OfferCallbackCreationAttributes extends Optional<OfferCallbackAttributes, 'id' | 'processed'> {}

export class OfferCallback extends Model<OfferCallbackAttributes, OfferCallbackCreationAttributes> implements OfferCallbackAttributes {
  public id!: number;
  public provider!: string;
  public userId?: number;
  public externalOfferId?: string;
  public externalUserId?: string;
  public status?: string;
  public rewardAmount?: number;
  public callbackData?: any;
  public processed!: boolean;
  public processedAt?: Date;
  public readonly createdAt!: Date;
}

OfferCallback.init(
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    provider: {
      type: DataTypes.STRING(50),
      allowNull: false,
    },
    userId: {
      type: DataTypes.INTEGER,
      references: {
        model: User,
        key: 'id',
      },
    },
    externalOfferId: {
      type: DataTypes.STRING(100),
    },
    externalUserId: {
      type: DataTypes.STRING(100),
    },
    status: {
      type: DataTypes.STRING(20),
    },
    rewardAmount: {
      type: DataTypes.FLOAT,
    },
    callbackData: {
      type: DataTypes.JSON,
    },
    processed: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },
    processedAt: {
      type: DataTypes.DATE,
    },
  },
  {
    sequelize,
    tableName: 'offer_callbacks',
  }
);

// Define associations
User.hasMany(UserOffer, { foreignKey: 'userId', as: 'userOffers' });
UserOffer.belongsTo(User, { foreignKey: 'userId', as: 'user' });

User.hasMany(Earning, { foreignKey: 'userId', as: 'earnings' });
Earning.belongsTo(User, { foreignKey: 'userId', as: 'user' });

User.hasMany(Payout, { foreignKey: 'userId', as: 'payouts' });
Payout.belongsTo(User, { foreignKey: 'userId', as: 'user' });

Offer.hasMany(UserOffer, { foreignKey: 'offerId', as: 'userOffers' });
UserOffer.belongsTo(Offer, { foreignKey: 'offerId', as: 'offer' });

UserOffer.hasOne(Earning, { foreignKey: 'userOfferId', as: 'earning' });
Earning.belongsTo(UserOffer, { foreignKey: 'userOfferId', as: 'userOffer' });

// Database initialization function
export async function initDatabase(): Promise<void> {
  try {
    await sequelize.authenticate();
    console.log('Database connection established successfully.');
    
    await sequelize.sync({ alter: true });
    console.log('Database synchronized successfully.');
  } catch (error) {
    console.error('Unable to connect to the database:', error);
    throw error;
  }
}

export default sequelize;
