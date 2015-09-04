'use strict'
var george = angular.module('george');

george.controller('HomeController', HomeController);
george.controller('WordSearchController', WordSearchController);
george.controller('TrendingController', TrendingController);

function HomeController(data) {
    this.colleges = data.colleges;
}

TrendingController.$inject = ['RestService'];
function WordSearchController(RestService, data) {
    this.colleges = data.colleges;
}

function TrendingController(data) {
    this.colleges = data.colleges;
}