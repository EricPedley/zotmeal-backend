const versionNumber = "1.0.1";
 
self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(versionNumber).then(function (cache) {
      return cache.addAll(["/"]);
    })
  );
});
 
self.addEventListener("fetch", function (event) {
  event.respondWith(
    caches.match(event.request).then(function (response) {
      return response || fetch(event.request);
    })
  );
});