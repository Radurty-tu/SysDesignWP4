'''
has all the material properties.
yeah
'''

materials = [
    {
        "name": "7475-T 761",
        "elasticity": 70e9,
        "density": 2810,
        "max_STRESS": 448e6,
        "max_SHEAR": 310e6,
        "expansion": 23.2e-6,
    },
    {
        "name": "2014-T6",
        "elasticity": 73.1e9,
        "density": 2800,
        "max_STRESS": 414e6,
        "max_SHEAR": 290e6,
        "expansion": 23e-6,
    },
    {
        "name": "7075-T6",
        "elasticity": 71.7e9,
        "density": 2810,
        "max_STRESS": 503e6,
        "max_SHEAR": 331e6,
        "expansion": 23.6e-6,
    },
    {
        "name": "AZ91C-T6",
        "elasticity": 44.8e9,
        "density": 1810,
        "max_STRESS": 145e6,
        "max_SHEAR": 150e6,
        "expansion": 26e-6,
    },
    {
        "name": "356-T6",
        "elasticity": 62.4e9,
        "density": 2670,
        "max_STRESS": 165e6,
        "max_SHEAR": 143e6,
        "expansion": 21.4e-6,
    },
    {
        "name": "4130 Steel",
        "elasticity": 205e9,
        "density": 7850,
        "max_STRESS": 435e6,
        "max_SHEAR": 430e6,
        "expansion": 11.1e-6,
    },
    {
        "name": "8630 Steel",
        "elasticity": 200e9,
        "density": 7850,
        "max_STRESS": 550e6,
        "max_SHEAR": 410e6,
        "expansion": 11e-6,
    },
    {
        "name": "2024-T3",
        "elasticity": 73.1e9,
        "density": 2780,
        "max_STRESS": 345e6,
        "max_SHEAR": 283e6,
        "expansion": 23.2e-6,
    },
    {
        "name": "2024-T4",
        "elasticity": 73.1e9,
        "density": 2780,
        "max_STRESS": 324e6,
        "max_SHEAR": 283e6,
        "expansion": 23.2e-6,
    },
]

def get_material(index: int, prop: str):
    """
    Example:
        E = get_material(3, "elasticity")
    """
    if not (0 <= index < len(materials)):
        raise IndexError(f"Material index {index} out of range.")

    mat = materials[index]

    if prop not in mat:
        raise KeyError(f"Property '{prop}' not found in material '{mat['name']}'.")

    return mat[prop]