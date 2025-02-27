import random
from enum import Enum


class BookingType(str, Enum):
    SINGLE_FLOOR = "single-floor"
    MULTI_FLOOR = "multi-floor"

class Hotel:
    def __init__(self):
        # Initialize hotel structure
        self.floors = 10
        self.rooms_per_floor = [10] * 9 + [7]  # 10 rooms on floors 1-9, 7 rooms on floor 10
        self.available_rooms = self._initialize_rooms()
        
    def _initialize_rooms(self):
        """Initialize all rooms as available"""
        available = {}
        for floor in range(1, self.floors + 1):
            rooms_count = self.rooms_per_floor[floor - 1]
            for room in range(1, rooms_count + 1):
                room_number = floor * 100 + room
                available[room_number] = True
                
        return available
    
    def _travel_time(self, room1, room2):
        """Calculate travel time between two rooms"""
        floor1, room_num1 = divmod(room1, 100)
        floor2, room_num2 = divmod(room2, 100)
        
        # Vertical travel time (2 minutes per floor)
        vertical_time = abs(floor1 - floor2) * 2
        
        # Horizontal travel time (1 minute per room)
        horizontal_time = abs(room_num1 - room_num2)
        
        return vertical_time + horizontal_time
    
    def _get_available_rooms_on_floor(self, floor):
        """Get list of available rooms on a specific floor"""
        rooms_count = self.rooms_per_floor[floor - 1]
        floor_rooms = []
        for room in range(1, rooms_count + 1):
            room_number = floor * 100 + room
            if self.available_rooms.get(room_number, False):
                floor_rooms.append(room_number)
        return floor_rooms
    
    def _find_best_rooms_single_floor(self, num_rooms):
        """Find the best rooms on a single floor"""
        best_rooms = []
        min_time = float('inf')
        
        for floor in range(1, self.floors + 1):
            available_rooms = self._get_available_rooms_on_floor(floor)
            
            if len(available_rooms) >= num_rooms:
                # Try all possible consecutive sequences
                for i in range(len(available_rooms) - num_rooms + 1):
                    rooms = available_rooms[i:i+num_rooms]
                    time = self._travel_time(rooms[0], rooms[-1])
                    
                    if time < min_time:
                        min_time = time
                        best_rooms = rooms
        
        return best_rooms, min_time
    
    def _find_best_rooms_multi_floor(self, num_rooms):
        """Find the best rooms across multiple floors"""
        all_available = []
        
        # Collect all available rooms
        for floor in range(1, self.floors + 1):
            all_available.extend(self._get_available_rooms_on_floor(floor))
        
        if len(all_available) < num_rooms:
            return [], float('inf')  # Not enough rooms available
        
        # Sort rooms by floor and room number
        all_available.sort()
        
        best_rooms = []
        min_time = float('inf')
        
        # Try all possible starting positions
        for i in range(len(all_available) - num_rooms + 1):
            rooms = all_available[i:i+num_rooms]
            time = self._travel_time(rooms[0], rooms[-1])
            
            if time < min_time:
                min_time = time
                best_rooms = rooms
        
        return best_rooms, min_time
    
    def book_rooms(self, num_rooms):
        """Book the specified number of rooms according to the booking rules"""
        if num_rooms > 5:
            return {"error": "Maximum 5 rooms per booking allowed."}
        
        if num_rooms <= 0:
            return {"error": "Invalid number of rooms requested."}
        
        # First try to find rooms on a single floor
        best_single_floor, time_single = self._find_best_rooms_single_floor(num_rooms)
        
        # If no single floor has enough rooms, try multi-floor booking
        if not best_single_floor:
            best_multi_floor, time_multi = self._find_best_rooms_multi_floor(num_rooms)
            
            if not best_multi_floor:
                return {"error": "Not enough rooms available for booking."}
            
            # Mark rooms as booked
            for room in best_multi_floor:
                self.available_rooms[room] = False
            
            return {
                "booked_rooms": best_multi_floor,
                "travel_time": time_multi,
                "booking_type": BookingType.MULTI_FLOOR
            }
        
        # Mark rooms as booked
        for room in best_single_floor:
            self.available_rooms[room] = False
        
        return {
            "booked_rooms": best_single_floor,
            "travel_time": time_single,
            "booking_type": BookingType.SINGLE_FLOOR
        }
    
    def book_specific_rooms(self, rooms):
        """Book specific rooms selected by the user"""
        # Check if all rooms are available
        for room in rooms:
            if room not in self.available_rooms or not self.available_rooms[room]:
                return {"error": f"Room {room} is not available."}
        
        # Calculate travel time if more than one room
        travel_time = 0
        if len(rooms) > 1:
            sorted_rooms = sorted(rooms)
            travel_time = self._travel_time(sorted_rooms[0], sorted_rooms[-1])
        
        # Mark rooms as booked
        for room in rooms:
            self.available_rooms[room] = False
        
        # Determine booking type (single floor or multi floor)
        floors = set([room // 100 for room in rooms])
        booking_type = BookingType.SINGLE_FLOOR if len(floors) == 1 else BookingType.MULTI_FLOOR
        
        return {
            "booked_rooms": rooms,
            "travel_time": travel_time,
            "booking_type": booking_type
        }
    
    def cancel_booking(self, rooms):
        """Cancel a booking and make rooms available again"""
        for room in rooms:
            if room in self.available_rooms:
                self.available_rooms[room] = True
            else:
                return {"error": f"Room {room} is not a valid room."}
        return {"success": True, "message": f"Successfully canceled booking for rooms: {rooms}"}
    
    def get_available_rooms(self):
        """Get all rooms with their availability status"""
        return self.available_rooms
    
    def generate_random_occupancy(self):
        """Generate random occupancy for the hotel"""
        for room in self.available_rooms:
            self.available_rooms[room] = random.choice([True, False])
        return {"success": True, "message": "Random occupancy generated"}
    
    def reset(self):
        """Reset all rooms to available"""
        self.available_rooms = self._initialize_rooms()
        return {"success": True, "message": "Hotel reset successfully"}