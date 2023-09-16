(function () {
  'use strict';

  angular
      .module('horizon.dashboard.admin.venus')
      .controller('ConfigurationController', ConfigurationController);

  ConfigurationController.$inject = ['$scope', 'venusSrv'];

  function ConfigurationController($scope, venusSrv) {
    $scope.STATIC_URL = STATIC_URL;
    $scope.logStorageDays = 0;

    $scope.getData = function () {
      venusSrv.getLogStorageDays().then(function (res) {
        $scope.logStorageDays = 0;
        $scope.logStorageDays = res.data.log_save_days;
      });
    };

    function init() {
      $scope.getData();
    }

    init();
  }

})();
