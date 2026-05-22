

def geo_dist(lat1, lon1, lat2, lon2):
    grad_rad = 0.0174539
    rad_rad = 57.29577951
    longitud = long1 - long2
    val = (sen(lat1*grad_rad) * sin(lat2*grad_rad))\
          + (cos(lat1*grad_rad)* cos(lat2*grad_rad) * (longitud * grad_rad))
    return (acos(val) * rad_rad) * 11.32