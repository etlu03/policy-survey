const puppeteer = require("puppeteer");
const fs = require("fs");

const seperator = " -- "

const policies_directory = "../templates/policies/";
const metadata_directory = "../storage/metadata/";

var filename = undefined;

const url = process.argv.slice(1)[1];

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setRequestInterception(true);
  page.on ("request", (request) => {
    request.continue();
  });
  await page.goto(url, {waitUntil: "load"});

  const html = await page.content();
  const title = await page.title();

  var first_instance = true;
  const files = fs.readdirSync(`${policies_directory}`)
  for (let i = 0; i < files.length; i++) {
    let namespace = files[i].split(seperator, 2);
    let page_title = namespace[0];
    if (page_title === title) {
      first_instance = false;
      fs.readFile(`${metadata_directory}${title}.json`,
        (err, data) => {
          if (err != null) {
            console.log(err);
            return;
          }

          fs.rename(`${policies_directory}${files[i]}`, `${policies_directory}${filename}`,
            (err) => {
              if (err != null) {
                console.log(err);
                return;
              }
            });
          
          fs.writeFile(`${policies_directory}${filename}`, html, {encoding:"utf-8", flags:"w+"},
            (err) => {
              if (err != null) {
                console.log(err);
                return;
              }
            });
        });
      break;
    }
  }

  if (first_instance == true) {
    fs.readFile(`${metadata_directory}${title}.json`,
      (err, data) => {
        if (err != null) {
          console.log(err);
          return;
        }

        let json = JSON.parse(data);
        let timestamp = json.__timestamp;

        filename = title + seperator + timestamp + ".html";
        fs.writeFile(`${policies_directory}${filename}`, html, {encoding:"utf-8", flags:"w+"}, (err) => {
          if (err != null) {
            console.log(err);
            return;
          }
        });
      });
  }
  
  browser.close();
})();