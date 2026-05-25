const CACHE_NAME = 'novel-reader-v1';
const PRECACHE_ASSETS = [
  '/',
  '/static/icon.svg',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 仅拦截 http/https，并排除 API、登录、登出和搜索等动态交互页面
  if (!event.request.url.startsWith('http') || 
      url.pathname.startsWith('/api') || 
      url.pathname === '/login' || 
      url.pathname === '/logout' || 
      url.pathname === '/search') {
    return;
  }

  // 1. 静态资源（图片、SVG、外部字体等）：缓存优先 (Cache First, fallback to Network and Cache)
  if (url.pathname.startsWith('/static/') || 
      url.hostname.includes('fonts.googleapis.com') || 
      url.hostname.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.match(event.request).then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          }
          return networkResponse;
        }).catch(() => {
          // 静态资源加载失败，可静默失败
        });
      })
    );
    return;
  }

  // 2. 页面 HTML（首页、详情页、阅读页等）：网络优先，失败退回缓存 (Network First, fallback to Cache)
  event.respondWith(
    fetch(event.request)
      .then(networkResponse => {
        // 如果是有效页面，缓存它
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
        }
        return networkResponse;
      })
      .catch(() => {
        // 网络失败（离线），尝试匹配缓存
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // 如果是页面 HTML 且离线，则返回一个友好的离线提示页面
          if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
            return new Response(
              `<!DOCTYPE html>
               <html lang="zh-CN">
               <head>
                 <meta charset="UTF-8">
                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
                 <title>离线模式 - 小说阅读器</title>
                 <style>
                   body {
                     background: #0b0f19;
                     color: #f3f4f6;
                     font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                     display: flex;
                     flex-direction: column;
                     align-items: center;
                     justify-content: center;
                     min-height: 100vh;
                     margin: 0;
                     padding: 20px;
                     text-align: center;
                     box-sizing: border-box;
                   }
                   h1 { font-size: 1.8rem; margin-bottom: 1rem; color: #fbbf24; }
                   p { color: #9ca3af; font-size: 1rem; margin-bottom: 2rem; max-width: 400px; line-height: 1.5; }
                   .btn {
                     background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                     color: white;
                     text-decoration: none;
                     padding: 0.8rem 2rem;
                     border-radius: 10px;
                     font-weight: bold;
                     box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
                   }
                 </style>
               </head>
               <body>
                 <h1>📡 您已离线</h1>
                 <p>当前页面尚未下载到本地，且您的网络连接已断开。请连接网络或在书架阅读已下载的小说。</p>
                 <a href="/" class="btn">返回首页书架</a>
               </body>
               </html>`,
              {
                headers: { 'Content-Type': 'text/html; charset=utf-8' }
              }
            );
          }
        });
      })
  );
});
