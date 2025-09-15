# OfferEarner - Complete Integration System

A modern TypeScript/Node.js web application for managing offerwall integrations, user earnings, and PayPal payouts.

## Features

- **User Authentication**: Secure JWT-based authentication system
- **Offer Management**: Browse and complete offers from various providers
- **Earnings Tracking**: Real-time tracking of user earnings and balance
- **PayPal Integration**: Direct PayPal payouts with minimum $5 threshold
- **Lootably Integration**: Complete offerwall integration with callbacks
- **Dashboard**: Comprehensive user dashboard with statistics
- **Admin Panel**: Platform management and analytics
- **Responsive Design**: Modern, mobile-friendly UI with dark/light themes

## Tech Stack

- **Backend**: Node.js, Express.js, TypeScript
- **Database**: SQLite with Sequelize ORM
- **Authentication**: JWT with bcrypt password hashing
- **Frontend**: EJS templates with vanilla JavaScript
- **Styling**: Modern CSS with CSS variables and responsive design
- **Payments**: PayPal REST API integration
- **Security**: Helmet.js, rate limiting, CORS protection

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd offerearner
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Build the application**
   ```bash
   npm run build
   ```

5. **Start the server**
   ```bash
   npm start
   ```

   For development with auto-reload:
   ```bash
   npm run dev
   ```

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Database Configuration
DATABASE_URL=sqlite:./offerwall.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
PORT=8001
NODE_ENV=development

# PayPal Configuration (optional)
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox

# Lootably Configuration (optional)
LOOTABLY_API_KEY=your-lootably-api-key
LOOTABLY_SECRET_KEY=your-lootably-secret-key
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Dashboard
- `GET /api/dashboard/stats` - Get user statistics
- `GET /api/dashboard/activity` - Get recent activity
- `GET /api/dashboard/earnings` - Get earnings history
- `GET /api/dashboard/offers` - Get offer history

### Offers
- `GET /api/offers` - List available offers
- `GET /api/offers/:id` - Get offer details
- `POST /api/offers/:id/start` - Start an offer
- `POST /api/offers/:id/complete` - Complete an offer
- `GET /api/offers/categories` - Get offer categories
- `GET /api/offers/providers` - Get offer providers

### Payouts
- `POST /api/payouts/request` - Request PayPal payout
- `GET /api/payouts/history` - Get payout history
- `GET /api/payouts/info` - Get payout information

### Lootably Integration
- `GET /api/callback/lootably` - Handle Lootably callbacks
- `POST /api/callback/lootably/sync` - Sync offers from Lootably

### Admin
- `GET /api/admin/platform-stats` - Get platform statistics
- `GET /api/admin/payouts/stats` - Get payout statistics
- `GET /api/admin/recent-activity` - Get recent activity
- `POST /api/admin/sync-lootably-offers` - Sync Lootably offers

## Web Pages

- `/` - Homepage
- `/register` - User registration
- `/login` - User login
- `/dashboard` - User dashboard
- `/offers` - Browse offers

## Database Schema

### Users
- Basic user information (username, email, password)
- PayPal email for payouts
- Balance and earnings tracking
- Task completion statistics

### Offers
- Offer details (title, description, requirements)
- Provider and category classification
- Reward amounts (full and user payout)
- External offer IDs for tracking

### UserOffers
- User-offer relationships
- Progress tracking and status
- Completion timestamps
- Reward amounts

### Earnings
- Individual earning records
- Type classification (task_completion, bonus, referral)
- Amount and description
- Timestamps

### Payouts
- Payout requests and status
- Payment method and details
- Transaction tracking
- Processing timestamps

### OfferCallbacks
- External callback data storage
- Provider-specific information
- Processing status tracking

## Deployment

### Production Deployment

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Set production environment**
   ```bash
   export NODE_ENV=production
   ```

3. **Start the server**
   ```bash
   npm start
   ```

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist
COPY public ./public
COPY views ./views

EXPOSE 8001

CMD ["node", "dist/server.js"]
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Development

### Scripts

- `npm run dev` - Start development server with auto-reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Project Structure

```
src/
├── database/          # Database models and configuration
├── middleware/        # Express middleware (auth, etc.)
├── routes/           # API route handlers
├── types/            # TypeScript type definitions
└── server.ts         # Main application entry point

views/                # EJS templates
├── base.ejs         # Base template
├── index.ejs        # Homepage
├── register.ejs     # Registration page
├── login.ejs        # Login page
├── dashboard.ejs    # User dashboard
├── offers.ejs       # Offers page
└── partials/        # Template partials

public/              # Static assets
├── css/
│   └── style.css   # Main stylesheet
└── js/
    ├── theme.js    # Theme management
    └── auth.js     # Authentication helpers
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing
- **Rate Limiting**: Protection against brute force attacks
- **CORS Protection**: Cross-origin request protection
- **Helmet.js**: Security headers
- **Input Validation**: Express-validator for request validation
- **SQL Injection Protection**: Sequelize ORM with parameterized queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions, please open an issue on GitHub or contact the development team.

---

**Note**: This application is designed for educational and development purposes. For production use, ensure proper security measures, SSL certificates, and compliance with relevant regulations.