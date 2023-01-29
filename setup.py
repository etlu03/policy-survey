import os

node_modules = ["puppeteer", "fs"]

if __name__ == "__main__":
  for module in node_modules:
    os.system("npm install " + module)

  os.system("pip install -r requirements.txt")