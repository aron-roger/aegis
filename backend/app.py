from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "aegis backend is live!"

if __name__ == "__main__":
    app.run(debug=True)


