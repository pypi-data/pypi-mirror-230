# Validaciones genéricas estándar
# Creado por: Totem Bear
# Fecha: 05-Sep-2023

from collections import deque
from typing import Type

def string_to_type(type_str):
    
    types_map = {
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'dict': dict
    }
    
    try:
        return types_map.get(type_str)
    except Exception as e:
        raise ValueError(f"TotemLib-Security - string_to_type-ERROR: Invalid "\
                         f"data type {type_str}.")
        
    

def validate_fields(data: dict, rules: dict) -> dict:
    """
    Validates the input fields to ensure they exist and are of the correct 
    type and size. This function can handle nested dictionaries for both
    data and rules.

    Args:
        data (dict): Dictionary containing the data to be validated.
        rules (dict): Dictionary containing validation rules.
    
    Returns:
        dict: A dictionary containing information about the validity of each field.
            - "valid": A boolean indicating whether all fields are valid.
            - "errors": A list of error messages.
    """
        
    if data is None or rules is None:
        raise ValueError("Args can't be None.")

    errors = []
    # Queue to manage nested dictionaries
    queue = deque([(data, rules, '')])

    try:
        while queue:
            current_data, current_rules, parent_key = queue.popleft()

            for field, rule in current_rules.items():
                full_key = f"{parent_key}.{field}" if parent_key else field
                value = current_data.get(field)

                # If rule is a dictionary and has a 'type' key
                if isinstance(rule, dict) and 'type' in rule:
                    type_ = rule.get('type')
                    type_class = string_to_type(type_)
                    max_length = rule.get('max_length')

                    if value is None:
                        errors.append(f"{full_key} can't be None.")
                    elif not isinstance(value, type_class):
                        errors.append(f"{full_key} must be of type {type_.__name__}.")
                    elif max_length and isinstance(value, str) and len(value) > max_length:
                        errors.append(f"{full_key} can't have more than {max_length} characters.")
                elif isinstance(rule, dict):
                    # In this case, the type is a dictionary. This means we 
                    # have a nested field.
                    queue.append((value, rule, full_key))         
    except KeyError as e:
        errors.append(f"Rule not defined for field {e}.")
    except Exception as e:
        errors.append(f"Unexpected error occurred: {str(e)}.")
        # Aquí puedes registrar el error real en un archivo de log para futura 
        # depuración, pero no lo expongas al usuario final.

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
