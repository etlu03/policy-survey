const puppeteer = require('puppeteer');

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

  const html = await page.content()
  console.log(html);

  browser.close()
})();