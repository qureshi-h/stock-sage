// index.js
const cors = require('cors');
const express = require('express');
const app = express();

// Configure CORS
app.use(cors({
    origin: 'http://localhost:3000', // Allow requests from this origin
    methods: ['GET', 'POST', 'PUT', 'DELETE'], // Allowed methods
    credentials: true, // Include credentials (if needed)
}));

const stockRoutes = require('./routes/stocks');
const tradeRoutes = require('./routes/trades');

require('dotenv').config();

const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use('/api/stocks', stockRoutes);
app.use('/api/trades', tradeRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
