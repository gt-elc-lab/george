'use strict'
var george = angular.module('george');

george.controller('HomeController', HomeController);

function HomeController(data) {
    this.colleges = data.colleges;
}