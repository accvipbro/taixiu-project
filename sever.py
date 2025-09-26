from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, random

app = Flask(__name__)
CORS(app)

DATA_FILE = "data.json"

# Hàm load dữ liệu từ file
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Hàm lưu dữ liệu
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/register", methods=["POST"])
def register():
    data = load_data()
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")

    # check trùng tên
    for u in data["users"]:
        if u["username"] == username:
            return "Tài khoản đã tồn tại!", 400

    # thêm user mới
    data["users"].append({
        "username": username,
        "password": password,
        "balance": 1000,   # số dư mặc định
        "history": []
    })
    save_data(data)
    return "Đăng ký thành công!"

@app.route("/login", methods=["POST"])
def login():
    data = load_data()
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")

    for u in data["users"]:
        if u["username"] == username and u["password"] == password:
            return jsonify({"success": True, "balance": u["balance"]})
    return jsonify({"success": False}), 401

@app.route("/play", methods=["POST"])
def play():
    data = load_data()
    body = request.get_json()
    username = body.get("username")
    choice = body.get("choice")

    # tìm user
    user = next((u for u in data["users"] if u["username"] == username), None)
    if not user:
        return jsonify({"error": "User không tồn tại"}), 404

    dice = random.randint(3, 18)
    win = (choice == "tai" and dice >= 11) or (choice == "xiu" and dice <= 10)

    if win:
        user["balance"] += 100
    else:
        user["balance"] -= 100

    # lưu lịch sử
    user["history"].append({
        "choice": choice,
        "dice": dice,
        "win": win
    })

    save_data(data)
    return jsonify({"dice": dice, "win": win, "balance": user["balance"]})

@app.route("/history/<username>", methods=["GET"])
def history(username):
    data = load_data()
    user = next((u for u in data["users"] if u["username"] == username), None)
    if not user:
        return jsonify([])
    return jsonify(user["history"])

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    data = load_data()
    sorted_users = sorted(data["users"], key=lambda x: x["balance"], reverse=True)
    top_users = [{"username": u["username"], "balance": u["balance"]} for u in sorted_users[:10]]
    return jsonify(top_users)

if __name__ == "__main__":
    app.run(debug=True)
