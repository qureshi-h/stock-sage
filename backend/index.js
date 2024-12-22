// index.js
const cors = require('cors');
const express = require('express');
const app = express();

const allowedOrigins = ['http://localhost:3000', 'https://trading-edge.netlify.app'];

app.use(
    cors({
        origin: (origin, callback) => {
            // Allow requests with no origin (like mobile apps or curl requests)
            if (!origin || allowedOrigins.includes(origin)) {
                callback(null, true);
            } else {
                callback(new Error('Not allowed by CORS'));
            }
        },
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        credentials: true,
    }),
);

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
