(function(angular, d3) {

var george = angular.module('george');

george.directive('topicGraph', TopicGraph);
george.directive('keywordFrequencyGraph', KeywordFrequencyGraph);
george.directive('sentimentTable', SentimentTable);

george.service('TopicNotifier', TopicNotifier);
george.factory('TooltipFactory', TooltipFactory);

TopicGraph.$inject = ['$http', '$stateParams', 'TopicNotifier', 'TooltipFactory'];
function TopicGraph($http, $stateParams, TopicNotifier, TooltipFactory) {
    return {
        restrict: 'E',
        scope: {},
        templateUrl:'src/dashboard/topic-graph-template.html',
        controller: function($scope, $stateParams) {

        },
        link: function($scope, $element, $attrs) {
            var $parent = $element.parent();
            var w = $parent.width();
            var h = 500;

            var svg = d3.select('#topic-graph').append('svg')
                .attr('width', w)
                .attr('height', h);

           $http.get('/topicgraph/' + $stateParams.college).then(function(response) {
                render(response.data);
            }, function(error) {
                alert('error');
            });

           function render(data) {
                var force = d3.layout.force()
                    .nodes(data.nodes)
                    .links(data.links)
                    .linkDistance(80)
                    .charge(-80)
                    .size([w, h])
                    .start();

                var frequencyScale = d3.scale.linear()
                    .domain(d3.extent(data.nodes, function(d) {return Math.sqrt(d.frequency)}))
                    .range([10, 35]);

                var edgeWeightScale = d3.scale.linear()
                    .domain(d3.extent(data.links, function(d) {return d.weight}))
                    .range([5, 20]);

                function radius(n) {
                    return frequencyScale(Math.sqrt(n));
                }

                var bubbleTip = TooltipFactory.getToolTip('bubble-tooltip.html');
                var edgeTip = TooltipFactory.getToolTip('edge-tooltip.html');
                svg.call(bubbleTip);
                svg.call(edgeTip);

                var edges = svg.selectAll('line')
                    .data(data.links)
                    .enter()
                    .append('line')
                    .style('stroke', '#ff9800')
                    .style('stroke-width', function(d) {
                        return edgeWeightScale(d.weight) + 'px';
                    })
                    .attr("x1", function(d) {
                        return d.source.x;
                    })
                    .attr("y1", function(d) {
                        return d.source.y;
                    })
                    .attr("x2", function(d) {
                        return d.target.x;
                    })
                    .attr("y2", function(d) {
                        return d.target.y;
                    });

                edges.on('mouseover', edgesMouseOverHandler);
                edges.on('mouseout', edgesMouseOutHandler);

                function edgesMouseOverHandler(d, i) {
                    edgeTip.show(d);
                    d3.select(this).style({
                      'stroke-width':  edgeWeightScale(d.weight) * 2
                    });
                }

                function edgesMouseOutHandler(d, i) {
                    edgeTip.hide(d);
                    d3.select(this).style({
                      'stroke-width':  edgeWeightScale(d.weight)
                    });
                }

                var nodes = svg.selectAll('g')
                    .data(data.nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node')
                    .call(force.drag)


                var circle = nodes.append('circle')
                    .attr('r', function(d) {
                        return radius(d.frequency);
                    })
                    .attr("cx", function(d) {
                        return d.x;
                    })
                    .attr("cy", function(d) {
                        return d.y;
                    })
                    .attr('stroke-width', '4px');


                circle.on('mouseover', bubbleMouseOverHandler);
                circle.on('mouseout', bubbleMouseOutHandler);
                circle.on('click', bubbleClickHandler);

                function bubbleMouseOverHandler(d, i) {
                    // Use D3 to select element, change color and size
                    bubbleTip.show(d);
                    d3.select(this).attr({
                      r:  radius(d.frequency) * 1.2
                    });
                }

                function bubbleMouseOutHandler(d, i) {
                    bubbleTip.hide(d);
                    d3.select(this).attr({
                        r: radius(d.frequency)
                    });
                }

                function bubbleClickHandler(d, i) {
                    d3.selectAll('.selected').classed('selected', false);
                    d3.select(this).classed('selected', true);
                    TopicNotifier.notify(d);
                }

                var text = nodes.append('text')
                    .attr("dx", 12)
                    .attr("dy", '2em')
                    .attr('id', function(d, i) {
                        return "t-" + d.id + '-' + i;
                    })
                    .text(function(d) { return d.id });

                force.on('tick', function() {
                    edges.attr("x1", function(d) {
                        return d.source.x;
                    })
                    .attr("y1", function(d) {
                        return d.source.y;
                    })
                    .attr("x2", function(d) {
                        return d.target.x;
                    })
                    .attr("y2", function(d) {
                        return d.target.y;
                    });

                    circle.attr("cx", function(d) {
                        return d.x;
                    })
                    .attr("cy", function(d) {
                        return d.y;
                    });

                    text.attr("x", function(d) { return d.x; })
                        .attr("y", function(d) { return d.y; })
                        .text(function(d) { return d.id });

                });
           };
        }

    };
};

KeywordFrequencyGraph.$inject = ['$http', '$stateParams', 'TopicNotifier'];
function KeywordFrequencyGraph($http, $stateParams, TopicNotifier) {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'src/dashboard/keyword-frequency-graph.html',
        controller: function($scope) {

        },
        link: function($scope, $element, $attrs) {
            var MARGIN = {
                top: 20,
                right: 40,
                bottom: 20,
                left: 20
            };
            var container = $element.children();

            var WIDTH = container.width() - MARGIN.left - MARGIN.right;
            var HEIGHT = 375 - MARGIN.bottom;
            var svg = d3.select('#keyword-frequency-graph').append('svg')
                .attr('width', WIDTH)
                .attr('height', HEIGHT)
                .append('g')
                .attr('transform',
                'translate(' + MARGIN.left + ',' + 0+ ')');

            TopicNotifier.subscribe(function(payload) {
                function render(data) {
                    var today = new Date();
                    var weekAgo = moment().subtract(7, 'days').toDate();
                    var map = d3.set(data.map(function(i) {return i.date.toDateString()}));
                    var range = d3.time.day.range(weekAgo, today).map(function(i) { return {total: 0,  date: i, id: payload.id};});
                    var fillerDates = range.filter(function(i) { return !map.has(i.date.toDateString())});
                    data = data.concat(fillerDates);
                    data.sort(function(a, b) { return a.date - b.date;});

                    var xScale = d3.time.scale()
                        .domain(d3.extent(data, function(d) {return d.date;}))
                        .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);

                    var yScale = d3.scale.linear()
                        .domain(d3.extent(data, function(d){return d.total;}))
                        .range([HEIGHT - MARGIN.top, MARGIN.bottom]);


                    var line = d3.svg.line()
                        .interpolate("monotone")
                        .x(function(d) {return xScale(d.date);})
                        .y(function(d) {return yScale(d.total);});

                    // Create x and y axis
                    var xAxis = d3.svg.axis().scale(xScale).orient('bottom')
                        .ticks(7)
                        .tickFormat(d3.time.format('%m/%e'));

                    var yAxis = d3.svg.axis().scale(yScale).orient('left')
                        .tickFormat(d3.format('d'));

                    // remove any previously drawn axis
                    svg.selectAll(".y.axis").remove();
                    svg.selectAll(".x.axis").remove();

                    var axisExists = svg.selectAll(".y.axis")[0].length < 1;
                    if (axisExists) {
                        // append the axis
                        svg.append('g')
                            .attr('class', 'x axis')
                            .attr('transform',
                            'translate(' + 0 + ',' + (HEIGHT - MARGIN.bottom) + ')')
                            .call(xAxis);

                        svg.append('g')
                            .attr('class', 'y axis')
                            .attr('transform', 'translate(' + MARGIN.left + ',' + 0 + ')')
                            .call(yAxis);
                    } else {
                        svg.selectAll(".y.axis")
                            .transition().duration(1500).call(yAxis);
                        svg.selectAll(".x.axis")
                            .transition().duration(1500).call(xAxis);
                    }

                    // remove any previously drawn lines
                    svg.selectAll(".line").remove();
                    //enter and append this lines
                    var path = svg.append("path").datum(data).attr("class", "line");

                    path.transition().duration(1500)
                        .attr('fill', 'none')
                        .style('stroke', 'red')
                        .style('stroke-width', '3px')
                        .attr("d", line);

                     // remove points
                    svg.selectAll(".circle").remove();
                    var points = svg.selectAll(".point")
                            .data(data)
                            .enter().append("svg:circle")
                            .attr('class', 'circle')
                            .attr("stroke", "none")
                            .attr("fill", 'red')
                            .attr("cx", function(d) {
                              return xScale(d.date);
                            })
                            .attr("cy", function(d) {
                              return yScale(d.total);
                            })
                            .attr("r", 5);
                }

                var options = {
                    params: {
                        college: $stateParams.college,
                    },
                    cache: true
                };

                $http.get('/keyword/activity/' + payload.id, options).then(
                    function(response) {
                        render(response.data.map(function(i) {
                            return {
                                total: i.total,
                                date: new Date(i._id),
                                id: payload.id
                            };
                    }));
                });
            });
        }
    }
}

SentimentTable.$inject = ['$http', '$stateParams', 'TopicNotifier'];
function SentimentTable($http, $stateParams, TopicNotifier) {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'src/dashboard/sentiment-table.html',
        controller: function($scope) {

        },
        link: function($scope, $element, $attrs) {
            var MARGIN = {
                top: 20,
                right: 40,
                bottom: 20,
                left: 20
            };
            var container = $element.children();

            var WIDTH = container.width() - MARGIN.left - MARGIN.right;
            var HEIGHT = 125 - MARGIN.bottom;
            var svg = d3.select('#sentiment-table').append('svg')
                .attr('width', WIDTH)
                .attr('height', HEIGHT)
                .append('g')
                .attr('transform',
                'translate(' + MARGIN.left + ',' + 0+ ')');

            TopicNotifier.subscribe(function(payload) {
                var options = {
                    params: {
                        college: $stateParams.college
                    },
                    cache: true
                };

                function render(data) {
                    data = d3.entries(data).filter(function(i) {
                            return i.value;
                    });
                    var order = {pos: 1, neu: 2, neg: 3};
                    data.sort(function(a, b) { return order[a.key] - order[b.key]});
                    var scale = d3.scale.linear()
                        .domain([0,1])
                        .range([0, WIDTH]);

                    var colors = {pos: 'green', neu: 'yellow', neg: 'red'};
                    //Draw the Rectangle
                    var rectangle = svg.selectAll('.rect')
                        .data(data)
                        .enter()
                        .append('rect')
                        .attr("x", function(i) {
                            var widths =  data.filter(function(d) {
                                return order[d.key] < order[i.key];
                            })
                            .map(function(x) {
                                return scale(x.value);
                            });
                            return d3.sum(widths || [0]);
                        })
                        .attr("y", 10)
                        .attr("width", function(i) {
                            return scale(i.value);
                        })
                        .attr("height", HEIGHT)
                        .style('fill', function(i) {
                            return colors[i.key];
                        })
                        .text(function(i) {
                            return i.key;
                        });
                }

                $http.get('/sentiment/' + payload.id, options).then(
                    function(response) {
                        render(response.data);
                });
            });
        }
    };
}

function TopicNotifier() {

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

TooltipFactory.$inject = ['$templateCache', '$interpolate'];
function TooltipFactory($templateCache, $interpolate) {
    var factory = {};

    factory.getToolTip = function(templateId) {
        return d3.tip().attr('class', 'd3-tip')
            .html(function(d) {
                return $interpolate($templateCache.get(templateId))(d);
            });
    };
    return factory;
}

})(angular, d3)