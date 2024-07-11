
from database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True, index=True)
    email = Column(String(250), unique=True, index=True)
    password = Column(Text)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return f'<User(username={self.username}, email={self.email})>'

class Order(Base):
    ORDER_STATUSES = (
        ('PENDING', "pending"),
        ('IN_TRANSIT', "in_transit"),
        ('DELIVERED', "delivered")
    )
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default="PENDING")
    user_id = Column(Integer, ForeignKey('users.id'))  # corrected table name
    user = relationship('User', back_populates='orders')
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='orders')

    def __repr__(self):
        return f"<Order {self.id}>"

class Product(Base):
    __tablename__ = 'products'  # corrected table name
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    orders = relationship('Order', back_populates='product')

    def __repr__(self):
        return f"<Product {self.name}>"
