from pydantic import BaseModel

class PaymentIntentRequest(BaseModel):
    amount: int
    currency: str

class PaymentIntentResponse(BaseModel):
    client_secret: str