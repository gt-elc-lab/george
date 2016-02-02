(function(angular, d3) {
var george = angular.module('george');

george.controller('WordsearchController', WordsearchController);

WordsearchController.$inject = ['$http'];
function WordsearchController($http) {
    this.vm = {}
    var selected = {};
    this.select = select;
    $http.get('/colleges', {cache: true}).then(collegesSuccess.bind(this));

    function collegesSuccess(response) {
        this.vm.colleges = response.data.colleges;
    }

    function select(college) {
        if (college in selected) {
            delete selected[college];
        } else {
            selected[college] = true
        }
        this.vm.selected = Object.keys(selected);
    }
}

})(angular, d3);