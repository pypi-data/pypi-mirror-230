(function () {
  'use strict';

  angular
    .module('horizon.dashboard.admin.venus')
    .service('venusSrv', venusSrv);

  venusSrv.$inject = ['$http', '$injector'];

  function venusSrv($http, $injector) {
    var venusAPI;

    if ($injector.has('horizon.app.core.openstack-service-api.venus')) {
      venusAPI = $injector.get('horizon.app.core.openstack-service-api.venus');
    }

    function getLogStorageDays() {
      if (venusAPI) {
        return venusAPI.getLogStorageDays()
          .then(function (data) {
            return data;
          })
          .catch(function (err) {
            console.error(err);
          });
      }
    }

    function getLogs(config) {
      config = {params: config};
      if (venusAPI) {
        return venusAPI.getLogs(config)
          .then(function (data) {
            return data;
          })
          .catch(function (err) {
            console.error(err);
          });
      }
    }
    function getAnalysis(config) {
      config = {params: config};
      if (venusAPI) {
        return venusAPI.getAnalysis(config)
          .then(function (data) {
            return data;
          })
          .catch(function (err) {
            console.error(err);
          });
      }
    }
    function getError(config) {
      config = {params: config};
      if (venusAPI) {
        return venusAPI.getError(config)
          .then(function (data) {
            return data;
          })
          .catch(function (err) {
            console.error(err);
          });
      }
    }

    return {
      getLogStorageDays: getLogStorageDays,
      getLogs: getLogs,
      getAnalysis: getAnalysis,
      getError: getError
    };
  }
})();
