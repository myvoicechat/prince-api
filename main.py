from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import random
import string
import time
import os

app = FastAPI()

# ===== DATABASE (Temporary memory store) =====
users = {}
otp_store = {}
api_keys = {}

# ===== CONFIG =====
ADMIN_KEY = "PRINCE_ADMIN_123"   # change later

# ===== FUNCTIONS =====
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_api_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


# =========================
# ROOT CHECK
# =========================
@app.get("/")
def home():
    return {"status": "API Running Successfully 🚀"}


# =========================
# REGISTER USER
# =========================
@app.post("/register")
async def register(req: Request):
    data = await req.json()
    user = data.get("user")

    if not user:
        raise HTTPException(status_code=400, detail="User required")

    otp = generate_otp()
    otp_store[user] = {"otp": otp, "time": time.time()}

    return {"otp": otp, "msg": "OTP Generated"}


# =========================
# VERIFY OTP
# =========================
@app.post("/verify")
async def verify(req: Request):
    data = await req.json()
    user = data.get("user")
    otp = data.get("otp")

    if user not in otp_store:
        raise HTTPException(status_code=400, detail="OTP expired or not found")

    saved = otp_store[user]

    if time.time() - saved["time"] > 120:
        del otp_store[user]
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp != saved["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    key = generate_api_key()
    api_keys[key] = user
    users[user] = {"api_key": key}

    del otp_store[user]

    return {"status": "verified", "api_key": key}


# =========================
# USER INFO
# =========================
@app.get("/me")
def me(api_key: str):
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid key")

    return {"user": api_keys[api_key]}


# =========================
# ADMIN PANEL
# =========================
@app.get("/admin/users")
def admin_users(admin_key: str):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Not admin")

    return {"total_users": len(users), "users": users}


# =========================
# DELETE USER (ADMIN)
# =========================
@app.delete("/admin/delete")
def delete_user(user: str, admin_key: str):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Not admin")

    if user in users:
        del users[user]
        return {"deleted": user}

    return {"msg": "User not found"}


# =========================
# START SERVER (RAILWAY FIX)
# =========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
