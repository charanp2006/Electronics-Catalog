from enum import Enum

from pydantic import BaseModel


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
