# file: /backend/services/delivery.py
# descr: check if customer delivers to zip code. CustomerDeliveryZone model


from sqlalchemy import select

from app import db
from app.models import CustomerDeliveryZone


def customer_delivers_to_zip(
    customer_id: int,
    zip_code: str,
) -> bool:
    """Return whether a customer delivers to the given ZIP code."""
    statement = select(CustomerDeliveryZone.id).where(
        CustomerDeliveryZone.customer_id == customer_id,
        CustomerDeliveryZone.zip_code == zip_code,
    )

    return db.session.execute(statement).scalar_one_or_none() is not None
