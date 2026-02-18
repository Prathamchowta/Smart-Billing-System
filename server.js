const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const bodyParser = require('body-parser');

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize Supabase
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

function parseDateRange(query) {
  const { from, to } = query || {};
  const out = {};

  if (from) {
    const d = new Date(from);
    if (!Number.isNaN(d.getTime())) {
      d.setUTCHours(0, 0, 0, 0);
      out.from = d.toISOString();
    }
  }

  if (to) {
    const d = new Date(to);
    if (!Number.isNaN(d.getTime())) {
      d.setUTCHours(23, 59, 59, 999);
      out.to = d.toISOString();
    }
  }

  return out;
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Server is running' });
});

// ===== Menu Routes =====
app.get('/api/menu', async (req, res) => {
  try {
    const { data: menu, error } = await supabase
      .from('menu_items')
      .select('*')
      .eq('is_active', true);

    if (error) throw error;

    res.json({ success: true, data: menu });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/menu', async (req, res) => {
  try {
    const { name, price, category } = req.body;

    if (!name || !price) {
      return res.status(400).json({ success: false, error: 'Name and price are required' });
    }

    const { data, error } = await supabase
      .from('menu_items')
      .insert([{ name, price, category, is_active: true }])
      .select();

    if (error) throw error;

    res.json({ success: true, data: data[0] });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.put('/api/menu/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, price, category, is_active } = req.body;

    const updateData = {};
    if (name !== undefined) updateData.name = name;
    if (price !== undefined) updateData.price = price;
    if (category !== undefined) updateData.category = category;
    if (is_active !== undefined) updateData.is_active = is_active;

    if (Object.keys(updateData).length === 0) {
      return res.status(400).json({ success: false, error: 'No fields provided to update' });
    }

    const { data, error } = await supabase
      .from('menu_items')
      .update(updateData)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== Billing Routes =====
app.post('/api/bills', async (req, res) => {
  try {
    const { customer_name, items, tax_rate = 0.05, service_charge = 20, total_amount, notes } = req.body;

    if (!items || items.length === 0) {
      return res.status(400).json({ success: false, error: 'Items are required' });
    }

    const bill_date = new Date().toISOString();
    const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const tax = subtotal * tax_rate;
    const final_total = subtotal + tax + service_charge;

    const { data, error } = await supabase
      .from('bills')
      .insert([{
        customer_name,
        bill_date,
        subtotal,
        tax,
        service_charge,
        total_amount: final_total,
        notes,
        items: items
      }])
      .select();

    if (error) throw error;

    res.json({ success: true, data: data[0] });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/bills', async (req, res) => {
  try {
    const { from, to } = parseDateRange(req.query);
    let q = supabase
      .from('bills')
      .select('*')
      .order('bill_date', { ascending: false });

    if (from) q = q.gte('bill_date', from);
    if (to) q = q.lte('bill_date', to);

    const { data: bills, error } = await q;

    if (error) throw error;

    res.json({ success: true, data: bills });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.delete('/api/bills/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { data, error } = await supabase
      .from('bills')
      .delete()
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/bills/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const { data: bill, error } = await supabase
      .from('bills')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;

    res.json({ success: true, data: bill });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== Analytics Routes =====
app.get('/api/analytics/summary', async (req, res) => {
  try {
    const { from, to } = parseDateRange(req.query);
    let q = supabase
      .from('bills')
      .select('total_amount, bill_date');

    if (from) q = q.gte('bill_date', from);
    if (to) q = q.lte('bill_date', to);

    const { data: bills, error } = await q;

    if (error) throw error;

    const totalRevenue = bills.reduce((sum, bill) => sum + bill.total_amount, 0);
    const totalBills = bills.length;
    const averageBill = totalBills > 0 ? totalRevenue / totalBills : 0;

    res.json({
      success: true,
      data: {
        total_revenue: totalRevenue,
        total_bills: totalBills,
        average_bill: averageBill
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/analytics/items-sold', async (req, res) => {
  try {
    const { from, to } = parseDateRange(req.query);
    let q = supabase
      .from('bills')
      .select('items, bill_date');

    if (from) q = q.gte('bill_date', from);
    if (to) q = q.lte('bill_date', to);

    const { data: bills, error } = await q;

    if (error) throw error;

    const itemStats = {};
    bills.forEach(bill => {
      if (bill.items && Array.isArray(bill.items)) {
        bill.items.forEach(item => {
          if (!itemStats[item.name]) {
            itemStats[item.name] = { name: item.name, quantity: 0, revenue: 0 };
          }
          itemStats[item.name].quantity += item.quantity;
          itemStats[item.name].revenue += item.price * item.quantity;
        });
      }
    });

    const result = Object.values(itemStats).sort((a, b) => b.quantity - a.quantity);

    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== Profit Prediction Routes =====
app.get('/api/analytics/predict-profit', async (req, res) => {
  try {
    const { from, to } = parseDateRange(req.query);
    let q = supabase
      .from('bills')
      .select('total_amount, bill_date')
      .order('bill_date', { ascending: true });

    if (from) q = q.gte('bill_date', from);
    if (to) q = q.lte('bill_date', to);

    const { data: bills, error } = await q;

    if (error) throw error;

    // Simple prediction: average of last 7 days or all bills if less
    const recentBills = bills.slice(-7);
    const avgDaily = recentBills.length > 0
      ? recentBills.reduce((sum, bill) => sum + bill.total_amount, 0) / recentBills.length
      : 0;

    const predictedMonthly = avgDaily * 30;

    res.json({
      success: true,
      data: {
        predicted_daily: avgDaily,
        predicted_monthly: predictedMonthly,
        based_on_days: recentBills.length
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
