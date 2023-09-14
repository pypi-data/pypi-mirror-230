"""This is a module docstring.
This module is used to define the material properties of the lattice.

Classes:
    Material: This is a class docstring.
        This class is used to define the material properties of the lattice.
"""

class Material:
    """This is a class docstring.
    This class is used to define the material properties of the lattice.
    
    Attributes:
        name: name of the material
        type: type of material
        prop: dictionary of properties
    
    Methods:
        __init__: inits Material with name, type and properties
    """
    def __init__(
        self,
        name:str = "Steel",
        type: str = "Cauchy",
        prop: dict = {
            "E": 200e3,
            "nu": 0.3,
            "G": 0.0,
            "rho": 7.7e-9,
        },
    ) -> None:
        """Inits Material with name, type and properties."""
        self. name = name
        self.type = type
        self.prop = prop
        for k, v in prop.items():
            setattr(self, k, v)