// index.js
const express = require('express');
const stockRoutes = require('./routes/stocks');
const tradeRoutes = require('./routes/trades');

require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use('/api/stocks', stockRoutes);
app.use('/api/trades', tradeRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
