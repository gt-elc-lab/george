(function(angular, d3) {
var george = angular.module('george');

george.controller('WordsearchController', WordsearchController);

WordsearchController.$inject = ['$http', '$state', '$q', 'TooltipFactory'];
function WordsearchController($http, $state, $q, TooltipFactory) {
    var vizTypes = {
        FREQUENCY: 'frequency',
        SCORE: 'score',
        SENTIMENT: 'sentiment'
    };
    this.vm = {}
    this.viz = null;
    this.loading = false;
    this.select = select;
    this.selectVizType = selectVizType;
    this.search = search.bind(this);
    init.bind(this)();

    var colors = d3.scale.category20();
    var selected = {};
    var pubsub = new PubSub()

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
        var parent = $('#search-viz');
        parent.empty();
        this.loading = true;
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
            var label = null;
            if (this.viz == vizTypes.FREQUENCY) {
                label = '# of posts';
            }
            if (this.viz == vizTypes.SCORE) {
                label = 'average score / post';
            }
            this.loading = false;
            visualize(data, label);
        }.bind(this));
    }

    function fillDates(data, defaultFn) {
        var flattened = d3.merge(data.map(function(d) { return d.data}));
        var dateExtent = d3.extent(flattened, function(d) {return d.date;});
        var dateMin = dateExtent[0];
        var dateMax = dateExtent[1];
        var range = d3.time.day.range(dateMin, dateMax).map(defaultFn);
        return data.map(function(d) {
            var map = d3.set(d.data.map((function(i) {return i.date.toDateString();})))
            var fillerDates = range.filter(function(i) { return !map.has(i.date.toDateString())});
            d.data = d.data.concat(fillerDates);
            d.data.sort(function(a, b) { return a.date - b.date;});
            return d;
        });
    }

    function simpleSearchVisualization(data, yLabel) {
        var parent = $('#search-viz');
        var WIDTH = parent.width();
        var HEIGHT = window.innerHeight - parent.offset().top - 50;
        var MARGIN = { top: 20, right: 40, bottom: 20, left: 20};
        var svg = d3.select('#search-viz').append('svg')
                .attr('width', WIDTH)
                .attr('height', HEIGHT)
                .append('g')
                .attr('transform', 'translate(' + MARGIN.left + ',' + 0+ ')');
        var flattened = d3.merge(data.map(function(d) { return d.data}));
        data = fillDates(data, function(i) {return {total: 0,  date: i}})
        var dateExtent = d3.extent(flattened, function(d) {return d.date;});
        var x = d3.time.scale()
                    .domain(dateExtent)
                    .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);

        var y = d3.scale.linear()
                    .domain([0, d3.max(flattened, function(d){return d.total;})])
                    .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

        var line = d3.svg.line()
                        .x(function(d) {return x(d.date);})
                        .y(function(d) {return y(d.total);})

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
            .text(yLabel);

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
        var parent = $('#search-viz');
        var margin = {top: 20, right: 20, bottom: 30, left: 50},
            width = parent.width() - margin.left - margin.right,
            height = 160 - margin.top - margin.bottom;

        var x = d3.time.scale()
                .range([0, width]);

        var y = d3.scale.linear()
                .range([height, 0]);

        var categories = d3.set(['positive', 'negative', 'neutral']);
        var color = d3.scale.category20();
        color.domain(d3.keys(data[0].data[0]).filter(categories.has, categories));
        var formatPercent = d3.format(".0%");

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(d3.time.format('%a %e'));

        var yAxis = d3.svg.axis()
                    .scale(y)
                    .orient("left")
                    .ticks(2)
                    .tickFormat(formatPercent);


        var area = d3.svg.area()
            .x(function(d) { return x(d.date); })
            .y0(function(d) { return y(d.y0); })
            .y1(function(d) { return y(d.y0 + d.y); });

        var stack = d3.layout.stack()
            .values(function(d) { return d.values; });


        var flattened = d3.merge(data.map(function(d) { return d.data}));
        x.domain(d3.extent(data[0].data, function(d) { return d.date; }));

        data = fillDates(data, function(i) {
            return {positive: 0, neutral: 0, negative: 0,  date: i}});

        data.forEach(function(college) {

            var svg = d3.select("#search-viz").append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            svg.append("text")
                .style('fill', college.college.color)
                .text(college.college.name);

            var sentiments = stack(color.domain().map(function(name) {
                return {
                  name: name,
                  values: college.data.map(function(d) {
                    return {date: d.date, y: d[name]};
                  })
                };
              }));


            var sentiment = svg.selectAll(".browser")
                            .data(sentiments)
                            .enter().append("g")
                            .attr("class", "browser");
            var line = svg.append("line")
                        .attr("x1", 5)
                        .attr("y1", 0)
                        .attr("x2", 5)
                        .attr("y2", height)
                        .attr("stroke-width", 2)
                        .attr("stroke", college.college.color);

            pubsub.subscribe(function() {
                    var x = d3.mouse(this)[0];
                    line.attr('x1', x)
                        .attr('y1', 0)
                        .attr('x2', x)
                        .attr('y2', height)
                        .style('display', 'visible')
              });

              svg.on('mousemove', function() {
                pubsub.publish(this);
              });
            sentiment.append("path")
              .attr("class", "area")
              .attr("d", function(d) { return area(d.values); })
              .style("fill", function(d) {
                var lookup = {
                    positive: '#4caf50',
                    neutral: '#FFDC00',
                    'negative': '#e51c23'
                }
                return lookup[d.name];
                });

            sentiment.append("text")
              .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
              .attr("transform", function(d) { return "translate(" + x(d.value.date) + "," + y(d.value.y0 + d.value.y / 2) + 10 + ")"; })
              .attr("x", -60)
              .attr("dy", ".35em")
              .text(function(d) { return d.name; });

            svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + height + ")")
              .call(xAxis);

            svg.append("g")
              .attr("class", "y axis")
              .call(yAxis);
        });
    }
}

function PubSub() {

    var callbacks = [];

    this.publish = function(ctx) {
        callbacks.forEach(function(cb) {
            cb.call(ctx || this);
        });
    };

    this.subscribe = function(cb) {
        callbacks.push(cb);
    };
}

})(angular, d3);