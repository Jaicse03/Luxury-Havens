from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    booking_id: int
    payment_method: str  # "stripe" or "razorpay"
    transaction_id: Optional[str] = None  # mock token or real tx id

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    amount: float
    status: str  # "success", "failed", "pending"
    created_at: datetime

    class Config:
        from_attributes = True
