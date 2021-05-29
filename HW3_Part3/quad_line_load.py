def quad_line_load(xy, properties_load):
    e = properties_load["t"]
    tx = properties_load["tx"]
    ty = properties_load["ty"]
    ke = 0

    x0 = xy[0,0]
    x1 = xy[1,0]

    y0 = xy[0,1]
    y1 = xy[1,1]
    L = sqrt((x1 - x0)**2 + (y1 - y0)**2)
    t = array([tx, ty, tx, ty])
    fe = e*L/2*t

    return ke, fe
