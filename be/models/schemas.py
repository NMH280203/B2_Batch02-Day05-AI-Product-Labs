from pydantic import BaseModel
from typing import Literal


class Location(BaseModel):
    lat: float
    lng: float
    address: str | None = None


class UserContext(BaseModel):
    location: Location | None = None
    budget: int | None = None           # VND
    people: int | None = None
    meal_time: Literal["breakfast", "lunch", "dinner", "snack"] | None = None
    purpose: Literal["family", "date", "friends", "work", "solo"] | None = None
    preferences: list[str] = []
    allergies: list[str] = []


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    context: UserContext


class FoodSuggestion(BaseModel):
    name: str
    category: str
    description: str
    estimated_price: int
    reason: str
    tags: list[str]


class Restaurant(BaseModel):
    place_id: str
    name: str
    address: str
    distance_km: float
    rating: float
    price_level: int
    is_open: bool
    phone: str | None = None
    maps_url: str
    photo_url: str | None = None
    featured_dishes: list[str]
    score: float


class RestaurantQueryParams(BaseModel):
    lat: float
    lng: float
    query: str
    budget: int | None = None
    radius: int = 2000
    limit: int = 5
