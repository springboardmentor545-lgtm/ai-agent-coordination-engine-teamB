import sys
sys.path.append(".")

from auth.security import verify_password, create_access_token, decode_access_token
import bcrypt

# 1. Hash a password and verify it correctly
test_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode("utf-8")
print("Correct password check:", verify_password("password123", test_hash))
print("Wrong password check:", verify_password("wrongpassword", test_hash))

# 2. Create a token and decode it back
token = create_access_token("EMP1001")
print("Token created:", token[:30], "...")

decoded_employee_id = decode_access_token(token)
print("Decoded employee_id:", decoded_employee_id)

# 3. Confirm a tampered/garbage token is rejected
try:
    decode_access_token(token + "tampered")
    print("PROBLEM: tampered token was accepted!")
except Exception as e:
    print("Tampered token correctly rejected:", type(e).__name__)