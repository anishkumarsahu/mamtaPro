// Define the version of the cache, allowing for easy updates
const CACHE_VERSION = 'v1.1.22';
const CACHE_NAME = `${CACHE_VERSION}::fundamentals`;
const MAX_CACHE_ITEMS = 100; // Limit the number of items in the cache

// Define the list of URLs to cache
const URLS_TO_CACHE = [
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
];

// List of file extensions and MIME types to cache
const CACHEABLE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'svg', 'css', 'js'];
const CACHEABLE_CONTENT_TYPES = ['image/', 'text/css', 'application/javascript', 'application/json'];

// Maximum number of retries for network requests
const MAX_RETRIES = 5;

// Install event: Cache static assets
self.addEventListener('install', async (event) => {
    console.log('WORKER: Install event in progress.');

    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('WORKER: Caching assets...');
            return cache.addAll(URLS_TO_CACHE);
        }).then(() => {
            console.log('WORKER: Install completed.');
        }).catch((error) => {
            console.error('WORKER: Failed to cache assets:', error);
        })
    );
});

// Fetch event: Serve cached content or fetch from network with retry
self.addEventListener('fetch', (event) => {
    console.log(`WORKER: Fetch event for ${event.request.url}`);

    if (event.request.method !== 'GET') {
        console.warn('WORKER: Fetch event ignored for non-GET request.');
        return;
    }

    event.respondWith(handleFetchWithRetry(event, event.request));
});

// Activate event: Clean up old caches
self.addEventListener('activate', async (event) => {
    console.log('WORKER: Activate event in progress.');

    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => !key.startsWith(CACHE_VERSION))
                    .map((key) => {
                        console.log(`WORKER: Deleting cache ${key}`);
                        return caches.delete(key);
                    })
            );
        }).then(() => {
            console.log('WORKER: Activate completed. Old caches removed.');
        }).catch((error) => {
            console.error('WORKER: Failed to remove old caches:', error);
        })
    );
});

// Handle fetch requests with retry logic
async function handleFetchWithRetry(event, request, retries = 0) {
    try {
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            console.log(`WORKER: Serving from cache: ${request.url}`);
            // Stale-while-revalidate strategy
            event.waitUntil(updateCache(request));
            return cachedResponse;
        }

        const networkResponse = await fetchWithTimeout(request);
        console.log(`WORKER: Fetched from network: ${request.url}`);

        if (isCacheable(networkResponse, request.url)) {
            const cache = await caches.open(CACHE_NAME);
            await cache.put(request, networkResponse.clone());
            console.log(`WORKER: Cached response for: ${request.url}`);
            await enforceCacheSizeLimit(cache); // Enforce cache size limit
        }

        return networkResponse;

    } catch (error) {
        console.error(`WORKER: Fetch attempt ${retries + 1} failed for ${request.url}:`, error);

        if (retries < MAX_RETRIES) {
            const retryDelay = Math.pow(2, retries) * 100; // Exponential backoff
            console.log(`WORKER: Retrying fetch for ${request.url} in ${retryDelay}ms...`);
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(handleFetchWithRetry(event, request, retries + 1));
                }, retryDelay);
            });
        }

        console.error('WORKER: Fetch request failed after maximum retries.');
return new Response(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Service Unavailable</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                max-width: 600px;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            h1 {
                font-size: 24px;
                color: #d9534f;
                margin-bottom: 16px;
            }
            p {
                font-size: 16px;
                color: #555;
            }
            a {
                color: #007bff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .button {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                font-size: 16px;
                color: #fff;
                background-color: #007bff;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Service Unavailable</h1>
            <p>Oops! It seems there was a problem retrieving the content. Please try the following:</p>
            <ul>
                <li>Check your internet connection.</li>
                <li>Refresh the page in a few moments.</li>
                <li>Contact support if the problem persists.</li>
            </ul>
            <button class="button" onclick="location.reload()">Try Again</button>
        </div>
    </body>
    </html>
`, {
    status: 503,
    statusText: 'Service Unavailable',
    headers: new Headers({
        'Content-Type': 'text/html'
    })
});
    }
}

// Check if the response is cacheable
function isCacheable(response, url) {
    const contentType = response.headers.get('Content-Type') || '';
    const extension = getUrlExtension(url).toLowerCase();
    const scheme = new URL(url).protocol;

    // Only cache resources that are served over HTTP or HTTPS
    return (
        (scheme === 'http:' || scheme === 'https:') &&
        (CACHEABLE_EXTENSIONS.includes(extension) ||
        CACHEABLE_CONTENT_TYPES.some((type) => contentType.startsWith(type)))
    );
}

// Helper function to get the file extension
function getUrlExtension(url) {
    return typeof url === 'string' ? url.split(/[#?]/)[0].split('.').pop().trim() : '';
}

// Fetch with a timeout to prevent hanging requests
function fetchWithTimeout(request, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Request timed out')), timeout);

        fetch(request).then(
            (response) => {
                clearTimeout(timer);
                resolve(response);
            },
            (err) => {
                clearTimeout(timer);
                reject(err);
            }
        );
    });
}

// Update cache for a request
async function updateCache(request) {
    try {
        const response = await fetchWithTimeout(request);
        if (response && isCacheable(response, request.url)) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
            console.log(`WORKER: Updated cache for ${request.url}`);
            await enforceCacheSizeLimit(cache); // Enforce cache size limit
        }
    } catch (error) {
        console.error(`WORKER: Failed to update cache for ${request.url}:`, error);
    }
}

// Enforce cache size limit by removing least recently used items
async function enforceCacheSizeLimit(cache) {
    const keys = await cache.keys();
    if (keys.length > MAX_CACHE_ITEMS) {
        console.log(`WORKER: Cache size exceeded limit of ${MAX_CACHE_ITEMS}. Removing oldest item.`);
        await cache.delete(keys[0]);
    }
}