from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_routes
from product_routes import product_router


app = FastAPI()


app.include_router(auth_router)
app.include_router(order_routes)
app.include_router(product_router)


@app.get("/")
async def get_home():
    return {"massage" "Hello FastApi"}




