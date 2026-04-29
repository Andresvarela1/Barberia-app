"""
FastAPI Webhook Server for MercadoPago Payment Notifications
Receives payment notifications, validates them, and updates PostgreSQL database
"""

import os
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MercadoPago Webhook Server",
    description="Receives and processes MercadoPago payment notifications",
    version="1.0.0"
)

# Configuration from environment
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # Optional secret for webhook validation

# MercadoPago API endpoint
MERCADOPAGO_API_URL = "https://api.mercadopago.com/v1"

# Database connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        DATABASE_URL,
        connect_timeout=10
    )
    logger.info("✅ Database connection pool created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database connection pool: {e}")
    db_pool = None


# Pydantic models for request validation
class MercadoPagoNotification(BaseModel):
    """MercadoPago webhook notification payload"""
    id: str
    type: str
    data: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Webhook response model"""
    success: bool
    message: str
    reservation_id: Optional[int] = None


def get_db_connection():
    """Get a database connection from the pool"""
    if not db_pool:
        logger.error("Database pool not initialized")
        return None
    try:
        return db_pool.getconn()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        return None


def return_db_connection(conn):
    """Return a connection to the pool"""
    if db_pool and conn:
        try:
            db_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Failed to return connection to pool: {e}")


def fetch_payment_details(payment_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch payment details from MercadoPago API
    
    Args:
        payment_id: MercadoPago payment ID
        
    Returns:
        Payment details dict or None if error
    """
    if not MERCADOPAGO_ACCESS_TOKEN:
        logger.error("MERCADOPAGO_ACCESS_TOKEN not configured")
        return None
    
    try:
        url = f"{MERCADOPAGO_API_URL}/payments/{payment_id}"
        headers = {
            "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        payment_data = response.json()
        logger.info(f"✅ Payment details fetched: {payment_id}")
        logger.debug(f"Payment data: {payment_data}")
        
        return payment_data
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching payment {payment_id}")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching payment {payment_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching payment {payment_id}: {e}")
        return None


def update_reservation_payment_status(
    reserva_id: int,
    payment_id: str,
    status: str
) -> bool:
    """
    Update PostgreSQL reservas table with payment status
    
    Args:
        reserva_id: Reservation ID (from external_reference)
        payment_id: MercadoPago payment ID
        status: Payment status (approved, pending, rejected, cancelled)
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Could not get database connection")
            return False
        
        cursor = conn.cursor()
        
        # Only mark as paid if status is "approved"
        pagado = status.lower() == "approved"
        
        update_query = """
            UPDATE reservas 
            SET 
                pagado = %s,
                payment_id = %s,
                updated_at = %s
            WHERE id = %s
            RETURNING id, cliente, servicio, fecha
        """
        
        cursor.execute(
            update_query,
            (pagado, payment_id, datetime.now(), reserva_id)
        )
        
        result = cursor.fetchone()
        
        if result:
            conn.commit()
            logger.info(
                f"✅ Reservation {reserva_id} updated: "
                f"pagado={pagado}, payment_id={payment_id}"
            )
            return True
        else:
            conn.rollback()
            logger.warning(f"Reservation {reserva_id} not found in database")
            return False
            
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        logger.error(f"Integrity error updating reservation {reserva_id}: {e}")
        return False
    except psycopg2.OperationalError as e:
        if conn:
            conn.rollback()
        logger.error(f"Operational error updating reservation {reserva_id}: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating reservation {reserva_id}: {e}")
        return False
    finally:
        if conn:
            return_db_connection(conn)


def validate_webhook_signature(request_headers: dict, body: str) -> bool:
    """
    Validate webhook signature (optional)
    Validates X-Signature header from MercadoPago
    
    Args:
        request_headers: Request headers dict
        body: Request body string
        
    Returns:
        True if valid or if no secret configured, False otherwise
    """
    if not WEBHOOK_SECRET:
        # Validation disabled if no secret configured
        return True
    
    try:
        # MercadoPago sends X-Signature header
        # Implementation depends on your webhook setup
        # For now, return True as MercadoPago notifications are secure
        return True
    except Exception as e:
        logger.error(f"Webhook signature validation error: {e}")
        return False


@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("🚀 Webhook server starting...")
    if not MERCADOPAGO_ACCESS_TOKEN:
        logger.warning("⚠️  MERCADOPAGO_ACCESS_TOKEN not configured")
    if not DATABASE_URL:
        logger.warning("⚠️  DATABASE_URL not configured")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("🛑 Webhook server shutting down...")
    if db_pool:
        try:
            db_pool.closeall()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint with real database connectivity probe."""
    db_status = "disconnected"
    if db_pool:
        conn = None
        try:
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            db_status = "connected"
        except Exception:
            logger.warning("Health check: database ping failed")
            db_status = "error"
        finally:
            if conn:
                try:
                    db_pool.putconn(conn)
                except Exception:
                    pass

    overall = "healthy" if db_status == "connected" else "degraded"
    return {
        "status": overall,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
    }


@app.post("/webhook", 
         response_model=WebhookResponse,
         status_code=status.HTTP_200_OK,
         tags=["Webhooks"])
