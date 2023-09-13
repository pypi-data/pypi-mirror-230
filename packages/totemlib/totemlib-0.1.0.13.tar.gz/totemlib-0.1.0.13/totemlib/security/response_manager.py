# # Manejador de estandar para response
# # Creado por: Totem Bear
# # Fecha: 23-Ago-2023

# from fastapi import Response
# from fastapi.responses import JSONResponse
# import requests
# from requests.exceptions import RequestException
# from typing import Optional, Tuple
# from totemlib import utils as tbu
# from . import gendata as gd

# # Diccionario de métodos disponibles para invocar APIs
# METHODS = {
#     'get': requests.get,
#     'post': requests.post,
#     'put': requests.put,
#     'delete': requests.delete
# }


# def get_response(url: str, metodo: str, req_form: dict = None):
#     """
#     Función para consumir un API y obtener el response.

#     Args:
#         url (str): URL del API a consumir.
#         metodo (str): Método de request a utilizar.
#         req_form (dict): Diccionario con datos a enviar al API.
#      Returns:
#         response: Respuesta del API.
#     Raises:
#         RequestException: En caso de que no se pueda realizar la solicitud HTTP.
#     """
#     try:
#         endpoint = gd.url_api + url
#         print(f"\n*****endpoint: {endpoint}")
#         print(f"*****method: {metodo}")
#         print(f"*****req_form: {req_form}")
        
#         if metodo not in METHODS:
#             raise ValueError(f"Invalid method: {metodo}")

#         response = METHODS[metodo](url=endpoint, json=req_form) if req_form \
#             else METHODS[metodo](url=endpoint)

#         print("\n*****response status-reason get_response:", 
#               response.status_code, " - ", response.reason)
#         print("\n*****response:", response, "\n")
#     except RequestException as e:
#         tbu.logger.printLog(gd.log_file, f"AppVentas Response Manager - "\
#                             f"Error al hacer request al url {url}. "\
#                             f"Error: {str(e)}", "error")
#         return JSONResponse(status_code=500, 
#                             content={"AppVentas Response Manager - detail": 
#                                      "Error al hacer request"})

#     return response


# def error_response(resp: dict, msj_error: str, 
#                    detalles: Optional[Tuple] = None) -> dict:
#     """
#     Genera una respuesta de error en formato de diccionario.

#     Args:
#         resp: Respuesta a devolver
#         msj_error (str): El mensaje de error principal a incluir en la 
#             respuesta.
#         detalles (Optional[Tuple], optional): Detalles adicionales para 
#             incluir. Por defecto en None.
#     Returns:
#         dict: Diccionario que contiene la respuesta de error:
#             resp: Diccionario de response.
#             msg: Mensaje de resultado.
#             error: True para indicar que ocurrió un error.
#             detalles (Opcional): Diccionario con datos adicionales.
#     """
    
#     response = {"resp": resp, "msj": msj_error, "error": True}
    
#     if detalles is not None:
#         response["detalles"] = detalles
    
#     return response
#     # TODO Revisar codigo de error del response
#     #return JSONResponse(status_code=500, content=response)


# def success_response(resp: dict, msj: str, 
#                      detalles: Optional[dict] = None) -> dict:
#     """
#     Genera una respuesta de éxito en formato de diccionario.

#     Args:
#         resp: Respuesta a devolver
#         msj (str): El mensaje principal a incluir en la respuesta.
#         detalles (Optional[Tuple], optional): Detalles adicionales para 
#             incluir. Por defecto en None.
#     Returns:
#         dict: Diccionario que contiene la respuesta:
#             resp: Diccionario de response.
#             msg: Mensaje de resultado.
#             error: False para indicar que NO ocurrió un error. Resultado OK.
#             detalles (Opcional): Diccionario con datos adicionales.
#     """
    
#     response = {"resp": resp, "msj": msj, "error": False}
    
#     if detalles is not None:
#         response["detalles"] = detalles
#     print(f"\n***** success_response: {response}")
    
#     return response
#     #return JSONResponse(status_code=200, content=response)


# def service_success(metodo: str, endpoint: str):
#     """
#     Imprime en archivo de log la invocación exitosa de servicio.

#     Args:
#         metodo (str): Método desde donde se invoca el API.
#         endpoint (str): Enpoint del API a invocar.
#     Returns:
#         No return.
#         Imprime en archivo log definido en archivo properties.
#     """

#     msj = f"Services-Inverfin - {metodo}: Servicio {endpoint} responde."
#     tbu.logger.printLog(gd.log_file, msj, "info")


# def service_error(metodo: str, endpoint: str):
#     """
#     Imprime en archivo de log la invocación fallida de servicio.

#     Args:
#         metodo (str): Método desde donde se invoca el API.
#         endpoint (str): Enpoint del API a invocar.
#     Returns:
#         No return.
#         Imprime en archivo log definido en archivo properties.
#     """
#     msj = f"Services-Inverfin - {metodo}: Servicio {endpoint} NO responde."
#     tbu.logger.printLog(gd.log_file, msj, "error")
