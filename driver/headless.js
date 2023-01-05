const puppeteer = require("puppeteer");
const fs = require("fs");

(async () => {
  const url = "https://www.cmu.edu/legal/privacy-notice.html";
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setRequestInterception(true)
  page.on ("request", (request) => {
    console.log(`Intercepting: ${request.method} ${request.url}`);
    request.continue();
  });
  await page.goto(url , {waitUntil: "load"});

  const html = await page.content();

  const title = await page.title();
  const datetime = retrieve_timestamp();

  const seperator = " => "
  const filename = title + seperator + datetime + ".html"

  const files = fs.readdirSync(__dirname + "/storage");
  for (let i = 0; i < files.length; i++) {
    let namespace = files[i].split(seperator, 2);
    let name = namespace[0];
    
    if (name === title) {
      fs.rename(__dirname + "/storage/" + files[i], 
                __dirname + "/storage/" + filename, 
                (err) => {
        if (err != null) {
          console.log(err)
        }
      });
    }
  }

  fs.writeFile(__dirname + "/storage/" + filename, 
               html, {encoding: "utf-8", flags: "w+"}, 
               (err) => {
    if (err != null) {
      console.log(err)
    }
  });

  browser.close()
})();

function retrieve_timestamp() {
  const today = new Date()
  const date = today.getFullYear() + '-' + 
              (today.getMonth() + 1) + '-' + 
               today.getDate();

  const time = today.getHours() + ":" + 
               today.getMinutes() + ":" + 
               today.getSeconds();
  
  return date + " " + time;
}