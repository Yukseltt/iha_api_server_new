from flask import Flask, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

# Mock kullanıcı bilgisi
VALID_USERNAME = "takimkadi"
VALID_PASSWORD = "takimsifresi"
TEAM_NUMBER = 1

# Oturum kontrolü
session_active = False

# Telemetri kayıtları
telemetries = {}

# QR ve HSS mock verileri
qr_coord = {
    "qrEnlem": 41.51238882,
    "qrBoylam": 36.11935778
}

hss_active = True
hss_data = [
    {"id": 0, "hssEnlem": 40.23260922, "hssBoylam": 29.00573015, "hssYaricap": 50},
    {"id": 1, "hssEnlem": 40.23351019, "hssBoylam": 28.99976492, "hssYaricap": 50},
    {"id": 2, "hssEnlem": 40.23105297, "hssBoylam": 29.00744677, "hssYaricap": 75},
    {"id": 3, "hssEnlem": 40.23090554, "hssBoylam": 29.00221109, "hssYaricap": 150}
]

def get_server_time():
    now = datetime.utcnow()
    return {
        "gun": now.day,
        "saat": now.hour,
        "dakika": now.minute,
        "saniye": now.second,
        "milisaniye": int(now.microsecond / 1000)
    }

@app.route("/api/giris", methods=["POST"])
def giris():
    global session_active
    data = request.json
    if not data:
        return "Format hatası", 204

    if data.get("kadi") == VALID_USERNAME and data.get("sifre") == VALID_PASSWORD:
        session_active = True
        return jsonify({"takim_numarasi": TEAM_NUMBER}), 200
    else:
        return "Geçersiz kullanıcı adı veya şifre", 400


@app.route("/api/sunucusaati", methods=["GET"])
def sunucu_saati():
    if not session_active:
        return "Kimliksiz erişim!", 401
    return jsonify(get_server_time())


@app.route("/api/telemetri_gonder", methods=["POST"])
def telemetri_gonder():
    if not session_active:
        return "Kimliksiz erişim!", 401

    data = request.json
    if not data:
        return "Format hatası", 204

    team_no = data.get("takim_numarasi")
    telemetries[team_no] = {
        "iha_enlem": data.get("iha_enlem", 0),
        "iha_boylam": data.get("iha_boylam", 0),
        "iha_irtifa": data.get("iha_irtifa", 0),
        "iha_dikilme": data.get("iha_dikilme", 0),
        "iha_yonelme": data.get("iha_yonelme", 0),
        "iha_yatis": data.get("iha_yatis", 0),
        "iha_hizi": data.get("iha_hiz", 0),
        "timestamp": time.time()
    }

    # Diğer takımların mock konumları
    konum_bilgileri = []
    for tno, tele in telemetries.items():
        konum_bilgileri.append({
            "takim_numarasi": tno,
            "iha_enlem": tele["iha_enlem"],
            "iha_boylam": tele["iha_boylam"],
            "iha_irtifa": tele["iha_irtifa"],
            "iha_dikilme": tele["iha_dikilme"],
            "iha_yonelme": tele["iha_yonelme"],
            "iha_yatis": tele["iha_yatis"],
            "iha_hizi": tele["iha_hizi"],
            "zaman_farki": int((time.time() - tele["timestamp"]) * 1000)
        })

    return jsonify({
        "sunucusaati": get_server_time(),
        "konumBilgileri": konum_bilgileri
    })


@app.route("/api/kilitlenme_bilgisi", methods=["POST"])
def kilitlenme():
    if not session_active:
        return "Kimliksiz erişim!", 401
    return "Kilitlenme bilgisi alındı", 200


@app.route("/api/kamikaze_bilgisi", methods=["POST"])
def kamikaze():
    if not session_active:
        return "Kimliksiz erişim!", 401
    return "Kamikaze bilgisi alındı", 200


@app.route("/api/qr_koordinati", methods=["GET"])
def qr_coord_api():
    if not session_active:
        return "Kimliksiz erişim!", 401
    return jsonify(qr_coord)


@app.route("/api/hss_koordinatlari", methods=["GET"])
def hss_coord_api():
    if not session_active:
        return "Kimliksiz erişim!", 401

    if not hss_active:
        return jsonify([])

    return jsonify({
        "sunucusaati": get_server_time(),
        "hss_koordinat_bilgileri": hss_data
    })


app.run(host="0.0.0.0", port=5000)
