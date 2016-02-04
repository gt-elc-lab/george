(function(angular, d3) {
var george = angular.module('george');

george.controller('WordsearchController', WordsearchController);
george.service('SearchNotifier', SearchNotifier)

WordsearchController.$inject = ['$http', '$state', '$q', 'SearchNotifier'];
function WordsearchController($http, $state, $q, SearchNotifier) {
    var vizTypes = {
        FREQUENCY: 'frequency',
        SCORE: 'score',
        SENTIMENT: 'sentiment'
    };
    this.vm = {}
    this.viz = null;
    this.select = select;
    this.selectVizType = selectVizType;
    this.search = search.bind(this);
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

    function search() {
        var colleges = Object.keys(selected);
        var query = this.query;
        var baseUrl = {
            frequency: 'wordsearch/',
            score: 'scoresearch/',
            sentiment: 'sentimentsearch/'
        };
        var url = baseUrl[this.viz];
        var promises = colleges.map(function(college) {
            var options = {
                params: {
                    term: query
                }
            };
            return $http.get(url + college, options);
        });

        $q.all(promises).then(function(responses) {
            var data = responses.map(function(response, i) {
                // Promises are returned in the same order so its ok to do this.
                var college = colleges[i];
                return {
                    college: selected[college],
                    data:  response.data
                }
            });
            SearchNotifier.notify(data);
        });
    }
}

function SearchNotifier() {

    var callbacks = [];

    this.notify = function(data) {
        callbacks.forEach(function(cb) {
            cb(data);
        });
    };

    this.subscribe = function(cb) {
        callbacks.push(cb);
    };
}

})(angular, d3);