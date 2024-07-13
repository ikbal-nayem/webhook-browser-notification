"use strict";

/* eslint-enable max-len */

self.addEventListener("install", function (event) {
  console.log("Service Worker installing.");
});

self.addEventListener("activate", function (event) {
  console.log("Service Worker activating.");
});

self.addEventListener("push", function (event) {
  const pushData = event.data.text();
  console.log(`[Service Worker] Push received this data - "${pushData}"`);
  let data, title, body;
  try {
    data = JSON.parse(pushData);
    title = data.title;
    body = data.body;
  } catch (e) {
    title = "GEMS Developers";
    body = pushData;
  }
  const options = {
    body: body,
    tag: data?.tag || "gems-developers",
    icon: "https://gems.gov.bd/media/logos/default-large.png",
    vibrate: [200, 100, 200],
  };
  event.waitUntil(self.registration.showNotification(title, options));
});
