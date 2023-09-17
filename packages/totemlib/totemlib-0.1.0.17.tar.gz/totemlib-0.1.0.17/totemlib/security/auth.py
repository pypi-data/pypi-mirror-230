# # Authtentication and security functions
# # Created by: Totem Bear
# # Date: 26-Ago-2023

# from typing import Optional
# from datetime import datetime, timedelta
# from jose import jwt, JWTError


# def create_access_token(args: tuple, secretkey: str = None, algorithm: str = None, expires_delta: Optional[timedelta] = None):
#     """
#     This function is used to create an access token for a user and encode it.

#     Args:
#         username (str): The username of the user.
#         user_id (int): The unique id of the user.
#         expires_delta (Optional[timedelta]): Time until token expiration. If not provided, a default value is used.

#     Returns:
#         str: A JWT token.
#     """
#     encode = {"sub": username, "id": user_id}
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=int(utils.tokenExp))

#     iat = datetime.utcnow()
#     encode.update({"iat": iat, "exp": expire})

#     # TODO: Remove this prints into the log file in production
#     # LOOGER

#     return jwt.encode(encode, secretkey, algorithm= algorithm)