'use strict';
var george = angular.module('george');

george.controller('HomeController', HomeController);
george.controller('WordSearchController', WordSearchController);
george.controller('TrendingController', TrendingController);

function HomeController(data) {
    this.colleges = data.colleges;
}

function WordSearchController($scope, RestService, data) {
    this.colleges = data.colleges;
    this.selected = {};

    this.selectCollege = function(college) {
        if (college in this.selected) {
            delete this.selected[college];
        }
        else {
            this.selected[college] = true;
        }
    };

    this.getSelectedColleges = function() {
        return Object.keys(this.selected);
    };

    this.validate = function() {
        var selectedColleges = this.getSelectedColleges();
        if (selectedColleges && this.term) {
            $scope.$broadcast('timeseries-graph',
                {term: this.term, colleges: selectedColleges})
        }
        else {
            alert('invalid input');
        }
    }
}

function TrendingController(RestService, data) {
    this.colleges = data.colleges;
    this.selectedCollege = this.colleges[0];

    this.drawGraph = function() {

    }
}