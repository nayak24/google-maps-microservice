from sqlalchemy.orm import Session, sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine, Column, Integer, String, Text, UniqueConstraint, ForeignKey
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy_paginator import Paginator
import requests
import json
import os
from dotenv import load_dotenv
import logging
import time
import uvicorn

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()


origins = ["http://127.0.0.1:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'user'
    id = Column(String(50), primary_key=True)
    routes = relationship('Route', back_populates='user')

class Route(Base):
    __tablename__ = 'route'
    id = Column(Integer, primary_key=True)
    origin = Column(String(256), nullable=False)
    destination = Column(String(256), nullable=False)
    mode = Column(String(50), nullable=False)
    route_data = Column(Text, nullable=False)
    user_id = Column(String(50), ForeignKey('user.id'), nullable=False)

    user = relationship('User', back_populates='routes')

    __table_args__ = (UniqueConstraint('origin', 'destination', 'mode', 'user_id', name='_origin_destination_user_uc'),)

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# call google places API to check for accessible facilities near given location
def find_accessible_places(lat, lng, radius=200):
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lng}&radius={radius}&key={GOOGLE_MAPS_API_KEY}"
    )

    try:
        response = requests.get(places_url)
        places = response.json().get('results', [])

        accessibility_keywords = ['accessible', 'accessibility', 'ramp', 'elevator', 'accessible entrance',
                                  'wheelchair', 'accessible restroom', 'lift']
        relevant_types = ['transit_station', 'shopping_mall', 'hospital', 'airport', 'subway_station', 'train_station',
                          'bus_station', 'public_building']

        accessible_places = []
        for place in places:
            if any(keyword in place.get('name', '').lower() for keyword in accessibility_keywords):
                place_details = get_place_details(place['place_id'])
                accessible_places.append({
                    "name": place.get('name'),
                    "location": place.get('geometry', {}).get('location'),
                    "place_id": place.get('place_id'),
                    "details": place_details
                })
            elif any(t in place.get('types', []) for t in relevant_types):
                place_details = get_place_details(place['place_id'])
                if len(place_details['relevant_reviews']) > 0:
                    accessible_places.append({
                        "name": place.get('name'),
                        "location": place.get('geometry', {}).get('location'),
                        "place_id": place.get('place_id'),
                        "details": place_details
                    })

        return accessible_places

    except requests.RequestException as e:
        print(f"Error fetching places: {e}")
        return None


# get detailed info about a place using google place details API
def get_place_details(place_id):
    place_details_url = (
        f"https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&key={GOOGLE_MAPS_API_KEY}"
    )

    try:
        response = requests.get(place_details_url)
        place_details = response.json().get('result', {})
        accessibility_keywords = ['accessible', 'accessibility', 'ramp', 'elevator', 'accessible entrance',
                                  'wheelchair', 'accessible restroom', 'lift']

        reviews = place_details.get('reviews', [])
        relevant_reviews = [review for review in reviews if
                            any(keyword in review.get('text', '').lower() for keyword in accessibility_keywords)]

        return {
            "rating": place_details.get("rating"),
            "user_ratings_total": place_details.get("user_ratings_total"),
            "relevant_reviews": relevant_reviews
        }

    except requests.RequestException as e:
        print(f"Error fetching place details: {e}")
        return {}


# get routes from google directions API and check for accessibility along the way
def get_accessible_routes(db: Session, origin, destination, mode="walking", user_id=None):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        new_user = User(id=user_id)
        db.add(new_user)
        db.commit()

    existing_route = db.query(Route).filter_by(
        origin=origin,
        destination=destination,
        mode=mode,
        user_id=user_id
    ).first()
    
    if existing_route:
        return json.loads(existing_route.route_data)

    directions_url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={origin}&destination={destination}&mode={mode}&alternatives=true&key={GOOGLE_MAPS_API_KEY}"
    )

    try:
        response = requests.get(directions_url)
        routes = response.json().get('routes', [])

        if routes:
            new_route = Route(
                origin=origin,
                destination=destination,
                mode=mode,
                route_data=json.dumps(routes),
                user_id=user_id
            )
            db.add(new_route)
            db.commit()

            for route in routes:
                for leg in route.get('legs', []):
                    for step in leg.get('steps', []):
                        lat = step['end_location']['lat']
                        lng = step['end_location']['lng']

                        # Find accessible places near each step
                        accessible_places = find_accessible_places(lat, lng)
                        if accessible_places:
                            step['accessible_places'] = accessible_places  # add accessible places to step

        return routes

    except requests.RequestException as e:
        print(f"Error fetching directions: {e}")
        return None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(f"Response status: {response.status_code} | Time: {process_time:.4f}s")
    return response


