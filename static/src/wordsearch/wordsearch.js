(function(angular, d3) {
var george = angular.module('george');

george.controller('WordsearchController', WordsearchController);

WordsearchController.$inject = ['$http', '$state'];
function WordsearchController($http, $state) {
    var vizTypes = {
        FREQUENCY: 'frequency',
        SCORE: 'score',
        SENTIMENT: 'sentiment'
    };
    var colors = d3.scale.category20();
    $state.params.vizType = $state.params.vizType ? $state.params.vizType
        : vizTypes.FREQUENCY;
    this.vm = {}
    var selected = {};
    this.select = select;
    $http.get('/colleges', {cache: true}).then(collegesSuccess.bind(this));

    function collegesSuccess(response) {
        this.vm.colleges = response.data.colleges.map(function(college, i) {
            return {
                name: college,
                color: colors(i)
            }
        });
    }

    function select(college) {
        if (college.name in selected) {
            delete selected[college];
        } else {
            selected[college.name] = college
        }
        this.vm.selected = Object.keys(selected).map(function(college) {
            return selected[college];
        });
    }
}

})(angular, d3);