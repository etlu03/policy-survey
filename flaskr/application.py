from flask import Flask, request, render_template
import asyncio

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
  if request.method == "POST":
    url = request.form.get("url")
    asyncio.run(retrieve(url))
    
  return render_template("./audit/home.html")

async def worker(url, queue):
  while True:
    sleep_for = await queue.get()
    await asyncio.sleep(sleep_for)
    queue.task_done()
    
async def retrieve(url):
  queue = asyncio.Queue()
  tasks = []

  task = asyncio.create_task(worker(url, queue))
  tasks.append(task)

  await queue.join()

  for task in tasks:
    task.cancel()
  
  await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
  app.run()