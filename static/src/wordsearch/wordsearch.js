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
    this.vm = {}
    this.viz = null;
    this.select = select;
    this.selectVizType = selectVizType;
    init.bind(this)();

    var colors = d3.scale.category20();
    var selected = {};

    $http.get('/colleges', {cache: true}).then(collegesSuccess.bind(this));

    function collegesSuccess(response) {
        this.vm.colleges = response.data.colleges.map(function(college, i) {
            return {
                name: college,
                color: colors(i)
            }
        });
    }

    function init() {
        this.selectVizType(vizTypes.SCORE);
    }

    function select(college) {
        if (college.name in selected) {
            delete selected[college.name];
        } else {
            selected[college.name] = college
        }
        this.vm.selected = Object.keys(selected).map(function(college) {
            return selected[college];
        });
    }

    function selectVizType(viz) {
        this.viz = viz;
        $('.btn').removeClass('btn-primary');
        $('#wordsearch-' + viz).addClass('btn-primary');
    }
}

})(angular, d3);