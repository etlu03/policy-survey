from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("Privacy Notice - CMU - Carnegie Mellon University -- 2023-1-29 15:55:43.html")

if __name__ == "__main__":
    app.run()