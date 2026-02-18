-- Smart Billing System - Supabase Database Setup
-- Run this SQL in your Supabase SQL Editor

-- Create menu_items table
CREATE TABLE IF NOT EXISTS menu_items (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  category VARCHAR(100),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create bills table
CREATE TABLE IF NOT EXISTS bills (
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date DESC);
CREATE INDEX IF NOT EXISTS idx_menu_active ON menu_items(is_active);

-- Insert default menu items (only if table is empty)
INSERT INTO menu_items (name, price, category) 
SELECT 'Coffee', 50, 'Beverages' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Coffee');

INSERT INTO menu_items (name, price, category) 
SELECT 'Tea', 30, 'Beverages' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Tea');

INSERT INTO menu_items (name, price, category) 
SELECT 'Sandwich', 70, 'Food' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Sandwich');

INSERT INTO menu_items (name, price, category) 
SELECT 'Burger', 90, 'Food' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Burger');

INSERT INTO menu_items (name, price, category) 
SELECT 'Fries', 60, 'Snacks' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Fries');

INSERT INTO menu_items (name, price, category) 
SELECT 'Pizza', 120, 'Food' 
WHERE NOT EXISTS (SELECT 1 FROM menu_items WHERE name = 'Pizza');

-- Enable Row Level Security (RLS) for production use
-- ALTER TABLE menu_items ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bills ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (optional)
-- CREATE POLICY "Enable read access for all users" ON menu_items
--   FOR SELECT USING (true);
--
-- CREATE POLICY "Enable insert for all users" ON menu_items
--   FOR INSERT WITH CHECK (true);
--
-- CREATE POLICY "Enable read access for all users" ON bills
--   FOR SELECT USING (true);
--
-- CREATE POLICY "Enable insert for all users" ON bills
--   FOR INSERT WITH CHECK (true);
