from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Union
import uvicorn
from enum import Enum
from bookRoom import Hotel

app = FastAPI(title="Hotel Booking System API")

# Add CORS middleware to allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookingType(str, Enum):
    SINGLE_FLOOR = "single-floor"
    MULTI_FLOOR = "multi-floor"

class BookingRequest(BaseModel):
    num_rooms: int = Field(..., ge=1, le=5, description="Number of rooms to book (1-5)")

class BookingResponse(BaseModel):
    booked_rooms: List[int] = Field(..., description="List of room numbers that were booked")
    travel_time: int = Field(..., description="Total travel time between first and last room")
    booking_type: BookingType = Field(..., description="Type of booking (single or multi floor)")

class CancelRequest(BaseModel):
    rooms: List[int] = Field(..., description="Room numbers to cancel booking for")

class RoomsResponse(BaseModel):
    available: Dict[int, bool] = Field(..., description="Map of room numbers to availability status")

class RoomSelectionRequest(BaseModel):
    rooms: List[int] = Field(..., description="List of selected room numbers to book")

    @field_validator('rooms')
    def validate_room_count(cls, v):
        if len(v) < 1 or len(v) > 5:
            raise ValueError('Must select between 1 and 5 rooms')
        return v

class StatusResponse(BaseModel):
    success: bool
    message: str

# Create a hotel instance
hotel = Hotel()

# API endpoints
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Hotel Booking System API"}

@app.get("/rooms", response_model=RoomsResponse, tags=["Rooms"])
async def get_rooms():
    """Get all rooms with their availability status"""
    return {"available": hotel.get_available_rooms()}

@app.post("/book", response_model=Union[BookingResponse, StatusResponse], tags=["Booking"])
async def book_rooms(request: BookingRequest):
    """Book rooms automatically based on availability and booking rules"""
    result = hotel.book_rooms(request.num_rooms)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/book-selected", response_model=Union[BookingResponse, StatusResponse], tags=["Booking"])
async def book_selected_rooms(request: RoomSelectionRequest):
    """Book specific rooms selected by the user"""
    result = hotel.book_specific_rooms(request.rooms)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/cancel", response_model=StatusResponse, tags=["Booking"])
async def cancel_booking(request: CancelRequest):
    """Cancel booking for specific rooms"""
    result = hotel.cancel_booking(request.rooms)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"success": True, "message": f"Successfully canceled booking for rooms: {request.rooms}"}

@app.post("/random", response_model=StatusResponse, tags=["Hotel Management"])
async def generate_random_occupancy():
    """Generate random occupancy for the hotel"""
    result = hotel.generate_random_occupancy()
    return result

@app.post("/reset", response_model=StatusResponse, tags=["Hotel Management"])
async def reset_hotel():
    """Reset all rooms to available"""
    result = hotel.reset()
    return result

if __name__ == "__main__":
    uvicorn.run("bookingRouter:app", host="0.0.0.0", port=8000, reload=True)