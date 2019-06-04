from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
location = geolocator.geocode(" pedro vidal 2471  ,Montevideo")
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)
