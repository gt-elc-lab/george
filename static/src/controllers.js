'use strict';
var george = angular.module('george');

george.controller('HomeController', HomeController);
george.controller('WordSearchViewController', WordSearchViewController);
george.controller('TrendingController', TrendingController);
george.controller('SummaryController', SummaryController);
george.controller('DashboardController', DashboardController);
george.controller('KeywordController', KeywordController);


function HomeController(data) {
    this.colleges = data.colleges;
}

function SummaryController($stateParams, activity) {
    this.vm = {}
    this.vm.college = $stateParams.college;
    this.vm.activity = activity;
}

function DashboardController($scope, $stateParams) {
    this.vm = {}
    this.vm.college = $stateParams.college;

    $scope.$on('$stateChangeSuccess',
        function(event, toState, toParams, fromState, fromParams) {
        if (toParams.keyword) {
            this.vm.keyword = toParams.keyword;
        }
        if (toState.name == 'dashboard.summary') {
            this.vm.keyword = null;
        }
    }.bind(this));
}

function WordSearchViewController($scope, $stateParams) {
    this.college = $stateParams.college;
}

function TrendingController($scope, RestService, data) {
    this.colleges = data.colleges;
    this.selectedCollege = this.colleges[0];

    this.drawGraph = function() {
        console.log(this.selectedCollege);
        $scope.$broadcast('trending-graph', {college: this.selectedCollege});
    };
}

function KeywordController($stateParams) {
    this.vm = {};
    this.vm.college = $stateParams.college;
    this.vm.keyword = $stateParams.keyword;
}