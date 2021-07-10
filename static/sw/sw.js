var version = 'v1.1.7::';
self.addEventListener("install", function (event) {
    console.log('WORKER: install event in progress.');
    event.waitUntil(
        caches
            .open(version + 'fundamentals')
            .then(function (cache) {
                return cache.addAll([
                    'https://fonts.googleapis.com/css?family=Roboto:400,700&subset=latin,cyrillic-ext',
                    'https://fonts.googleapis.com/icon?family=Material+Icons',
                    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css',
                    '/static/plugins/node-waves/waves.min.css',
                    'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css',
                    '/static/plugins/morrisjs/morris.css',
                    '/static/css/style.min.css',
                    '/static/css/themes/all-themes.min.css',
                    'https://cdn.datatables.net/1.10.25/css/dataTables.bootstrap.min.css',
                    'https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js',
                    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/jQuery-slimScroll/1.3.8/jquery.slimscroll.min.js',
                    '/static/plugins/node-waves/waves.min.js',
                    '/static/plugins/jquery-countto/jquery.countTo.js',
                    '/static/plugins/raphael/raphael.min.js',
                    '/static/plugins/morrisjs/morris.min.js',
                    '/static/js/admin.js',
                    '/static/js/pages/index.js',
                    '/static/js/demo.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.4.1/chart.min.js',
                    '/static/js/pages/ui/modals.js',
                    'https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js',
                    'https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap.min.js',
                    '/static/date/bootstrap-datepicker.css',
                    '/static/date/bootstrap-datepicker.js',
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css',
                    'https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.12/dist/css/bootstrap-select.min.css',
                    'https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.12/dist/js/bootstrap-select.min.js'
                ]);
            })
            .then(function () {
                console.log('WORKER: install completed');
            })
    );
});
function get_url_extension(url) {
    return url.split(/[#?]/)[0].split('.').pop().trim();
}
self.addEventListener("fetch", function (event) {
    console.log('WORKER: fetch event in progress.');
    if (event.request.method !== 'GET') {
        return;
    }
    event.respondWith(
        caches
            .match(event.request)
            .then(function (cached) {
                var networked = fetch(event.request)
                    .then(fetchedFromNetwork, unableToResolve)
                    .catch(unableToResolve);
                // console.log('WORKER: fetch event', cached ? '(cached)' : '(network)', event.request.url);
                return cached || networked;
                function fetchedFromNetwork(response) {
                    var cacheCopy = response.clone();
                    caches
                        .open(version + 'pages')
                        .then(function add(cache) {
                            var img = get_url_extension(event.request.url);
                            if (img.toLowerCase() === 'png' || img.toLowerCase() === 'jpg' || img.toLowerCase() === 'jpeg' || img.toLowerCase() === 'svg') {
                                cache.put(event.request, cacheCopy);
                            }
                        })
                        .then(function () {
                            // console.log('WORKER: fetch response stored in cache.', event.request.url);
                        });
                    return response;
                }

                function unableToResolve() {
                    // console.log('WORKER: fetch request failed in both cache and network.');
                    return new Response('<h1>Service Unavailable</h1>', {
                        status: 503,
                        statusText: 'Service Unavailable',
                        headers: new Headers({
                            'Content-Type': 'text/html'
                        })
                    });
                }
            })
    );
});
self.addEventListener("activate", function (event) {
    console.log('WORKER: activate event in progress.');
    event.waitUntil(
        caches
            .keys()
            .then(function (keys) {
                return Promise.all(
                    keys
                        .filter(function (key) {
                            return !key.startsWith(version);
                        })
                        .map(function (key) {
                            return caches.delete(key);
                        })
                );
            })
            .then(function () {
                console.log('WORKER: activate completed.');
            })
    );
});

