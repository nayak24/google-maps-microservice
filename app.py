from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

curr_page = 1
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500"]}})
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# db config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(256), nullable=False)
    destination = db.Column(db.String(256), nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    route_data = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint('origin', 'destination', 'mode', name='_origin_destination_mode_uc'),)


with app.app_context():
    db.create_all()


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
def get_accessible_routes(origin, destination, mode="walking"):
    existing_route = Route.query.filter_by(origin=origin, destination=destination, mode=mode).first()
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
                route_data=json.dumps(routes)
            )
            db.session.add(new_route)
            db.session.commit()

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


@app.route('/viewed_routes/page/<int:page>', methods=['GET', 'POST'])
def viewed_routes(page):
    if page < 1:
        return jsonify({"error": "Invalid page number."}), 400
    
    limit = request.args.get('limit', 10, type=int) 
    routes_query = Route.query.paginate(page=page, per_page=limit, error_out=False)

    if not routes_query.items:
        return jsonify({"error": "No routes found."}), 404

    route_data_res = []
    for route in routes_query.items:
        route_data_res.append({
            'id': route.id,
            'origin': route.origin,
            'destination': route.destination,
        })

    pagination_info = {
        'totalItems': routes_query.total,
        'currentPage': page,
        'totalPages': routes_query.pages,
        'limit': limit
    }

    return jsonify({
        'routes': route_data_res,
        'pagination': pagination_info
    }), 200


# API endpoint to get accessible routes
@app.route('/routes', methods=['GET', 'POST'])
def routes():
    if request.method == 'GET':
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        mode = request.args.get('mode')

        if not origin or not destination:
            return jsonify(
                {"error": "Please provide both origin, destination, and direction mode parameters in the URL."}), 400

        routes = get_accessible_routes(origin, destination, mode)

        if routes:
            return jsonify({"routes": routes})
        else:
            return jsonify({"error": "Error retrieving routes."}), 500

    if request.method == 'POST':
        data = request.json
        origin = data.get('origin')
        destination = data.get('destination')
        mode = data.get('mode', 'walking')

        if not origin or not destination:
            return jsonify({"error": "Origin and destination are required."}), 400

        routes = get_accessible_routes(origin, destination, mode)

        if routes:
            return jsonify({"routes": routes}), 201
        else:
            return jsonify({"error": "Error retrieving {mode} routes."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
