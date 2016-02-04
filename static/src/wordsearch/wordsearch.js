(function(angular, d3) {
var george = angular.module('george');

george.controller('WordsearchController', WordsearchController);
george.service('SearchNotifier', SearchNotifier)

WordsearchController.$inject = ['$http', '$state', '$q', 'TooltipFactory'];
function WordsearchController($http, $state, $q, TooltipFactory) {
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
        var visualize = this.viz == vizTypes.FREQUENCY ||
            this.viz == vizTypes.SCORE ? simpleSearchVisualization : sentimentVisualization
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
                    data:  response.data.map(function(d) {
                        d.date = new Date(d._id);
                        d.college = college;
                        return d;
                    })
                }
            });

            visualize(data)
        });
    }

    function simpleSearchVisualization(data) {
        var parent = $('#search-viz');
        var WIDTH = parent.width();
        var HEIGHT = window.innerHeight - parent.offset().top - 100;
        var MARGIN = { top: 20, right: 40, bottom: 20, left: 20};
        var svg = d3.select('#search-viz').append('svg')
                .attr('width', WIDTH)
                .attr('height', HEIGHT)
                .append('g')
                .attr('transform', 'translate(' + MARGIN.left + ',' + 0+ ')');

        var flattened = d3.merge(data.map(function(d) { return d.data}));
        var dateExtent = d3.extent(flattened, function(d) {return d.date;});
        var dateMin = dateExtent[0];
        var dateMax = dateExtent[1];
        var range = d3.time.day.range(dateMin, dateMax).map(function(i) { return {total: 0,  date: i};});
        data =  data.map(function(d) {
            var map = d3.set(d.data.map((function(i) {return i.date.toDateString();})))
            var fillerDates = range.filter(function(i) { return !map.has(i.date.toDateString())});
            d.data = d.data.concat(fillerDates);
            d.data.sort(function(a, b) { return a.date - b.date;});
            return d;
        });


        var x = d3.time.scale()
                    .domain(dateExtent)
                    .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);

        var y = d3.scale.linear()
                    .domain([0, d3.max(flattened, function(d){return d.total;})])
                    .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

        var line = d3.svg.line()
                        .x(function(d) {return x(d.date);})
                        .y(function(d) {return y(d.total);});

        var xAxis = d3.svg.axis().scale(x).orient('bottom')
                        .tickFormat(d3.time.format('%a %e'));

        var yAxis = d3.svg.axis().scale(y).orient('left')
                        .tickFormat(d3.format('d'));

        svg.append('g')
            .attr('class', 'x axis')
            .attr('transform',
            'translate(' + 0 + ',' + (HEIGHT - MARGIN.bottom) + ')')
            .call(xAxis);

        svg.append('g')
            .attr('class', 'y axis grid')
            .attr('transform', 'translate(' + MARGIN.left + ',' + 0 + ')')
            .call(yAxis)
            .append("text")      // text label for the x axis
            .attr("x", 15 )
            .attr("y", 35 )
            .style("text-anchor", "start")
            .attr("transform", "rotate(90)")
            .text("average score / post");

        var tooltip = TooltipFactory.getToolTip('search-tooltip.html');
        svg.call(tooltip);
        data.forEach(function(i) {
            var path = svg.append("path").datum(i.data).attr("class", "line");
            path.attr('fill', 'none')
                        .style('stroke', i.college.color)
                        .style('stroke-width', '3px')
                        .attr("d", line);

            var points = svg.selectAll(".point")
                            .data(i.data)
                            .enter().append("svg:circle")
                            .attr('class', 'circle')
                            .attr("stroke", "none")
                            .attr("fill", i.college.color)
                            .attr("cx", function(d) {
                              return x(d.date);
                            })
                            .attr("cy", function(d) {
                              return y(d.total);
                            })
                            .attr("r", 5);

            points.on('mouseover', circleMouseOverHandler);
            points.on('mouseout', circleMouseOutHandler);

            function circleMouseOverHandler(d) {
                tooltip.show(d);
                d3.select(this).attr({
                    r: 8
                });
            }

            function circleMouseOutHandler(d) {
                tooltip.hide(d);
                d3.select(this).attr({
                    r: 5
                });
            }
        });

    }

    function sentimentVisualization(data) {

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