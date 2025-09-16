# OfferEarner - Complete Integration System

A modern TypeScript/Node.js web application for managing offerwall integrations, user earnings, and PayPal payouts. Includes a complete Python/FastAPI version for reference and testing.

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

### Primary Application (Node.js/TypeScript)
- **Backend**: Node.js, Express.js, TypeScript
- **Database**: SQLite with Sequelize ORM
- **Authentication**: JWT with bcrypt password hashing
- **Frontend**: EJS templates with vanilla JavaScript
- **Styling**: Modern CSS with CSS variables and responsive design
- **Payments**: PayPal REST API integration
- **Security**: Helmet.js, rate limiting, CORS protection

### Reference Implementation (Python/FastAPI)
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt password hashing
- **Frontend**: Jinja2 templates
- **Payments**: PayPal REST API integration

## Quick Start

### Prerequisites

- Node.js 18+ (for main application)
- Python 3.8+ (for reference Python version)
- npm or yarn

### Installation (Node.js Version)

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

### Installation (Python Version - Reference)

The Python version is located in the [`python-version/`](python-version/) directory and serves as a reference implementation:

```bash
cd python-version
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python start.py
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

## Project Structure

```
offerearner/
├── src/                    # TypeScript source code
│   ├── database/          # Database models and configuration
│   ├── middleware/        # Express middleware (auth, etc.)
│   ├── routes/           # API route handlers
│   ├── types/            # TypeScript type definitions
│   └── server.ts         # Main application entry point
├── views/                # EJS templates
├── public/              # Static assets (CSS, JS)
├── python-version/       # Python/FastAPI reference implementation
│   ├── auth.py          # Authentication module
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   ├── templates/       # Jinja2 templates
│   ├── static/         # Static assets
│   └── start.py         # FastAPI application entry point
├── package.json         # Node.js dependencies
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
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

## Deployment

### Deployment

For comprehensive deployment instructions covering both Node.js and Python versions, see [`COMPREHENSIVE_DEPLOYMENT_GUIDE.md`](COMPREHENSIVE_DEPLOYMENT_GUIDE.md).

## Development

### Scripts (Node.js)

- `npm run dev` - Start development server with auto-reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Running Python Version
```bash
cd python-version
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python start.py
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