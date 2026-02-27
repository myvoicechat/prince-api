from fastapi import FastAPI
import random
import time

app = FastAPI()

# ====== DATA STORE ======
API_KEYS = {
    "OWNER_KEY": {"limit": 1000, "used": 0}
}

otp_store = {}
logs = []

# ====== KEY CHECK FUNCTION ======
def check_key(key):
    if key not in API_KEYS:
        return False
    if API_KEYS[key]["used"] >= API_KEYS[key]["limit"]:
        return False
    API_KEYS[key]["used"] += 1
    return True

# ====== HOME ======
@app.get("/")
def home():
    return {"status": "Prince API Live 🚀"}

# ====== CREATE NEW API KEY ======
@app.get("/create-key")
def create_key():
    new_key = "PRINCE" + str(random.randint(10000, 99999))
    API_KEYS[new_key] = {"limit": 100, "used": 0}
    return {"api_key": new_key}

# ====== SEND OTP ======
@app.get("/send-otp")
def send_otp(number: str, key: str):
    if not check_key(key):
        return {"status": False, "message": "Invalid or Limit Exceeded"}

    otp = random.randint(100000, 999999)
    otp_store[number] = {
        "otp": otp,
        "expire": time.time() + 120
    }

    logs.append({
        "action": "send",
        "number": number,
        "time": time.ctime()
    })

    return {"status": True, "otp": otp}

# ====== VERIFY OTP ======
@app.get("/verify-otp")
def verify_otp(number: str, otp: int, key: str):
    if not check_key(key):
        return {"status": False, "message": "Invalid or Limit Exceeded"}

    if number not in otp_store:
        return {"status": False, "message": "No OTP Found"}

    data = otp_store[number]

    if time.time() > data["expire"]:
        return {"status": False, "message": "OTP Expired"}

    if data["otp"] != otp:
        return {"status": False, "message": "Wrong OTP"}

    logs.append({
        "action": "verify",
        "number": number,
        "time": time.ctime()
    })

    return {"status": True, "message": "Verified Successfully"}

# ====== VIEW LOGS (OWNER ONLY) ======
@app.get("/logs")
def view_logs(key: str):
    if key != "OWNER_KEY":
        return {"status": "Access Denied"}
    return logs
