from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
  if request.method == "POST":
    print(request.form.get("url"))
    
  return render_template("./audit/home.html")

if __name__ == "__main__":
  app.run()