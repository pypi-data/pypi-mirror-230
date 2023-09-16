def density_formula(mass, volume):
    density = mass / volume
    return density


def cylinder_density_formula(area1, area2, height, density):
    cylinder_density = (area1 + area2) * height * density
    return cylinder_density


def specific_gravity_formula(object_density, fluid_den):
    specific_gravity = object_density / fluid_den
    return specific_gravity


def fluid_density(buoyancy_formula, gravity, volume):
    return buoyancy_formula / (gravity * volume)


def unit(name):
    if name == 'density_formula':
        un = "kg/m^3"
        return un
    elif name == 'cylinder_density_formula':
        un = "kg/m^4"
        return un
    elif name == "specific_gravity_formula":
        un = ""
        return un
    elif name == "fluid_density":
        un = "kg/m^3"
        return un
    else:
        raise TypeError
