from fastapi import FastAPI, Request
import requests, random, string, json, os, time
from uuid import uuid4
from datetime import datetime, timedelta

app = FastAPI()

# ========= CONFIG =========
BOT_TOKEN="8524866774:AAGyrQP3-UYO_GiLuG1ePOO2DDq6tBvPsVs"
ADMIN_ID=  "7655840681"

DB_FILE="db.json"

# ========= LOAD DATABASE =========
if os.path.exists(DB_FILE):
    with open(DB_FILE) as f:
        db=json.load(f)
else:
    db={"users":{}, "banned":[], "logs":[]}

def save():
    with open(DB_FILE,"w") as f:
        json.dump(db,f,indent=2)

# ========= SEND =========
def send(cid,text,btn=None):
    data={"chat_id":cid,"text":text,"parse_mode":"HTML"}
    if btn:
        data["reply_markup"]=btn
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",json=data)

# ========= REGISTER =========
def register(uid):
    db["users"][str(uid)]={
        "key":str(uuid4()),
        "demo":5,
        "premium":False,
        "expiry":None,
        "last":0
    }
    save()

# ========= MENU =========
def menu():
    return {"keyboard":[
        ["📱 Lookup","🌐 IP"],
        ["👤 Profile","🔐 Pass"],
        ["📊 Status","📍 Address"],
        ["💎 Premium","🔎 User"],
        ["📱 Device"]
    ],"resize_keyboard":True}

# ========= WEBHOOK =========
@app.post("/webhook")
async def webhook(req:Request):

    data=await req.json()
    if "message" not in data:
        return {"ok":True}

    msg=data["message"]
    uid=str(msg["chat"]["id"])
    text=msg.get("text","")

# ===== BAN CHECK =====
    if uid in db["banned"]:
        return {"ok":True}

# ===== REGISTER =====
    if uid not in db["users"]:
        register(uid)

    u=db["users"][uid]

# ===== ANTI SPAM =====
    if time.time()-u["last"]<1:
        return {"ok":True}
    u["last"]=time.time()

# ===== START =====
    if text=="/start":
        send(uid,"🔥 <b>Ultimate Multi Tool Bot</b>",menu())

# ===== PROFILE =====
    elif text=="👤 Profile":
        send(uid,f"""
<b>PROFILE</b>

ID : <code>{uid}</code>
Premium : {u['premium']}
Demo : {u['demo']}
Expiry : {u['expiry']}
""")

# ===== STATUS =====
    elif text=="📊 Status":
        send(uid,f"""
📊 STATUS

Premium : {u['premium']}
Expiry : {u['expiry']}
Demo : {u['demo']}
""")

# ===== LOOKUP =====
    elif text=="📱 Lookup":
        send(uid,"Send:\nlookup 9876543210")

    elif text.startswith("lookup"):
        if not u["premium"] and u["demo"]<=0:
            send(uid,"Demo finished")
            return {"ok":True}

        num=text.split(" ")[1]

        if not u["premium"]:
            u["demo"]-=1

        # ===== API SLOT =====
        API="PUT_API"

        data={
        "name":"Demo User",
        "number":num,
        "location":"India",
        "address":"Hidden",
        "father":"Private"
        }

        send(uid,f"""
📊 RESULT

Name :- {data['name']}
Number :- {data['number']}
Location :- {data['location']}
Address :- {data['address']}
SO :- {data['father']}

ID :- {uid}

Credit :- @Zixerworld_bot
""")

# ===== IP TOOL =====
    elif text=="🌐 IP":
        send(uid,"Send ip 8.8.8.8")

    elif text.startswith("ip"):
        ip=text.split(" ")[1]
        send(uid,f"IP : {ip}\nCountry : India\nISP : Demo")

# ===== USER CHECK =====
    elif text=="🔎 User":
        send(uid,"Send user name")

    elif text.startswith("user"):
        uname=text.split(" ")[1]
        send(uid,f"Username : {uname}\nStatus : Available")

# ===== PASSWORD =====
    elif text=="🔐 Pass":
        p=''.join(random.choices(string.ascii_letters+string.digits,k=12))
        send(uid,f"Password:\n<code>{p}</code>")

# ===== ADDRESS =====
    elif text=="📍 Address":
        send(uid,"Name : Rahul\nCity : Mumbai\nState : MH")

# ===== DEVICE =====
    elif text=="📱 Device":
        send(uid,f"User ID : {uid}\nPlatform : Telegram")

# ===== PREMIUM =====
    elif text=="💎 Premium":
        send(uid,"Send payment proof then /paid amount")

# ===== PAYMENT REQUEST =====
    elif text.startswith("/paid"):
        send(uid,"Payment request sent to admin")

# ================= ADMIN =================

    elif text=="/admin" and uid==str(ADMIN_ID):
        send(uid,"Admin Panel\n/users\n/stats\n/ban id\n/unban id\n/add id days\n/broadcast msg")

    elif text=="/users" and uid==str(ADMIN_ID):
        send(uid,str(len(db["users"])))

    elif text=="/stats" and uid==str(ADMIN_ID):
        send(uid,f"Users: {len(db['users'])}\nLogs: {len(db['logs'])}")

    elif text.startswith("/ban") and uid==str(ADMIN_ID):
        i=text.split(" ")[1]
        db["banned"].append(i)
        save()
        send(uid,"Banned")

    elif text.startswith("/unban") and uid==str(ADMIN_ID):
        i=text.split(" ")[1]
        db["banned"].remove(i)
        save()
        send(uid,"Unbanned")

    elif text.startswith("/add") and uid==str(ADMIN_ID):
        p=text.split(" ")
        i=p[1]
        d=int(p[2])
        db["users"][i]["premium"]=True
        db["users"][i]["expiry"]=str(datetime.now()+timedelta(days=d))
        save()
        send(uid,"Premium added")

    elif text.startswith("/broadcast") and uid==str(ADMIN_ID):
        msg=text.replace("/broadcast ","")
        for u in db["users"]:
            send(u,msg)

    save()
    return {"ok":True}
