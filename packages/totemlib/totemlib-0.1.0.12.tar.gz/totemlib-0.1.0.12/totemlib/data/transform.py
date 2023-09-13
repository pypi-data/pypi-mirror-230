import json
from typing import Optional

def transform_data(source: dict, transformation_type: str, 
                   json_file: str) -> Optional[dict]:
    """
    Transforma un diccionario de datos de acuerdo a las reglas de 
        transformación definidas en un archivo JSON.

    Args:
        origen (dict): El diccionario de datos original que se quiere 
            transformar.
        tipo (str): El tipo de transformación a aplicar, como se define en el 
            archivo JSON.
        archivo_json (str): Ruta al archivo JSON que contiene las reglas de 
            transformación.

    Returns:
        Optional[dict]: Un nuevo diccionario con los datos transformados, o 
            None si el tipo de transformación no se encuentra.
    
    Raises:
        FileNotFoundError: File json not found.

    Example:
        JSON file ('transformaciones.json'):
        {
            "vendedor": {
                "tel_id": "movil_id",
                "telefono": "movil_numero",
                "latitud": "movil_latitud",
                "longitud": "movil_longitud",
                "salon": "movil_indicador_salon"
            },
            ...
        }

        >>> transform_data({"tel_id": "123", "telefono": "555-1234"}, 
            "vendedor", 'transformaciones.json')
        {'movil_id': '123', 'movil_numero': '555-1234'}
    """
    
    try:
        with open(json_file, 'r') as f:
            transformations = json.load(f)
    except FileNotFoundError:
        return {"error": f"File not found {json_file}"}

    transformation = transformations.get(transformation_type, {})
    
    if not transformation:
        return {"error": f"Type {transformation_type} not found in file "\
                f"{json_file}"}
    
    final = {}
    for k_source, k_final in transformation.items():
        if k_source in source:
            final[k_final] = source[k_source]
    
    return final


def get_json_data(json_data: str, json_file: str) -> Optional[dict]:
    """
    Recupera un conjunto de datos específico de un archivo JSON.

    Args:
        json_data (str): El nombre del conjunto de datos que se quiere recuperar.
        json_file (str): Ruta al archivo JSON que contiene los datos.

    Returns:
        Optional[dict]: Un diccionario con los datos recuperados, o None si el conjunto de datos no se encuentra.

    Raises:
        FileNotFoundError: Si el archivo JSON no se encuentra.
    """
        
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"error": f"File not found {json_file}"}

    final_data = data.get(json_data, {})
    
    if not final_data:
        return {"error": f"Type {json_data} not found in file "\
                f"{json_file}"}
    
    return final_data
