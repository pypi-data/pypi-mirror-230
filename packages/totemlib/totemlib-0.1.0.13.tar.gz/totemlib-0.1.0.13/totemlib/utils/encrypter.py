# # ****************************************************************
# # *********** Manage encryption ***********

# from passlib.context import CryptContext
# from jose import jwt


# # Encrypt the msg with the secretKey and algorithm through the JWT
# def encrypt_msg(log: str, secretKey: str, algorithm: str):
#     msg = {"datetime.date": log}
#     return jwt.encode(msg, secretKey, algorithm=algorithm)


# # Use CryptContext to create a bcrypt_context object
# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# # Generate a hashed password
# def get_password_hash(password):
#     return bcrypt_context.hash(password)


# # Verifies that the password matches the hashed password
# def verify_password(plain_password, hashed_password):
#     return bcrypt_context.verify(plain_password, hashed_password)
