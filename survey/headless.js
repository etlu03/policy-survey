const puppeteer = require("puppeteer");
const fs = require("fs");

const seperator = " -- ";

const storage_directory = "/templates/";
const metadata_directory = "/metadata/";

(async () => {
  const url = "https://www.cmu.edu/legal/privacy-notice.html";
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setRequestInterception(true);
  page.on ("request", (request) => {
    console.log(`Intercepting: ${request.method} ${request.url}`);
    request.continue();
  });
  await page.goto(url , {waitUntil: "load"});

  const html = await page.content();

  const title = await page.title();
  const today = retrieve_timestamp();

  const filename = title + seperator + today + ".html";
  var first_instance = true;

  const files = fs.readdirSync(`${__dirname}${storage_directory}`);
  for (let i = 0; i < files.length; i++) {
    let namespace = files[i].split(seperator, 2);
    let name = namespace[0];
    
    if (name === title) {
      first_instance = false;
      fs.readFile(`${__dirname}${metadata_directory}${title}.json`, 
                  (err, data) => {
                    if (err != null) {
                      console.log(err);
                      return;
                    }

        let json = JSON.parse(data);
        let yesterday = json._page_timestamp;

        if (renew_audit(yesterday, today) === true) {
          fs.rename(`${__dirname}${storage_directory}${files[i]}`, 
                    `${__dirname}${storage_directory}${filename}`, 
                    (err) => {
                      if (err != null) {
                        console.log(err);
                        return;
                      }
                   });

          fs.writeFile(`${__dirname}${storage_directory}${filename}`,
                       html, {encoding: "utf-8", flags: "w+"},
                       (err) => {
                        if (err != null) {
                          console.log(err);
                          return;
                        }
                      });
        }
      });
    }
  }

  if (first_instance == true) {
    fs.writeFile(__dirname + storage_directory + filename,
                 html, {encoding: "utf-8", flags: "w+"},
                 (err) => {
                  if (err != null) {
                    console.log(err);
                    return;
                  }
                });
  }

  browser.close();
})();

function retrieve_timestamp() {
  const today = new Date();
  const date = today.getFullYear() + '-' + 
              (today.getMonth() + 1) + '-' + 
               today.getDate();

  const time = today.getHours() + ":" + 
               today.getMinutes() + ":" + 
               today.getSeconds();
  
  return date + " " + time;
}

function renew_audit(timestamp1, timestamp2) {
  const time1 = timestamp1.split(/[: -]/);
  const time2 = timestamp2.split(/[: -]/);

  for (let i = 0; i < time1.length; i++) {
    if (time1[i].length < 2) {
      time1[i] = "0" + time1[i];
    }
  }

  for (let i = 0; i < time2.length; i++) {
    if (time2[i].length < 2) {
      time2[i] = "0" + time2[i];
    }
  }

  const date1 = new Date(time1[0] + "/" + time1[1] + "/" + time1[2]);
  const date2 = new Date(time2[0] + "/" + time2[1] + "/" + time2[2]);

  const diff = (date2.getTime() - date1.getTime()) / (1000 * 3600 * 24);

  return 30 < diff;
}