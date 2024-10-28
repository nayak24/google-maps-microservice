# google-maps-microservice

Description: This microservice makes requests to the Google Maps API and returns generated routes between two locations w/ some information about accessbility.

Author: Anish Nayak (an3270)

Team: CloudGPT

## API Usage:
API Root: http://3.133.129.121:5000/

### Calling Endpoint

Given an origin, destination, and mode of transportation (walking, transit, driving) this API endpoint returns all routes for the input parameters. 

Example usage:
```
async function getAccessibleRoutes() {
    const origin = "116th and Broadway, New York, NY";
    const destination = "200 Central Park W, New York, NY";
    const mode = "transit";

    const url = `http://3.133.129.121:5000/routes`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                origin: origin,
                destination: destination,
                mode: mode
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const routesData = await response.json();
        routesData.routes.forEach((route, index) => {
                    console.log(`Route ${index + 1}:`, route);
                });

    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}
```

Optionally, you can run a curl command like the following:
```
curl -X POST http://3.133.129.121:5000/routes \
-H "Content-Type: application/json" \
-d '{
  "origin": "116th and Broadway, New York, NY",
  "destination": "200 Central Park W, New York, NY",
  "mode": "transit"
}'
```

Or use a link that contains the origin, destination, and mode of transport like the following:

http://3.133.129.121:5000/routes?origin=116th+and+Broadway,+New+York,+NY&destination=200+Central+Park+W,+New+York,+NY&mode=transit



### Example Data
The route data is organized into legs (info about the overall route) and steps/substeps for each direction in the route. Some steps may optionally have an 'accessible_places' field that shows if a location on the route has some information about accessbility. If a location has this field it will look like this:

```
"accessible_places": [
                {
                  "details": {
                    "rating": 4.2,
                    "relevant_reviews": [
                      {
                        "author_name": "Koki Takahashi",
                        "author_url": "https://www.google.com/maps/contrib/107573818385641518728/reviews",
                        "language": "en",
                        "original_language": "en",
                        "profile_photo_url": "https://lh3.googleusercontent.com/a-/ALV-UjXpVdalViDV8TA6mk-sg9qJWpVUfEM2-wgiVZU3y51I_uGqSL1ngQ=s128-c0x00000000-cc-rp-mo-ba5",
                        "rating": 3,
                        "relative_time_description": "4 years ago",
                        "text": "The station is clean and nicely located near Sunnyvale Downtown, but it might not be easy to find a parking space.\n\nI luckily found the last one when I drove there late in the morning on a weekday. The elevator was slow, and the two ticket vending machines in front of the lot were occupied. So my family and others needed to rush onto a train. When I returned in the evening, I found the lot remained full.",
                        "time": 1570426851,
                        "translated": false
                      }
                    ],
                    "user_ratings_total": 101
                  },
                  "location": {
                    "lat": 37.3784297,
                    "lng": -122.03078
                  },
                  "name": "Sunnyvale",
                  "place_id": "ChIJkzEodly2j4ARRrQGHWuIeQ4"
                }
              ],
