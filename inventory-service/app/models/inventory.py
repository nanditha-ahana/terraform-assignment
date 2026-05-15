from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)  # reserved by pending orders
    reorder_point = Column(Integer, default=10, nullable=False)
    reorder_quantity = Column(Integer, default=50, nullable=False)
    warehouse_location = Column(String(100), nullable=True)

    product = relationship("Product", back_populates="inventory")
    movements = relationship("StockMovement", back_populates="inventory", cascade="all, delete-orphan")



class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(30), nullable=False)  # "in", "out", "adjustment", "reserve", "release"
    quantity = Column(Integer, nullable=False)
    reference_id = Column(String(100), nullable=True)   # e.g. order_id
    reference_type = Column(String(50), nullable=True)  # e.g. "order", "purchase_order"
    note = Column(Text, nullable=True)
    performed_by = Column(Integer, nullable=True)       # user_id

    inventory = relationship("Inventory", back_populates="movements")