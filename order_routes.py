from fastapi import APIRouter
from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderModel
from database import engine,session
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

order_router = APIRouter(
    prefix='/order'
)

session = session(bind=engine)


@order_router.get('/')
async def welcome_page(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    return {"message": "This is order page."}


@order_router.post("/create", response_model=OrderModel)
async def create_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id,
    )
    new_order.user_id = user.id
    session.add(new_order)
    session.commit()
    session.refresh(new_order)  # Refresh to get the new ID

    response_data = {
        'id': new_order.id,
        'quanty': new_order.quantity,
        'user_id': new_order.user_id,
        'product_id': new_order.product_id
    }
    return jsonable_encoder(response_data)



@order_router.get('/list')
async def get_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_staff:
        orders = session.query(Order).all()
    else:

        orders = session.query(Order).filter(Order.user_id == user.id).all()
    return orders


@order_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_active:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            custom_order = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_statuses.value,
                "total_price": order.quantity * order.product.price
            }
            return jsonable_encoder(custom_order)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is allowed to this request")



@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    """
    Get a request user's orders
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    custom_data = [
        {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_statuses.value,
            "total_price": order.quantity * order.product.price
        }
        for order in user.orders
    ]
    return jsonable_encoder(custom_data)


@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    """
    get user order by id
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id, Order.user == current_user).first()
    if order:
        custom_order = {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_statuses.value,
            "total_price": order.quantity * order.product.price
        }
        return jsonable_encoder(custom_order)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this ID {id}")



@order_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT=Depends()):
    """
    Updating user order by fields: quantity and product_id
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order_to_update = session.query(Order).filter(Order.id == id).first()
    if order_to_update.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not update other user's order")
    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "Your order has been successfully modified",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_statuses": order.order_statuses
        }
    }
    return jsonable_encoder(custom_response)


@order_router.delete('/{id}/delete', status_code=status.HTTP_200_OK)
async def delete_order(id: int, Authorize: AuthJWT=Depends()):
    """Delete on order of user"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()

    order = session.query(Order).filter(Order.id == id).first()
    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not delete other user's order")
    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You cannot delete Transit or Delivered orders")

    session.delete(order)
    session.commit()
    custom_response = {
        "success": True,
        "code": 200,
        "message": "User order is successfully deleted",
        "date": None
    }
    return jsonable_encoder(custom_response)