```

Below is an example of the full route data response from the endpoint:

```
{
  "routes": [
    {
      "bounds": {
        "northeast": {
          "lat": 40.8079847,
          "lng": -73.9610705
        },
        "southwest": {
          "lat": 40.7817756,
          "lng": -73.9750048
        }
      },
      "copyrights": "Map data ©2024 Google",
      "legs": [
        {
          "arrival_time": {
            "text": "3:51 PM",
            "time_zone": "America/New_York",
            "value": 1727639510
          },
          "departure_time": {
            "text": "3:24 PM",
            "time_zone": "America/New_York",
            "value": 1727637884
          },
          "distance": {
            "text": "2.3 mi",
            "value": 3736
          },
          "duration": {
            "text": "27 mins",
            "value": 1626
          },
          "end_address": "200 Central Park W, New York, NY 10024, USA",
          "end_location": {
            "lat": 40.7817756,
            "lng": -73.9730704
          },
          "start_address": "Broadway & W 116th St, New York, NY 10027, USA",
          "start_location": {
            "lat": 40.8079847,
            "lng": -73.9638007
          },
          "steps": [
            {
              "distance": {
                "text": "0.2 mi",
                "value": 299
              },
              "duration": {
                "text": "4 mins",
                "value": 244
              },
              "end_location": {
                "lat": 40.8065699,
                "lng": -73.9613019
              },
              "html_instructions": "Walk to Amsterdam Avenue & West 116 Street",
              "polyline": {
                "points": "{haxFv`mbMDMbAaDf@_Bf@}Ar@{BRq@v@f@"
              },
              "start_location": {
                "lat": 40.8079847,
                "lng": -73.9638007
              },
              "steps": [
                {
                  "distance": {
                    "text": "0.2 mi",
                    "value": 264
                  },
                  "duration": {
                    "text": "4 mins",
                    "value": 219
                  },
                  "end_location": {
                    "lat": 40.8068473,
                    "lng": -73.9610994
                  },
                  "html_instructions": "Head \u003Cb\u003Esoutheast\u003C/b\u003E toward \u003Cb\u003EAmsterdam Ave\u003C/b\u003E",
                  "polyline": {
                    "points": "{haxFv`mbMDMbAaDf@_Bf@}Ar@{BRq@"
                  },
                  "start_location": {
                    "lat": 40.8079847,
                    "lng": -73.9638007
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "115 ft",
                    "value": 35
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 25
                  },
                  "end_location": {
                    "lat": 40.8065699,
                    "lng": -73.9613019
                  },
                  "html_instructions": "Turn \u003Cb\u003Eright\u003C/b\u003E onto \u003Cb\u003EAmsterdam Ave\u003C/b\u003E\u003Cdiv style=\"font-size:0.9em\"\u003EDestination will be on the right\u003C/div\u003E",
                  "maneuver": "turn-right",
                  "polyline": {
                    "points": "yaaxFzolbMv@f@"
                  },
                  "start_location": {
                    "lat": 40.8068473,
                    "lng": -73.9610994
                  },
                  "travel_mode": "WALKING"
                }
              ],
              "travel_mode": "WALKING"
            },
            {
              "distance": {
                "text": "2.0 mi",
                "value": 3160
              },
              "duration": {
                "text": "19 mins",
                "value": 1152
              },
              "end_location": {
                "lat": 40.7828255,
                "lng": -73.9750048
              },
              "html_instructions": "Bus towards West Village Abingdon Sq Via 9 Ave",
              "polyline": {
                "points": "g`axFpqlbMJSlAx@bAn@x@h@n@b@FB@@bAp@JHB@NJ^Vz@h@v@f@HHz@h@XRr@d@XPTHNLNi@Ng@Tu@Ne@DU@CX}@Xy@j@kBX}@Nc@Rc@ZNJHZRDBHDNJLH`@Xt@f@b@Xn@b@JFh@^VPTN~@j@j@\\LJFDHFZRNJ@?~@n@VNb@XBBLHt@d@dAt@p@b@NH\\VNJdAp@DBFB\\VfAr@z@j@z@f@RN`@ZDBbAp@VP|AbAPLLHjAv@ZPVPh@\\BBdAp@`@Xp@b@p@b@LJ|AbANJt@d@hAt@`BfAXPx@j@~@l@bC~AxBxAn@b@lAv@|BzAn@`@tA~@dAr@bAn@bAp@z@h@|@n@|@l@b@Xd@Zt@d@d@Z^Tz@j@h@^t@d@IT"
              },
              "start_location": {
                "lat": 40.8065997,
                "lng": -73.9613743
              },
              "transit_details": {
                "arrival_stop": {
                  "location": {
                    "lat": 40.7828255,
                    "lng": -73.9750048
                  },
                  "name": "Columbus Av/W 80 St"
                },
                "arrival_time": {
                  "text": "3:48 PM",
                  "time_zone": "America/New_York",
                  "value": 1727639280
                },
                "departure_stop": {
                  "location": {
                    "lat": 40.8065997,
                    "lng": -73.9613743
                  },
                  "name": "Amsterdam Avenue & West 116 Street"
                },
                "departure_time": {
                  "text": "3:28 PM",
                  "time_zone": "America/New_York",
                  "value": 1727638128
                },
                "headsign": "West Village Abingdon Sq Via 9 Ave",
                "line": {
                  "agencies": [
                    {
                      "name": "MTA",
                      "url": "https://new.mta.info/"
                    }
                  ],
                  "color": "#1d59b3",
                  "name": "Riverbank Park & Harlem - West Village",
                  "short_name": "M11",
                  "text_color": "#ffffff",
                  "vehicle": {
                    "icon": "//maps.gstatic.com/mapfiles/transit/iw2/6/bus2.png",
                    "name": "Bus",
                    "type": "BUS"
                  }
                },
                "num_stops": 15
              },
              "travel_mode": "TRANSIT"
            },
            {
              "distance": {
                "text": "0.2 mi",
                "value": 277
              },
              "duration": {
                "text": "4 mins",
                "value": 230
              },
              "end_location": {
                "lat": 40.7817756,
                "lng": -73.9730704
              },
              "html_instructions": "Walk to 200 Central Park W, New York, NY 10024, USA",
              "polyline": {
                "points": "mk|wFjfobMDBHDFMHDLHDWBK?C?AA??AACMMAA?A?A@G?I?C?GHAF?D@F@F@?I?O?KAICKEOBKJ_@@CHUDQBS@G?M?M?KJANEHGHIBEHOJ[RN"
              },
              "start_location": {
                "lat": 40.7827888,
                "lng": -73.9749367
              },
              "steps": [
                {
                  "distance": {
                    "text": "85 ft",
                    "value": 26
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 31
                  },
                  "end_location": {
                    "lat": 40.7825528,
                    "lng": -73.9749992
                  },
                  "html_instructions": "Head \u003Cb\u003Esouthwest\u003C/b\u003E on \u003Cb\u003EColumbus Ave\u003C/b\u003E toward \u003Cb\u003EW 80th St\u003C/b\u003E",
                  "polyline": {
                    "points": "mk|wFjfobMDBHDFMHDLH"
                  },
                  "start_location": {
                    "lat": 40.7827888,
                    "lng": -73.9749367
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "167 ft",
                    "value": 51
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 41
                  },
                  "end_location": {
                    "lat": 40.7825859,
                    "lng": -73.9745075
                  },
                  "html_instructions": "Turn \u003Cb\u003Eleft\u003C/b\u003E",
                  "maneuver": "turn-left",
                  "polyline": {
                    "points": "}i|wFvfobMDWBK?C?AA??AACMMAA?A?A@G?I?C?G"
                  },
                  "start_location": {
                    "lat": 40.7825528,
                    "lng": -73.9749992
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "72 ft",
                    "value": 22
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 17
                  },
                  "end_location": {
                    "lat": 40.7823885,
                    "lng": -73.9745342
                  },
                  "html_instructions": "Turn \u003Cb\u003Eright\u003C/b\u003E",
                  "maneuver": "turn-right",
                  "polyline": {
                    "points": "ej|wFtcobMHAF?D@F@F@"
                  },
                  "start_location": {
                    "lat": 40.7825859,
                    "lng": -73.9745075
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "112 ft",
                    "value": 34
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 28
                  },
                  "end_location": {
                    "lat": 40.7824477,
                    "lng": -73.9741465
                  },
                  "html_instructions": "Turn \u003Cb\u003Eleft\u003C/b\u003E",
                  "maneuver": "turn-left",
                  "polyline": {
                    "points": "}h|wFxcobM?I?O?KAICKEO"
                  },
                  "start_location": {
                    "lat": 40.7823885,
                    "lng": -73.9745342
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "243 ft",
                    "value": 74
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 61
                  },
                  "end_location": {
                    "lat": 40.7822527,
                    "lng": -73.9733713
                  },
                  "html_instructions": "Turn \u003Cb\u003Eright\u003C/b\u003E",
                  "maneuver": "turn-right",
                  "polyline": {
                    "points": "ii|wFlaobMBKJ_@@CHUDQBS@G?M?M?K"
                  },
                  "start_location": {
                    "lat": 40.7824477,
                    "lng": -73.9741465
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "171 ft",
                    "value": 52
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 38
                  },
                  "end_location": {
                    "lat": 40.7818831,
                    "lng": -73.9729899
                  },
                  "html_instructions": "Turn \u003Cb\u003Eright\u003C/b\u003E",
                  "maneuver": "turn-right",
                  "polyline": {
                    "points": "ah|wFp|nbMJANEHGHIBEHOJ["
                  },
                  "start_location": {
                    "lat": 40.7822527,
                    "lng": -73.9733713
                  },
                  "travel_mode": "WALKING"
                },
                {
                  "distance": {
                    "text": "59 ft",
                    "value": 18
                  },
                  "duration": {
                    "text": "1 min",
                    "value": 14
                  },
                  "end_location": {
                    "lat": 40.7817756,
                    "lng": -73.9730704
                  },
                  "html_instructions": "Turn \u003Cb\u003Eright\u003C/b\u003E\u003Cdiv style=\"font-size:0.9em\"\u003EDestination will be on the right\u003C/div\u003E",
                  "maneuver": "turn-right",
                  "polyline": {
                    "points": "we|wFdznbMRN"
                  },
                  "start_location": {
                    "lat": 40.7818831,
                    "lng": -73.9729899
                  },
                  "travel_mode": "WALKING"
                }
              ],
              "travel_mode": "WALKING"
            }
          ],
          "traffic_speed_entry": [],
          "via_waypoint": []
        }
      ],
      "overview_polyline": {
        "points": "{haxFv`mbMxCmJfAmDv@f@ELJSlAx@|BxA|BzAxFtDlAx@n@ZNLNi@Ng@l@uBxBaHb@gAf@Xz@h@fGbE|DfC~MzIdBjAvBrA~B`BtClBhDxBjIrFrRhMl]dUdBjAt@d@ITFKDBHDFMVNHc@AGQS@K?M?GHAL@NBAo@I[Nk@T_A@o@ZGRQLUJ[RN"
      },
      "summary": "",
      "warnings": [
        "Walking directions are in beta. Use caution – This route may be missing sidewalks or pedestrian paths."
      ],
      "waypoint_order": []
    }
  ]
}
```

