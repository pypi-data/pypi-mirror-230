# Manejo de arhivos properties
# Creado por: Totem Bear
# Fecha: 23-Ago-2023

from jproperties import Properties

# REVISAR Y OPTIMIZAR ####################

# Create a properties object
config = Properties()


# Loading the properties file
def readProperties(route_file: str, access: str = 'rb'):

    with open(route_file, access) as config_file:
        config.load(config_file)

    return config


# Getting the property value
def getProperty(propKey: str):

    # print(f"property readed: {config.get(propKey).data}")
    return config.get(propKey).data