@app.get("/viewed_routes/page/{page}")
def viewed_routes(page: int, limit: int = 10, db: Session = Depends(get_db)):
    if page < 1:
        return JSONResponse(content={"error": "Invalid page number."}, status_code=400)

    offset = (page - 1) * limit

    routes_query = db.query(Route).offset(offset).limit(limit).all()
    
    total_items = db.query(Route).count()

    total_pages = (total_items + limit - 1) // limit

    if not routes_query:
        return JSONResponse({"error": "No routes found."}, status_code=404)

    route_data_res = [
        {
            'id': route.id,
            'origin': route.origin,
            'destination': route.destination,
        }
        for route in routes_query
    ]

    pagination_info = {
        'totalItems': total_items,
        'currentPage': page,
        'totalPages': total_pages,
        'limit': limit,
        'links': {
            'self': f'/viewed_routes/page/{page}',
            'first': f'/viewed_routes/page/1',
            'last': f'/viewed_routes/page/{total_pages}',
            'next': f'/viewed_routes/page/{page + 1}' if page < total_pages else None,
            'prev': f'/viewed_routes/page/{page - 1}' if page > 1 else None
        }
    }

    return JSONResponse(content={"routes": route_data_res, "pagination": pagination_info})


@app.get("/routes")
async def routes_get(origin: str, destination: str, mode: str = "walking", user_id: str = "1", db: Session = Depends(get_db)):
    if not origin or not destination or not user_id:
        return JSONResponse(content={"error": "Origin, destination, and user_id are required."}, status_code=400)

    routes = get_accessible_routes(db, origin, destination, mode, user_id)
    if routes:
        return JSONResponse(content={"routes": routes, 'links': {"self": f"/routes?origin={origin}&destination={destination}&mode={mode}&user_id={user_id}", "viewed_routes": f"/viewed_routes/page/1?limit=10"}}, status_code=200)
    else:
        return JSONResponse(content={"error": "Error retrieving routes."}, status_code=500)
    
@app.post("/routes")
async def routes_post(data: dict, db: Session = Depends(get_db)):
    origin = data.get('origin')
    destination = data.get('destination')
    mode = data.get('mode', 'walking')
    user_id = data.get('user_id')

    if not origin or not destination or not user_id:
        return JSONResponse(content={"error": "Origin, destination, and user_id are required."}, status_code=400)
    
    routes = get_accessible_routes(db, origin, destination, mode, user_id)
    if routes:
        return JSONResponse(content={"routes": routes, 'links': {"self": f"/routes?origin={origin}&destination={destination}&mode={mode}&user_id={user_id}", "viewed_routes": f"/viewed_routes/page/1?limit=10"}}, status_code=201)
    else:
        return JSONResponse(content={"error": "Error retrieving routes."}, status_code=500)

@app.get("/user/{user_id}/routes")
async def get_user_routes(user_id: int, db: Session = Depends(get_db)):
    routes = db.query(Route).filter_by(user_id=user_id).all()
    
    if not routes:
        return JSONResponse(content={"error": "No routes found for this user."}, status_code=500)

    user_routes = [
        {
            "id": route.id,
            "origin": route.origin,
            "destination": route.destination,
            "mode": route.mode,
            "route_data": json.loads(route.route_data)
        }
        for route in routes
    ]

    return JSONResponse(content={"routes": user_routes}, status_code=201)

@app.delete("/routes/{route_id}")
async def delete_route(route_id: int, user_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter_by(id=route_id, user_id=user_id).first()

    if not route:
        return JSONResponse(
            content={"error": f"Route with ID {route_id} for User ID {user_id} does not exist."},
            status_code=500
        )
    
    try:
        db.delete(route)
        db.commit()
        return JSONResponse(
            content={"message": f"Route with ID {route_id} for User ID {user_id} has been deleted."},
            status_code=200
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            content={"error": f"An error occurred while deleting the route: {str(e)}"},
            status_code=500
        )

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=5000)