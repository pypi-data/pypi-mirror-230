(function () {
  'use strict';

  angular
      .module('horizon.dashboard.admin.venus')
      .controller('LogSearchController', LogSearchController);

  LogSearchController.$inject = ['$scope', 'venusSrv'];

  function LogSearchController($scope, venusSrv) {
    $scope.STATIC_URL = STATIC_URL;
    $scope.model = {
      start_time: new Date(),
      end_time: new Date(),
      condition: 'module_name',
      condition_value: '',
      page_size: horizon.cookies.get('API_RESULT_PAGE_SIZE') || 20,
      page_num: 1
    };
    $scope.total = 0;
    $scope.tableData = [];
    $scope.chartsData = []; // 数据形如：{key_as_string: '2022-05-30T15:30:00.000+08:00', doc_count: 20}

    $scope.getData = function () {
      var config = {
        start_time: $scope.model.start_time.getTime() / 1000,
        end_time: $scope.model.end_time.getTime() / 1000,
        page_size: $scope.model.page_size,
        page_num: $scope.model.page_num,
        module_name: '',
        host_name: '',
        program_name: '',
        level: ''
      };
      if ($scope.model.condition == 'module_name') {
        config.module_name = $scope.model.condition_value;
      }
      if ($scope.model.condition == 'host_name') {
        config.host_name = $scope.model.condition_value;
      }
      if ($scope.model.condition == 'program_name') {
        config.program_name = $scope.model.condition_value;
      }
      if ($scope.model.condition == 'level') {
        config.level = $scope.model.condition_value;
      }
      venusSrv.getLogs(config).then(function (res) {
        $scope.tableData = [];
        if (res.data.hasOwnProperty('data')) {
          $scope.tableData = res.data.data.values;
          $scope.chartsData = res.data.data_stats.count;
          $scope.total = res.data.data.total;
        }
        $scope.updateChart();
      });
    };

    $scope.updateChart = function () {
      var data = $scope.chartsData;

      var padding = {
        top: 50,
        right: 50,
        bottom: 50,
        left: 100
      };

      var barGap = 2;

      var svg = d3.select('#svg');

      var width = svg.node().getBoundingClientRect().width - padding.left - padding.right,
          height = svg.node().getBoundingClientRect().height - padding.top - padding.bottom,
          barHotZoneWidth = data.length != 0 ? width / data.length : 0,
          barHotZoneHighlight = '#ddd',
          barWidth = barHotZoneWidth - barGap,
          barBgColor = '#007ede';

      var xScale = d3.scale.linear()
          .domain([0, data.length])
          .range([0, width]);

      var yScale = d3.scale.linear()
          .domain(d3.extent(data, d => d.doc_count))
          .range([height, 0]);

      var xAxis = d3.svg.axis()
          .scale(xScale)
          .orient('bottom');

      var yAxis = d3.svg.axis()
          .scale(yScale)
          .orient('left');

      svg.select('#xAxis')
          .remove();

      svg.append('g')
          .attr('id', 'xAxis')
          .attr('transform', 'translate('+padding.left+', '+(height+padding.top)+')')
          .attr("class", "axis")
          .call(xAxis);

      svg.select('#yAxis')
          .remove();

      svg.append('g')
          .attr('id', 'yAxis')
          .attr('transform', 'translate('+padding.left+', '+padding.top+')')
          .attr("class", "axis")
          .call(yAxis);

      svg.select('#bar-container')
          .remove();

      var barContainer = svg.append('g')
          .attr('id', 'bar-container')
          .attr('transform', 'translate('+padding.left+', '+padding.top+')');

      var bars = barContainer.selectAll('g')
          .data(data);

      // enter
      var barG = bars.enter()
          .append('g');

      var barHotZone = barG.append('rect')
          .attr('class', 'hotzone')
          .attr('x', (d, i) => xScale(i))
          .attr('y', 0)
          .attr('width', barHotZoneWidth)
          .attr('height', height)
          .attr('fill', 'none')
          .attr('pointer-events', 'all');

      barG.append('rect')
          .attr('fill', barBgColor)
          .attr('x', (d, i) => xScale(i) + barGap / 2)
          .attr('y', (d) => yScale(d.doc_count))
          .attr('width', barWidth)
          .attr('height', (d) => height - yScale(d.doc_count));

      barG.append('text')
          .attr('x', (d, i) => xScale(i) + barHotZoneWidth / 2)
          .attr('y', (d) => yScale(d.doc_count) - 5)
          .attr('text-anchor', 'middle')
          .attr('font-size', 12)
          .text((d) => d.doc_count);

      barG.on('mouseenter', function () {
          d3.select(this).select('.hotzone').attr('fill', barHotZoneHighlight);
      }).on('mouseleave', function() {
          d3.select(this).select('.hotzone').attr('fill', 'none');
      });
    };

    function init() {
      var end_time = new Date();
      end_time.setMilliseconds(0);
      var start_time = new Date();
      start_time.setMilliseconds(0);
      start_time.setTime(end_time.getTime() - 24 * 60 * 60 * 1000);
      $scope.model.start_time = start_time;
      $scope.model.end_time = end_time;

      $scope.getData();
    }

    init();
  }

})();
