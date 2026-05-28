# MercadoPago Webhook Server Setup Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

FastAPI, uvicorn, and requests have been added to requirements.txt automatically.

## Environment Variables

Set these environment variables in your shell or deployment:

```env
# MercadoPago Configuration
MERCADOPAGO_ACCESS_TOKEN=your_mercadopago_access_token_here

# Database Configuration (already configured)
DATABASE_URL=postgresql://user:password@localhost:5432/barberia_db
# Or
SUPABASE_DB_URL=postgresql://user:password@your-supabase-host/your_db

# Webhook Server Configuration (optional)
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
WEBHOOK_RELOAD=False  # Set to True for development
WEBHOOK_SECRET=your_webhook_secret_optional
```

## Database Schema

Ensure your `reservas` table has these columns:

```sql
ALTER TABLE reservas ADD COLUMN IF NOT EXISTS payment_id VARCHAR(255);
ALTER TABLE reservas ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_reservas_payment_id ON reservas(payment_id);
```

## Running the Webhook Server

### Development Mode:
```bash
python webhook.py
```

Server will start on `http://0.0.0.0:8000`

### Production Mode (with Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker webhook:app --bind 0.0.0.0:8000
```

## API Endpoints

- **GET /health** - Health check endpoint
- **GET /docs** - Interactive API documentation (Swagger)
- **POST /webhook** - MercadoPago payment notification webhook
- **POST /webhook/test** - Test endpoint for debugging

## Configuration in MercadoPago

1. Go to [https://www.mercadopago.cl/developers/panel](https://www.mercadopago.cl/developers/panel)
2. Navigate to **Webhooks** section
3. Add webhook URL: `https://your-domain.com/webhook`
4. Select event type: **Payment**
5. MercadoPago will send POST requests to your webhook when payments are received

## Webhook Flow

1. **Payment Creation** (in app.py):
   ```python
   # When creating payment, set external_reference to reserva_id
   preference = {
       "external_reference": str(reserva_id),  # ← This links to webhook
       ...
   }
   ```

2. **Payment Completion** (MercadoPago → Your Webhook):
   - User completes payment on MercadoPago
   - MercadoPago sends notification to `/webhook`

3. **Webhook Processing**:
   - Receives notification with payment ID
   - Fetches payment details from MercadoPago API
   - Checks if status == "approved"
   - Updates `reservas.pagado = TRUE` using `external_reference` (reserva_id)

4. **Status Tracking**:
   - Supported statuses: approved, pending, rejected, cancelled
   - Only "approved" status sets `pagado = TRUE`
   - Other statuses still update the record for tracking

## Integration with app.py

Update the payment creation in `app.py` to ensure `external_reference` is set:

```python
# In crear_pago_mercadopago() function around line 884
preference = {
    "external_reference": str(reserva_id),  # ← CRITICAL: Links webhook to reservation
    "items": [...],
    "payer": {...},
    ...
}
```

## Testing the Webhook

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Test Webhook Endpoint
```bash
curl -X POST http://localhost:8000/webhook/test
```

### Test 3: Simulate MercadoPago Notification (for debugging)
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "id": "999999999",
    "data": {}
  }'
```

**Note**: This will fail if payment ID doesn't exist in MercadoPago API, but shows webhook is working.

## Logging

Webhook logs are written to:
- **Console**: Real-time output during execution
- **File**: `webhook.log` in the application directory

View logs:
```bash
tail -f webhook.log
```

## Error Handling

The webhook handles:
- ✅ Missing/invalid JSON payload
- ✅ Invalid external_reference format
- ✅ MercadoPago API errors (timeouts, HTTP errors)
- ✅ Database connection failures
- ✅ Database transaction conflicts
- ✅ Missing configuration (tokens, database URL)

All errors are logged with timestamps and details for debugging.

## Running Multiple Services

If running the Streamlit app and webhook simultaneously:

**Terminal 1** - Streamlit App:
```bash
streamlit run app.py
```

**Terminal 2** - Webhook Server:
```bash
python webhook.py
```

Or use different ports:
```bash
# Streamlit default: 8501
# Webhook: 8000 (set in webhook.py or --server.port)
```

## Deployment Considerations

### For Production:

1. **Use environment variables** for sensitive data
2. **Enable HTTPS** (required by MercadoPago for webhooks)
3. **Use reverse proxy** (Nginx) with SSL/TLS
4. **Monitor webhook logs** for payment failures
5. **Set up database backups** before going live
6. **Test with MercadoPago Sandbox** first

### Nginx Configuration Example:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Issue: "MERCADOPAGO_ACCESS_TOKEN not configured"
**Solution**: Set the token as an environment variable and restart webhook server

### Issue: "Could not connect to database"
**Solution**: Check DATABASE_URL is correct and PostgreSQL is running

### Issue: "Reservation not found in database"
**Solution**: Ensure `external_reference` matches actual `reserva_id` in database

### Issue: Webhook not being called
**Solution**: 
1. Verify webhook URL in MercadoPago dashboard
2. Check firewall allows incoming connections
3. Enable HTTPS if required by MercadoPago
4. Test with `/webhook/test` endpoint

## Security Notes

- ⚠️ Always use HTTPS in production (MercadoPago requirement)
- ⚠️ Validate external_reference before database operations
- ⚠️ Implement rate limiting for production deployments
- ⚠️ Store MERCADOPAGO_ACCESS_TOKEN in environment, never in code
- ⚠️ Use connection pooling to prevent database exhaustion
- ⚠️ Log all payment activities for audit trail

## Next Steps

1. Set MERCADOPAGO_ACCESS_TOKEN as an environment variable
2. Update database schema (add payment_id, updated_at columns)
3. Verify external_reference is set in app.py's crear_pago_mercadopago()
4. Run webhook server: `python webhook.py`
5. Configure webhook URL in MercadoPago dashboard
6. Test payment flow end-to-end
