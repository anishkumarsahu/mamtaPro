self.addEventListener('install', function(event){

	console.log('installed');
	event.waitUntil(
	    caches.open('static')
        .then(function (cache) {
            cache.addAll([
                '/static/plugins/bootstrap/css/bootstrap.css',
                '/static/plugins/node-waves/waves.css',
                '/static/plugins/animate-css/animate.css',
                '/static/plugins/morrisjs/morris.css',
                '/static/css/style.css',
                '/static/css/themes/all-themes.css',
                '/static/plugins/jquery/jquery.min.js',
                '/static/plugins/bootstrap/js/bootstrap.js',
                '/static/plugins/node-waves/waves.js',
                '/static/plugins/jquery-countto/jquery.countTo.js',
                '/static/plugins/raphael/raphael.min.js',
                '/static/plugins/morrisjs/morris.js',
                '/static/js/admin.js',
                '/static/js/pages/index.js',
                '/static/js/demo.js',
                '/static/plugins/chartjs/Chart.min.js',
                '/static/js/pages/ui/modals.js',
                '/static/plugins/jquery-datatable/skin/bootstrap/css/dataTables.bootstrap.css',
                '/static/date/bootstrap-datepicker.css',
                '/static/plugins/jquery-datatable/jquery.dataTables.js',
                '/static/plugins/jquery-datatable/skin/bootstrap/js/dataTables.bootstrap.js',
                '/static/plugins/jquery-datatable/extensions/export/dataTables.buttons.min.js',
                '/static/plugins/jquery-datatable/extensions/export/jszip.min.js',
                '/static/plugins/jquery-datatable/extensions/export/buttons.html5.min.js',
                '/static/plugins/jquery-datatable/extensions/export/buttons.print.min.js',
                '/static/date/bootstrap-datepicker.js',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css'
            ]);

        })
    );

});

self.addEventListener('activate', function(event){
    console.log('activated');
});

self.addEventListener('fetch', function(event){
  event.respondWith(
      caches.match(event.request).then(function (res) {
          if (res){
              return res;
          }
          else {
              return fetch(event.request);
          }
      })
  )
  // return something for each interception
});/**
 * Created by anish on 15/7/19.
 */
