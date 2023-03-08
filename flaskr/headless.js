const puppeteer = require("puppeteer");
const fs = require("fs");

const seperator = " -- "

const policies_directory = "./templates/policies/";
const metadata_directory = "./storage/metadata/";

const concepts_txt = "./storage/concepts.txt";
const objects_json = "./storage/objects.json";

const url = "https://www.cmu.edu/legal/privacy-notice.html";

function retrieve_keywords() {
  if (!fs.existsSync(concepts_txt)) {
    const objects = [];
    const json = JSON.parse(fs.readFileSync(objects_json, {encoding:'utf8', flag:'r'}));
    for (const key in json) {
      concept = (key.replace(/_/g, " ")).trim();
      if (/\s/g.test(concept)) {
        objects.push(concept);
      }
    }

    objects.sort((a, b) => a.length - b.length);
    objects.reverse();

    for (let i = 0; i < objects.length; i++) {
      if (i != objects.length - 1) {
        fs.writeFileSync(concepts_txt, objects[i] + "\n", {encoding:'utf8', flag:'a+'});
      } else {
        fs.writeFileSync(concepts_txt, objects[i], {encoding:'utf8', flag:'a+'});
      }
    }
  }
}

function retrieve_time() {
  const today = new Date();
  const date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  const day = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  return date + " " + day;
}

function renew(title, time) {
  const source_json = `${metadata_directory}${title}.json`;
  if (fs.existsSync(source_json)) {
    const json = JSON.parse(fs.readFileSync(source_json, {encoding:'utf8', flag:'r'}));
    const yesterday = json.__time;
    const today = time;

    const t1 = new Date(yesterday);
    const t2 = new Date(today);
    const diff = Math.floor((t2 - t1) / (1000*36000*24));
    
    if (diff < 30) {
      return false;
    }
    return true;    
  } else {
    return true;
  }
}

function has_overlap(matches, span) {
  start = span[0];
  end = span[1];

  for (let i = 0; i < matches.length; i++) {
    existing_start = matches[i][0];
    existing_end = matches[i][1];
    if (existing_start <= start && end <= existing_end) {
      return true;
    }
  }

  return false;
}

function process(title, text, time) {
  const data = fs.readFileSync(concepts_txt, {encoding:'utf8', flag:'r'});
  const keywords = data.split("\n");

  var matches = new Set();
  var concepts = [];

  for (let i = 0; i < keywords.length; i++) {
    const re = new RegExp(`\\b${keywords[i]}\\b`);
    const search = text.search(re)
    if (search != -1) {
      const span = [search, search + keywords[i].length];
      if (!has_overlap(matches, span)) {
        concepts.push(keywords[i].toLowerCase());
        matches.add(span);
      }
    }
  }

  concepts.sort((a, b) => a.length - b.length);
  concepts.reverse();
  
  number_of_concepts = concepts.length;

  const metadata = {"__url": url,
                    "__title": title,
                    "__time": time, 
                    "__number_of_concepts": number_of_concepts,
                    "__concepts": concepts};
  
  const config = JSON.stringify(metadata)

  fs.writeFileSync(`${metadata_directory}${title}.json`, config, {encoding:'utf8', flag:'w+'});
}

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

  const text = await page.$eval('*', (el) => {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNode(el);
    selection.removeAllRanges();
    selection.addRange(range);
    return window.getSelection().toString();
  });

  const time = retrieve_time();

  if (renew(title, time)) {
    process(title, text, time)
  }

  const json = JSON.parse(fs.readFileSync(`${metadata_directory}${title}.json`),
    {encoding:'utf8', flag:'r'});
  
  const objects = json.__concepts;
  const timestamp = json.__time;

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