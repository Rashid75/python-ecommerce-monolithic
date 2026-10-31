"""Collects every module's router into one versioned API router.

main.py mounts this once, so adding a module later is a single line here
rather than another change to the application entry point.
"""

from fastapi import APIRouter

from app.modules.addresses.router import router as addresses_router
from app.modules.cart.router import router as cart_router
from app.modules.categories.router import router as categories_router
from app.modules.products.router import router as products_router
from app.modules.users.auth_router import router as auth_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(cart_router)
api_router.include_router(addresses_router)