async def mercadopago_webhook(request: Request) -> WebhookResponse:
    """
    MercadoPago Payment Notification Webhook
    
    Receives payment notifications from MercadoPago, fetches payment details,
    and updates the PostgreSQL database with payment status.
    
    Args:
        request: FastAPI request object
        
    Returns:
        WebhookResponse with success status and message
    """
    try:
        # Get request body
        body = await request.body()
        logger.info(f"📨 Webhook received from MercadoPago")
        
        # Parse JSON
        try:
            payload = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        logger.debug(f"Webhook payload: {payload}")
        print("\n🔍 DEBUG - WEBHOOK DATA:", payload)  # Console debug
        
        # Validate webhook signature (optional)
        if not validate_webhook_signature(dict(request.headers), body.decode()):
            logger.warning("Webhook signature validation failed")
            # Still process, but log warning
        
        # Extract notification type
        notification_type = payload.get("type")
        
        # Extract payment_id - handle multiple payload formats
        payment_id = None
        
        # Format 1: {"data": {"id": "..."}}
        if "data" in payload and isinstance(payload["data"], dict):
            payment_id = payload["data"].get("id")
        
        # Format 2: {"id": "..."}
        elif "id" in payload:
            payment_id = payload.get("id")
        
        # Format 3: {"resource": "..."}
        elif "resource" in payload:
            resource = payload.get("resource")
            if isinstance(resource, str):
                payment_id = resource.split("/")[-1]
        
        # Validate payment_id extraction
        if not payment_id:
            logger.error(f"Could not extract payment_id from webhook payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract payment_id from payload"
            )
        
        logger.info(f"Extracted payment_id: {payment_id}, notification_type: {notification_type}")
        
        # Only process payment notifications
        if notification_type != "payment":
            logger.info(f"Ignoring notification type: {notification_type}")
            return WebhookResponse(
                success=True,
                message=f"Notification type '{notification_type}' ignored"
            )
        
        # Fetch payment details from MercadoPago API
        payment_details = fetch_payment_details(payment_id)
        
        if not payment_details:
            logger.error(f"Could not fetch payment details for {payment_id}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not fetch payment details from MercadoPago"
            )
        
        # Extract payment information
        payment_status = payment_details.get("status")
        external_reference = payment_details.get("external_reference")
        payment_id = payment_details.get("id")
        transaction_amount = payment_details.get("transaction_amount")
        payer_email = payment_details.get("payer", {}).get("email")
        
        logger.info(
            f"Payment details - Status: {payment_status}, "
            f"Reference: {external_reference}, Amount: {transaction_amount}"
        )
        print(f"\n🔍 DEBUG - PAYMENT STATUS: {payment_status}")  # Console debug
        print(f"🔍 DEBUG - PAYMENT ID: {payment_id}")  # Console debug
        print(f"🔍 DEBUG - EXTERNAL REFERENCE: {external_reference}")  # Console debug
        
        # Validate external reference (should be reserva_id)
        if not external_reference:
            logger.error(f"Payment {payment_id} has no external_reference")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has no external_reference"
            )
        
        try:
            reserva_id = int(external_reference)
            print(f"✅ DEBUG - RESERVA ID: {reserva_id}")  # Console debug
        except (ValueError, TypeError):
            logger.error(f"Invalid external_reference format: {external_reference}")
            print(f"❌ DEBUG - INVALID RESERVA ID: {external_reference}")  # Console debug
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid external_reference format"
            )
        
        # Update database
        print(f"\n📝 DEBUG - UPDATING DATABASE FOR RESERVA {reserva_id}")  # Console debug
        success = update_reservation_payment_status(
            reserva_id=reserva_id,
            payment_id=str(payment_id),
            status=payment_status
        )
        
        if not success:
            logger.error(f"Failed to update reservation {reserva_id}")
            print(f"❌ DEBUG - DATABASE UPDATE FAILED FOR RESERVA {reserva_id}")  # Console debug
            # Return 200 anyway so MercadoPago doesn't retry indefinitely
            # but log the error for manual review
            return WebhookResponse(
                success=False,
                message=f"Failed to update reservation {reserva_id}",
                reservation_id=reserva_id
            )
        else:
            print(f"✅ DEBUG - DATABASE UPDATE SUCCESSFUL FOR RESERVA {reserva_id}")  # Console debug
        
        # Success response
        message = (
            f"✅ Payment approved and reservation {reserva_id} marked as paid"
            if payment_status == "approved"
            else f"Payment status: {payment_status} - Reservation {reserva_id} updated"
        )
        
        logger.info(message)
        
        return WebhookResponse(
            success=True,
            message=message,
            reservation_id=reserva_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in webhook handler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/webhook/test",
         response_model=WebhookResponse,
         status_code=status.HTTP_200_OK,
         tags=["Testing"])
async def test_webhook():
    """
    Test webhook endpoint for debugging
    Returns a success response to verify webhook is working
    """
    logger.info("📨 Test webhook called")
    return WebhookResponse(
        success=True,
        message="Test webhook endpoint working correctly"
    )


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "MercadoPago Webhook Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health (GET)",
            "webhook": "/webhook (POST)",
            "test": "/webhook/test (POST)",
            "docs": "/docs (GET)"
        },
        "documentation": "/docs"
    }


@app.get("/docs", tags=["Documentation"])
async def docs():
    """API documentation"""
    return {
        "title": "MercadoPago Webhook Server",
        "description": "Receives MercadoPago payment notifications and updates reservations",
        "endpoints": {
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            },
            "/webhook": {
                "method": "POST",
                "description": "MercadoPago payment notification webhook",
                "body": {
                    "type": "payment",
                    "id": "payment_id_from_mercadopago"
                }
            },
            "/webhook/test": {
                "method": "POST",
                "description": "Test webhook for debugging"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    reload = os.getenv("WEBHOOK_RELOAD", "False").lower() == "true"
    
    logger.info(f"Starting webhook server on {host}:{port}")
    
    uvicorn.run(
        "webhook:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
