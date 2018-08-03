from city import City
from pedestrian import Pedestrian

city = City.generate_random_city(10, 10)
#city.print(True, True)
pedestrians = Pedestrian.generate_random_pedestrians(50, city)


