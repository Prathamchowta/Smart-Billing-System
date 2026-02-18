# Smart Billing System - Web-Based

A modern web-based billing system built with React, Node.js, and Supabase. Originally a desktop application using customtkinter, now converted to a full-stack web application.

## Features

- **Modern Web Interface**: Built with React and React Router
- **Real-time Billing**: Create and manage bills in real-time
- **Menu Management**: Add and manage menu items
- **Analytics Dashboard**: Track revenue, sales trends, and profit predictions
- **Cloud Database**: Using Supabase (PostgreSQL) for data persistence
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **PDF Generation**: Print and download bills

## Tech Stack

### Frontend
- React 18
- React Router v6
- Axios for API calls
- Recharts for analytics
- React Icons for UI icons

### Backend
- Node.js with Express
- Supabase JavaScript SDK
- CORS enabled for frontend communication

### Database
- Supabase (PostgreSQL)

## Project Structure

```
Smart_Billing_System/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/           # Page components (Home, Billing, Menu, Analytics)
│   │   ├── services/        # API service layer
│   │   ├── styles/          # CSS styling
│   │   ├── App.js           # Main App component
│   │   └── index.js         # React entry point
│   ├── public/              # Static files
│   └── package.json         # Frontend dependencies
│
├── backend/                  # Node.js/Express backend
│   ├── server.js            # Main server file with API routes
│   ├── package.json         # Backend dependencies
│   └── .env.example         # Environment variables example
│
├── Billing-System/          # Original desktop application (legacy)
│
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Supabase account (free tier available at https://supabase.com)

### Step 1: Setup Supabase Database

1. Create a Supabase project at https://supabase.com
2. In your Supabase dashboard, go to SQL Editor
3. Run the following SQL to create the database schema:

```sql
-- Create menu_items table
CREATE TABLE menu_items (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  category VARCHAR(100),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create bills table
CREATE TABLE bills (
  id BIGSERIAL PRIMARY KEY,
  customer_name VARCHAR(255),
  bill_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  subtotal DECIMAL(10, 2) NOT NULL,
  tax DECIMAL(10, 2) DEFAULT 0,
  service_charge DECIMAL(10, 2) DEFAULT 0,
  total_amount DECIMAL(10, 2) NOT NULL,
  notes TEXT,
  items JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default menu items
INSERT INTO menu_items (name, price, category) VALUES
('Coffee', 50, 'Beverages'),
('Tea', 30, 'Beverages'),
('Sandwich', 70, 'Food'),
('Burger', 90, 'Food'),
('Fries', 60, 'Snacks'),
('Pizza', 120, 'Food');

-- Create indexes for performance
CREATE INDEX idx_bills_date ON bills(bill_date DESC);
CREATE INDEX idx_menu_active ON menu_items(is_active);
```

4. Get your Supabase credentials:
   - Go to Project Settings → API
   - Copy your Project URL and Anon Key

### Step 2: Setup Backend

```bash
cd backend
npm install

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
# SUPABASE_URL=your_project_url
# SUPABASE_ANON_KEY=your_anon_key
```

Start the backend server:
```bash
npm run dev
```

The backend will run on `http://localhost:5000`

### Step 3: Setup Frontend

```bash
cd frontend
npm install

# Create .env file
cp .env.example .env

# Edit .env with your configuration
# REACT_APP_API_URL=http://localhost:5000
# REACT_APP_SUPABASE_URL=your_project_url
# REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

Start the frontend development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## API Endpoints

### Menu Routes
- `GET /api/menu` - Get all menu items
- `POST /api/menu` - Add new menu item

### Billing Routes
- `POST /api/bills` - Create new bill
- `GET /api/bills` - Get all bills
- `GET /api/bills/:id` - Get specific bill

### Analytics Routes
- `GET /api/analytics/summary` - Get revenue summary
- `GET /api/analytics/items-sold` - Get items sales data
- `GET /api/analytics/predict-profit` - Get profit prediction

## Features Overview

### Dashboard
- View total revenue
- View total number of bills
- View average bill amount
- See recent bills

### Billing
- Select items from menu
- Add quantities
- View real-time bill total with tax and service charge
- Customer name field
- Notes section
- Generate and print bill as PDF

### Menu Management
- View all menu items
- Add new items
- Set prices
- Categorize items

### Analytics
- Revenue distribution by item
- Top selling items
- Profit prediction based on historical data
- Visual charts and graphs

## Environment Variables

### Backend (.env)
```
PORT=5000
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
NODE_ENV=development
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Running in Production

### Backend Production
```bash
npm install
NODE_ENV=production npm start
```

### Frontend Production Build
```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## Deployment Options

- **Frontend**: Deploy to Vercel, Netlify, or GitHub Pages
- **Backend**: Deploy to Heroku, Railway, or AWS Lambda
- **Database**: Supabase handles hosting (PostgreSQL database)

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure the backend is running and the `REACT_APP_API_URL` in frontend `.env` matches your backend URL.

### Database Connection Issues
Check your Supabase credentials in the `.env` file. Ensure your Supabase project is active.

### Port Already in Use
- Backend: Change PORT in `.env`
- Frontend: Run `PORT=3001 npm start`

## Future Enhancements

- User authentication and login
- Role-based access control (Admin, Staff, Manager)
- Advanced analytics and reporting
- Email bill delivery
- Multiple language support
- Dark mode
- Mobile app using React Native

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
