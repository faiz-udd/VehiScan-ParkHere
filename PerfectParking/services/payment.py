import requests
from django.conf import settings
from ..models import Payment, Booking
import logging
import hashlib
import json
import time

logger = logging.getLogger(__name__)

class EasypaisaPaymentService:
    def __init__(self):
        self.merchant_id = settings.EASYPAISA_MERCHANT_ID
        self.merchant_key = settings.EASYPAISA_MERCHANT_KEY
        self.base_url = settings.EASYPAISA_API_URL

    def create_payment(self, booking: Booking) -> dict:
        """Create a new payment request"""
        try:
            # Generate order details
            order_id = f"PKG-{booking.id}-{int(time.time())}"
            amount = float(booking.total_cost)
            
            # Prepare request data
            data = {
                "merchantId": self.merchant_id,
                "orderId": order_id,
                "storeId": "1",
                "transactionAmount": str(amount),
                "mobileAccountNo": booking.user.phone_number,
                "emailAddress": booking.user.email,
                "transactionType": "MA",  # Mobile Account
            }
            
            # Add security hash
            data["hash"] = self._generate_hash(data)
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/initiate-payment",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("responseCode") == "0000":
                    # Create payment record
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=amount,
                        payment_id=result.get("paymentToken"),
                        status="PENDING"
                    )
                    return {
                        "success": True,
                        "payment_token": result.get("paymentToken"),
                        "payment_id": payment.id
                    }
            
            logger.error(f"Easypaisa payment failed: {response.text}")
            return {"success": False, "error": "Payment initiation failed"}
            
        except Exception as e:
            logger.error(f"Error creating Easypaisa payment: {str(e)}")
            return {"success": False, "error": str(e)}

    def verify_payment(self, payment_id: str) -> bool:
        """Verify payment status"""
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            
            data = {
                "merchantId": self.merchant_id,
                "paymentToken": payment_id
            }
            data["hash"] = self._generate_hash(data)
            
            response = requests.post(
                f"{self.base_url}/verify-payment",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("responseCode") == "0000":
                    payment.status = "COMPLETED"
                    payment.save()
                    return True
                    
            payment.status = "FAILED"
            payment.save()
            return False
            
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return False

    def _generate_hash(self, data: dict) -> str:
        """Generate security hash for Easypaisa API"""
        sorted_data = dict(sorted(data.items()))
        data_string = json.dumps(sorted_data, separators=(',', ':'))
        return hashlib.sha256(
            f"{data_string}{self.merchant_key}".encode()
        ).hexdigest() 