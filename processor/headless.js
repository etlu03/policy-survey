const puppeteer = require("puppeteer");
const fs = require("fs");

const seperator = " -- ";

const storage_directory = "/static/";
const metadata_directory = "/metadata/";

var filename = undefined;

const url = process.argv.slice(1)[1];

(async () => {
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

  var first_instance = true;
  const files = fs.readdirSync(`${__dirname}${storage_directory}`);
  for (let i = 0; i < files.length; i++) {
    let namespace = files[i].split(seperator, 2);
    let pagename = namespace[0];

    if (pagename === title) {
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
          } else {
            filename = title + seperator + yesterday + ".html";
          }
      });
      break;
    }
  }

  if (first_instance === true) {
    fs.readFile(`${__dirname}${metadata_directory}${title}.json`, 
                    (err, data) => {
                      if (err != null) {
                        console.log(err);
                        return;
                      }

          let json = JSON.parse(data);
          let yesterday = json._page_timestamp;

          filename = title + seperator + yesterday + ".html";

          fs.writeFile(`${__dirname}${storage_directory}${filename}`,
                          html, {encoding: "utf-8", flags: "w+"},
                          (err) => {
                            if (err != null) {
                              console.log(err);
                              return;
                            }
                          });
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

function renew_audit(time1, time2) {
  const t1 = time1.split(/[: -]/);
  const t2 = time2.split(/[: -]/);

  for (let i = 0; i < t1.length; i++) {
    if (t1[i].length < 2) {
      t1[i] = "0" + t1[i];
    }
  }

  for (let i = 0; i < t2.length; i++) {
    if (t2[i].length < 2) {
      t2[i] = "0" + t2[i];
    }
  }

  const date1 = new Date(t1[0] + "/" + t1[1] + "/" + t1[2]);
  const date2 = new Date(t2[0] + "/" + t2[1] + "/" + t2[2]);

  const diff = (date2.getTime() - date1.getTime()) / (1000 * 3600 * 24);

  return 30 < diff;
}