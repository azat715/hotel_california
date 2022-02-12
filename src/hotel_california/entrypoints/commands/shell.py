"""чтото типа django shell"""
from hotel_california.config import get_settings
from hotel_california.adapters.orm import start_mappers

settings = get_settings()

start_mappers()
