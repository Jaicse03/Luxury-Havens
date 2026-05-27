from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.hotel import Hotel, HotelImage
from app.models.room import Room
from app.models.review import Review
from app.models.booking import Booking
import random
from datetime import date, timedelta, datetime

def seed_db():
    db = SessionLocal()
    
    # 1. Clear existing database for clean seeding
    print("Clearing existing tables...")
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    
    # Check if admin already exists
    admin_user = db.query(User).filter(User.email == "admin@luxuryhavens.com").first()
    if admin_user:
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding database with premium content...")

    # 2. Create Users
    admin_user = User(
        email="admin@luxuryhavens.com",
        full_name="Admin Director",
        phone="+123456789",
        hashed_password=get_password_hash("AdminPass123!"),
        role="admin",
        is_verified=True
    )
    db.add(admin_user)

    guest_user = User(
        email="guest@luxuryhavens.com",
        full_name="Alex Mercer",
        phone="+198765432",
        hashed_password=get_password_hash("GuestPass123!"),
        role="user",
        is_verified=True
    )
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    # 3. Create Hotels
    hotels_data = [
        {
            "name": "The Ritz-Carlton Kapalua",
            "description": "Nestled on the coast of Maui, Hawaii, this breathtaking beachfront resort offers premium rooms, signature dining, and two golf courses surrounded by historical sanctuaries.",
            "address": "1 Ritz Carlton Dr",
            "city": "Maui",
            "country": "United States",
            "rating": 4.8,
            "amenities": ["Wi-Fi", "Pool", "Spa", "Gym", "Oceanfront", "Bar", "Restaurant", "Golf Court"],
            "latitude": 21.002,
            "longitude": -156.654,
            "images": [
                {"url": "https://images.unsplash.com/photo-1540541338287-41700207dee6?auto=format&fit=crop&w=1200&q=80", "is_primary": True},
                {"url": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1200&q=80", "is_primary": False}
            ],
            "rooms": [
                {"room_type": "Standard Room", "description": "Elegant king bed room with garden views, marble bath, and private lanai balcony.", "price_per_night": 450.0, "capacity": 2, "amenities": ["King Bed", "Garden View", "Balcony", "AC", "TV"], "quantity": 10},
                {"room_type": "Deluxe Ocean Suite", "description": "Expansive suite with panoramic ocean vistas, master parlor, dining alcove, and bespoke butler service.", "price_per_night": 850.0, "capacity": 4, "amenities": ["Ocean View", "Living Room", "King Bed", "Jacuzzi", "AC", "Kitchenette"], "quantity": 5}
            ]
        },
        {
            "name": "Aman Tokyo",
            "description": "Hovering above the Otemachi Forest, Aman Tokyo combines traditional Japanese minimalism with premium modern architectural scales. Features a towering 30-meter indoor pool and panoramic skyline views.",
            "address": "1-5-6 Otemachi, Chiyoda-ku",
            "city": "Tokyo",
            "country": "Japan",
            "rating": 4.9,
            "amenities": ["Wi-Fi", "Indoor Pool", "Spa", "Gym", "Sky Bar", "Bespoke Dining", "City View"],
            "latitude": 35.688,
            "longitude": 139.764,
            "images": [
                {"url": "https://images.unsplash.com/photo-1503174971373-b1f69850bded?auto=format&fit=crop&w=1200&q=80", "is_primary": True},
                {"url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=80", "is_primary": False}
            ],
            "rooms": [
                {"room_type": "Deluxe Room", "description": "Minimalist Japanese style room featuring authentic Washi paper slides, Furo soaking tub, and Mount Fuji views.", "price_per_night": 600.0, "capacity": 2, "amenities": ["King Bed", "Soaking Tub", "City View", "AC", "Mini-bar"], "quantity": 8},
                {"room_type": "Aman Suite", "description": "Our finest sky residence. 150 square meters of absolute serenity overlooking the Imperial Palace gardens.", "price_per_night": 1200.0, "capacity": 3, "amenities": ["Imperial View", "Spacious Lounge", "King Bed", "AC", "Bose Sound System"], "quantity": 3}
            ]
        },
        {
            "name": "Villa d'Este Cernobbio",
            "description": "Originally built as a Renaissance palace, Villa d'Este is one of the world's most legendary hotels. Set within 25 acres of formal gardens directly fronting the sparkling waters of Lake Como.",
            "address": "Via Regina 40",
            "city": "Lake Como",
            "country": "Italy",
            "rating": 4.7,
            "amenities": ["Wi-Fi", "Floating Pool", "Spa", "Tennis", "Lakefront", "Michelin Restaurant", "Bar"],
            "latitude": 45.845,
            "longitude": 9.076,
            "images": [
                {"url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80", "is_primary": True},
                {"url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80", "is_primary": False}
            ],
            "rooms": [
                {"room_type": "Classic Room", "description": "Charming vintage Italian furnishings, high ceilings, silk wallpapers, and manicured courtyard views.", "price_per_night": 700.0, "capacity": 2, "amenities": ["Queen Bed", "Antiques", "AC", "Luxury Linens"], "quantity": 12},
                {"room_type": "Lake View Suite", "description": "Opulent suites dressed in silk brocades, period artwork, offering unmatched views of the sailing boats on Lake Como.", "price_per_night": 1600.0, "capacity": 3, "amenities": ["Lakefront View", "Balcony", "King Bed", "Living Area", "Mini-bar"], "quantity": 4}
            ]
        },
        {
            "name": "Burj Al Arab Jumeirah",
            "description": "Standing on a private man-made island, the sail-shaped silhouette of Burj Al Arab is the crown jewel of Arabian hospitality. Offers ultimate luxury with private suites on two floors and full-service butlers.",
            "address": "Jumeirah St",
            "city": "Dubai",
            "country": "United Arab Emirates",
            "rating": 4.9,
            "amenities": ["Wi-Fi", "Private Beach", "Pool", "Helipad", "Gym", "Butler Service", "Gold Interior", "Spa"],
            "latitude": 25.141,
            "longitude": 55.185,
            "images": [
                {"url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1200&q=80", "is_primary": True},
                {"url": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&q=80", "is_primary": False}
            ],
            "rooms": [
                {"room_type": "Deluxe Marina Suite", "description": "Split-level luxury suite overlooking the turquoise Persian Gulf with private staircase, bar, and office.", "price_per_night": 1500.0, "capacity": 3, "amenities": ["Marina View", "Split Level", "Private Butler", "iPad Console", "King Bed"], "quantity": 6},
                {"room_type": "Royal Suite", "description": "The peak of international opulence. Features private cinema, gold-leaf canopy beds, private elevator, and master dining.", "price_per_night": 3200.0, "capacity": 4, "amenities": ["Private Cinema", "Rotatable Bed", "Elevator", "Gold Leaf Details", "Oceanfront View"], "quantity": 1}
            ]
        }
    ]

    # Create Hotels and sub-rooms/images
    for hotel_item in hotels_data:
        db_hotel = Hotel(
            name=hotel_item["name"],
            description=hotel_item["description"],
            address=hotel_item["address"],
            city=hotel_item["city"],
            country=hotel_item["country"],
            rating=hotel_item["rating"],
            amenities=hotel_item["amenities"],
            latitude=hotel_item["latitude"],
            longitude=hotel_item["longitude"]
        )
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)

        # Add images
        for img in hotel_item["images"]:
            db_img = HotelImage(
                hotel_id=db_hotel.id,
                url=img["url"],
                is_primary=img["is_primary"]
            )
            db.add(db_img)

        # Add rooms
        for rm in hotel_item["rooms"]:
            db_room = Room(
                hotel_id=db_hotel.id,
                room_type=rm["room_type"],
                description=rm["description"],
                price_per_night=rm["price_per_night"],
                capacity=rm["capacity"],
                amenities=rm["amenities"],
                is_available=True,
                quantity=rm["quantity"]
            )
            db.add(db_room)

        db.commit()
        
        # Add a couple of reviews for each hotel
        reviews_pool = [
            ("Absolute heaven on earth! Exceeded every single expectation.", 5),
            ("Unmatched service, premium dining, and gorgeous room aesthetics. Highly recommended.", 5),
            ("Excellent location and beautiful views. Extremely attentive hospitality.", 4),
            ("A truly unforgettable stay. The attention to detail is remarkable.", 5)
        ]
        
        for comment, stars in random.sample(reviews_pool, 2):
            db_rev = Review(
                user_id=guest_user.id,
                hotel_id=db_hotel.id,
                rating=stars,
                comment=comment
            )
            db.add(db_rev)
            
        db.commit()

    print("Creating sample bookings to populate user history & analytics...")
    
    # Grab Maui deluxe room and Como classic room
    maui_room = db.query(Room).join(Hotel).filter(Hotel.city == "Maui", Room.room_type == "Standard Room").first()
    como_room = db.query(Room).join(Hotel).filter(Hotel.city == "Lake Como", Room.room_type == "Classic Room").first()

    # Past stay for Guest User (makes them qualified to write reviews)
    past_booking = Booking(
        booking_code="LH-PAST77",
        user_id=guest_user.id,
        room_id=maui_room.id,
        check_in=date.today() - timedelta(days=15),
        check_out=date.today() - timedelta(days=10),
        total_price=5 * maui_room.price_per_night,
        status="confirmed",
        guest_name=guest_user.full_name,
        guest_email=guest_user.email,
        guest_count=2,
        created_at=datetime.utcnow() - timedelta(days=20)
    )
    db.add(past_booking)
    
    # Upcoming stay for Guest User
    upcoming_booking = Booking(
        booking_code="LH-NEXT88",
        user_id=guest_user.id,
        room_id=como_room.id,
        check_in=date.today() + timedelta(days=12),
        check_out=date.today() + timedelta(days=15),
        total_price=3 * como_room.price_per_night,
        status="confirmed",
        guest_name=guest_user.full_name,
        guest_email=guest_user.email,
        guest_count=2,
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(upcoming_booking)
    
    db.commit()
    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
