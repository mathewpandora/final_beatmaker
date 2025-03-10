import stripe
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import GenerationPackage
from app.db.schemas.shop_schemas import *
from app.core.security import get_current_user
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.get("/cards")
async def get_cards(db: AsyncSession = Depends(get_db)):
    product_cards_objects = await db.execute(select(GenerationPackage))
    return product_cards_objects.scalars().all()


@router.post("/buy", response_model=PaymentIntentResponse)
async def create_payment_intent(data: PaymentIntentRequest, user_email: str = Depends(get_current_user),) -> PaymentIntentResponse:
    if user_email:
        try:
            intent = stripe.PaymentIntent.create(
                amount=data.amount,
                currency=data.currency,
                payment_method_types=["card"])
            return PaymentIntentResponse(client_secret= intent.client_secret)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="incorrect token")