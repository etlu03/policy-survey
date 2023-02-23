const puppeteer = require("puppeteer");
const fs = require("fs");

const seperator = " -- "

const policies_directory = "./templates/policies/";
const metadata_directory = "./storage/metadata/";

const url = process.argv.slice(1)[1];

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setRequestInterception(true);
  page.on ("request", (request) => {
    request.continue();
  });
  await page.goto(url, {waitUntil: "load"});

  var html = await page.content();
  const title = await page.title();
  
  const json = JSON.parse(fs.readFileSync(`${metadata_directory}${title}.json`),
    {encoding:'utf8', flag:'r'});
  
  const objects = json.__concepts;
  const timestamp = json.__timestamp;

  const filename = title + seperator + timestamp + ".html";

  for (let i = 0; i < objects.length; i++) {
    let re = new RegExp(`\\b${objects[i]}\\b`, "gi");
    html = html.replace(re, `<span style="color:blue">${objects[i]}</span>`);
  }

  var first_instance = true;
  const files = fs.readdirSync(`${policies_directory}`);
  for (let i = 0; i < files.length; i++) {
    let namespace = files[i].split(seperator, 2);
    let name = namespace[0];
    if (name === title) {
      first_instance = false;

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
      break;
    }
  }

  if (first_instance === true) {
    fs.writeFile(`${policies_directory}${filename}`, html, {encoding:"utf-8", flags:"w+"}, 
      (err) => {
        if (err != null) {
          console.error(err);
          return;
        }
    });
  }
  
  browser.close();
})();