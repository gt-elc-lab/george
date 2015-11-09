var george = angular.module('george');

george.directive('dropdownMultiselect', DropdownMultiselect);
george.directive('timeSeriesGraph', ['RestService', TimeSeriesGraph]);
george.directive('trendingGraph', ['RestService', TrendingGraph]);

george.directive('trendingPanel', ['RestService', TrendingPanel]);
george.directive('dailyActivityPanel', ['RestService', DailyActivityPanel]);
george.directive('activityGraph', ['RestService', ActivityGraph]);
george.directive('wordTree', ['RestService', WordTree]);
george.directive('cokeywordsGraph', ['RestService', CokeywordsGraph]);
george.directive('submissionCard', ['RestService', SubmissionCard]);
george.directive('bigqueryGraph', ['$http', BigQueryGraph]);


function DropdownMultiselect() {
    var directive = {
        scope: {
            colleges: '=',
            selectCollege: '&'
        },
        restrict: 'AE',
        templateUrl: '../templates/multiselect.html',
        replace: true
    };

    directive.controller = function($scope) {

    };

    return directive;
}

function TimeSeriesGraph() {
    var directive = {
        scope: {

        },
        restrict: 'AE',
        templateUrl: '../templates/timeseriesgraph.html',
        replace: true
    };

    directive.controller = function($scope, RestService, ColorHashService) {
            /**
                The link function does not accept any aditional parameters so we
                we attach any functionality that we need from the Services to
                the scope.
            */
            $scope.getColor = ColorHashService.colorFromString;
            $scope.getData = RestService.getTermFrequencyData;
    };

    directive.link = function($scope, $element, $attrs) {
        var vis = d3.select('#timeseries-graph');

        var MARGIN = {
            top: 20,
            right: 20,
            bottom: 20,
            left: 20
        };
        var WIDTH = $element.width() - MARGIN.left - MARGIN.right;
        var HEIGHT = 400 - MARGIN.bottom;

        var svg = vis.append('svg')
            .attr('width', WIDTH)
            .attr('height', HEIGHT)
            .append('g')
            .attr('transform',
                'translate(' + MARGIN.left + ',' + 0+ ')');

        var xScale = d3.time.scale()
            .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);
        var yScale = d3.scale.linear()
            .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

        var area = d3.svg.area()
            .x(function(d) {return xScale(new Date(d.date));})
            .y0(HEIGHT - MARGIN.bottom)
            .y1(function(d) {return yScale(d.total);});

        var line = d3.svg.line()
            .x(function(d) {
                return xScale(new Date(d.date));
            })
            .y(function(d) {
                return yScale(d.total);
            })
            .interpolate('monotone');

        $scope.$on('timeseries-graph', function(e, args) {
            $scope.loading = true;
            $scope.colleges = [];
            $scope.getData(args.term, args.colleges).success(function(response) {
                $scope.loading = !$scope.loading;
                $scope.colleges = args.colleges.map(function(college) {
                return {
                        name: college,
                        color: $scope.getColor(college)
                    };
                });
                var data = response.data;

                /**
                    Compute the maximum and minimum values for each individual
                    college.Then use that to compute the overall maxima and minima.
                    This is needed in order to effectively scale the graph for
                    varying input ranges.
                */
                var maxTotal = calculateExtrema(data, d3.max, function(d) {
                    return d.total;
                });

                var minTotal = calculateExtrema(data, d3.min, function(d) {
                    return d.total;
                });

                yScale.domain([minTotal, maxTotal]);

                var startDate = calculateExtrema(data, d3.min, function(d) {
                        return new Date(d.date);
                });

                var endDate = calculateExtrema(data, d3.max, function(d) {
                        return new Date(d.date);
                });

                xScale.domain([new Date(startDate), new Date(endDate)]);

                var yAxis = d3.svg.axis().scale(yScale).orient('left');
                var xAxis = d3.svg.axis().scale(xScale).orient('bottom')
                    .tickFormat(d3.time.format('%m / %d'));

                /**
                    Wipe any data that was previously in the dom. This may need
                    to change in order to enable more gracful transitions.
                */
                svg.selectAll(".line").remove();
                svg.selectAll("circle").remove();
                svg.selectAll(".y.axis").transition().duration(1500).call(yAxis);
                svg.selectAll(".x.axis").transition().duration(1500).call(xAxis);

                svg.append('g')
                    .attr('class', 'x axis')
                    .attr('transform',
                        'translate(' + 0 + ',' + (HEIGHT - MARGIN.bottom) + ')')
                    .call(xAxis);

                svg.append('g')
                    .attr('class', 'y axis')
                    .attr('transform', 'translate(' + MARGIN.left + ',' + 0 + ')')
                    .call(yAxis)

                /**
                    Draw the lines and add the circles for each college.
                */
                data.forEach(function(college) {
                    // TODO(simplyfaisal): add area filling.
                    var color = d3.rgb($scope.getColor(college.college));
                    var path = svg.append("path")
                        .datum(college.data)
                        .attr("class", "line")
                        .attr('class', 'area')
                        .attr('fill', 'none')
                        .style('stroke', color)
                        .style('stroke-width', '3px')
                        .attr("d", line);

                    var points = svg.selectAll(".point")
                        .data(college.data)
                        .enter().append("svg:circle")
                        .attr("stroke", "none")
                        .attr("fill", color)
                        .attr("cx", function(d) {
                            return xScale(new Date(d.date))
                        })
                        .attr("cy", function(d) {
                            return yScale(d.total)
                        })
                        .attr("r", 5);
                });

            }).error(function(error) {
                $scope.loading = false;
                // TODO(simplyfaisal): add a panel that displays on error.
                alert('an error occured');
                console.log(error);
            });
        });

    }

    /**
     * @param data -
     * @param calcFn -
     * @param mapFn -
     */
    function calculateExtrema(data, calcFn, mapFn) {
        return calcFn(data.map(function(innerArray) {
                    return calcFn(innerArray.data.map(mapFn));
                }));
    }

    return directive;
}

function TrendingGraph() {
    var directive = {
        scope: {
            college: '='
        },
        restrict: 'AE',
        templateUrl: '../templates/trendinggraph.html',
        replace: true
    };

    directive.controller = function($scope, RestService) {
        $scope.restService = RestService;
    };

    directive.link = function($scope, $element, $attr) {
        var w = 600;
        var h = 500;

        var svg = d3.select('#force-layout-graph').append('svg')
                    .attr('width', w)
                    .attr('height', h);
        $scope.restService.getTrendingGraph($scope.college).success(function(data) {
                svg.selectAll("*").remove();
                var force = d3.layout.force()
                                .nodes(data.nodes)
                                .links(data.edges)
                                .size([w, h])
                                .linkDistance(25)
                                .start();

                var edges = svg.selectAll('line')
                                .data(data.edges)
                                .enter()
                                .append('line')
                                .style('stroke','#ccc')
                                .style('stroke-width', 1)
                                .attr("x1", function(d) { return d.source.x; })
                                .attr("y1", function(d) { return d.source.y; })
                                .attr("x2", function(d) { return d.target.x; })
                                .attr("y2", function(d) { return d.target.y; });

                var colorScale = d3.scale.category20();
                var nodes = svg.selectAll('circle')
                                .data(data.nodes)
                                .enter()
                                .append('circle')
                                .attr('r', 8)
                                .attr("cx", function(d) { return d.x; })
                                .attr("cy", function(d) { return d.y; })
                                .attr("stroke", function(d) {
                                    if (d.title) {
                                        return 'red';
                                    }
                                    return 'none';
                                })
                                .attr('stroke-width', '4px')
                                .style('cursor', 'pointer')
                                .style('fill', function(d) {
                                    if (d.partition) {
                                        return colorScale(d.partition);
                                    }
                                    return 'black';
                                });

                force.on('tick', function() {
                    edges.attr("x1", function(d) { return d.source.x; })
                            .attr("y1", function(d) { return d.source.y; })
                            .attr("x2", function(d) { return d.target.x; })
                            .attr("y2", function(d) { return d.target.y; });

                    nodes.attr("cx", function(d) { return d.x; })
                        .attr("cy", function(d) { return d.y; });
                });

                force.on('end', function() {
                    var allKeywords = d3.merge(data.nodes.map(function(d) {
                        return d.keywords;
                    }));
                    var fontScale = d3.scale.linear()
                            .domain([1, d3.max(getCounter(allKeywords).values())])
                            .range([5, 40]);

                    var connectedNodes = data.nodes.filter(function(d) {
                        return d.partition;
                    });
                    var partitions = d3.set(connectedNodes.map(function(d) {
                        return d.partition;
                    }));

                    var structs = partitions.values().map(function(partition) {
                            var community = connectedNodes.filter(function(node) {
                                return node.partition == partition;
                            });
                            var keywords = d3.merge(community.map(function(node) {
                                return node.keywords;
                            }));
                            var counter = getCounter(keywords);
                            var orderedKeywords = counter.entries().sort(function(a, b) {
                                return b.value - a.value;
                            });
                            var struct = {
                                keyword: orderedKeywords[0].key,
                                total: orderedKeywords[0].value,
                                x: d3.mean(community.map(function(d) {return d.x})),
                                y: d3.mean(community.map(function(d) {return d.y}))
                            };
                            return struct;
                    });
                    var keywords = svg.selectAll('g')
                        .data(structs)
                        .enter()
                        .append('g')
                        .append('text')
                        .attr('x', function(d) { return d.x;})
                        .attr('y', function(d) { return d.y;})
                        .attr('fill', 'blue')
                        .style('margin', '1px')
                        .attr('font-size', function(d) {return fontScale(d.total) + 'px';})
                        .text(function(d) {return d.keyword;});
                });

                nodes.on('click', function(d) {
                    $scope.selected = d;
                    $scope.$apply();
                });
        })
        .error(function(error) {

        });
    };

    function getCounter(array) {
        var counter = d3.map();
        array.forEach(function(element) {
            if (!counter.has(element)) {
                counter.set(element, 0);
            }
            counter.set(element, counter.get(element) + 1);
        });
        return counter;
    }

    return directive;
}

function TrendingPanel() {
    var directive = {
        scope: {
            college: '='
        },
        restrict: 'AE',
        templateUrl: '../templates/trendingpanel.html',
        replace: true
    };

    directive.controller = function($scope, RestService) {
        $scope.loading;
        $scope.render = function(limit) {
            RestService.getTrendingKeywords($scope.college, limit)
            .then(function(response) {
                $scope.keywords = response.data.data;
                var totals = $scope.keywords.map(function(d) {return d.total});
                $scope.scale = d3.scale.linear()
                     .domain([0, d3.max(totals)])
                     .range([0, 100]);
            });
        };
        $scope.render(1);
    };

    directive.link = function($scope, $element, $attrs) {
        var nav = $element.find('ul');
        nav.children().each(function() {
            $(this).on('click', function() {
                nav.children().each(function() {
                    $(this).removeClass('active');
                });
                $(this).addClass('active');
                $scope.render(+this.dataset.daysago);
            });
        });
    };

    return directive;
}

function DailyActivityPanel() {
    var directive = {
        scope: {
            activity: '=',
            college: '='

        },
        restrict: 'AE',
        templateUrl: '../templates/dailyactivitypanel.html',
        replace: true
    };

    directive.controller = function($scope, RestService) {

    };

    directive.link = function($scope, $element, $attrs) {

    };

    return directive;
}

function ActivityGraph() {
    var directive = {
        scope: {
            college: '='
        },
        restrict: 'AE',
        templateUrl: '../templates/activitygraph.html',
        replace: true
    };

    directive.controller = function($scope, RestService) {
        $scope.RestService = RestService;
    };

    directive.link = function($scope, $element, $attrs) {
        var MARGIN = {top: 20, right: 20, bottom: 30, left: 40};
        var WIDTH = $element.width() - MARGIN.left - MARGIN.right;
        var HEIGHT = 200;
        var color = d3.scale.ordinal().range(['#4caf50', '#2196f3']);
        color.domain(['post', 'comment']);

        var xScale = d3.time.scale()
            .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);

        var yScale = d3.scale.linear()
            .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

        var xAxis = d3.svg.axis()
            .scale(xScale)
            .orient("bottom")
            .tickFormat(d3.time.format("%-I%p"))
            .ticks(d3.time.hour, 2);

        var yAxis = d3.svg.axis()
            .scale(yScale)
            .orient("left")
            .tickFormat(d3.format("d"))
            .ticks(5);

        var svg = d3.select('#activity-graph').append("svg")
            .attr("width", WIDTH + MARGIN.left + MARGIN.right)
            .attr("height", HEIGHT + MARGIN.top + MARGIN.bottom)
            .append("g")
            .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")");

        $scope.RestService.getActivity($scope.college, 1)
        .then(function(response) {
            var dateSet = {};
            var data = response.data.data.map(function(d) {
                d.date = toDateObject(d.date);
                dateSet[d.date.getHours()] = true;
                var y0 = 0;
                d.submissions = color.domain().map(function(type) {
                    return {type: type, y0: y0, y1: y0 += d[type]};
                });
                d.total = d.submissions[d.submissions.length - 1].y1;
                return d;
            });
            var totals = data.map(function(d) { return d.total;});
            var start = d3.time.day.floor(new Date());
            var stop = d3.time.day.ceil(new Date());
            d3.time.hour.range(start, stop, d3.time.hour).forEach(function(d) {
                if (!(d.getHours() in  dateSet)) {
                    data.push({date: d, submissions: [], total: 0});
                }
            });

            data.sort(function(a, b) { return a.date - b.date; });

            var dates = data.map(function(d) { return d.date; });
            xScale.domain([d3.min(dates), d3.max(dates)]);
            yScale.domain([0, d3.max(totals)]);

            svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + HEIGHT + ")")
              .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

            var hour = svg.selectAll(".hour")
                    .data(data)
                    .enter().append("g")
                    .attr("class", "g")
                    .attr("transform", function(d) {
                        return "translate(" + xScale(d.date) + ",0)";
                    });


            hour.selectAll("rect")
                .data(function(d) { return d.submissions; })
                .enter().append("rect")
                .attr("width", 15)
                .attr("y", function(d) { return yScale(d.y1); })
                .attr("height", function(d) { return yScale(d.y0) - yScale(d.y1); })
                .style("fill", function(d) { return color(d.type); });
        });
    };

    function toDateObject(string) {
        var properFormat = string.split(' ').join('T');
        return new Date(Date.parse(properFormat));
    }

    return directive;
}

function WordTree() {
    var directive = {
        scope: {
            college: '='

        },
        restrict: 'AE',
        templateUrl: '../templates/wordtree.html',
        replace: true
    };

    directive.controller = function($scope, RestService) {
        $scope.RestService = RestService;

    };

    directive.link = function($scope, $element, $attrs) {
        var width = $element.width() + 300;
        var height = 900;

        var cluster = d3.layout.cluster()
            .size([height, width / 2])
            .separation(function (a, b) {
              return (a.parent == b.parent ? 1 : 2) / a.depth;
            });

        var diagonal = d3.svg.diagonal()
            .projection(function(d) { return [d.y, d.x]; });

        $scope.render = function() {
            if (!$scope.searchTerm) {
                alert('please enter a term');
                return;
            }
            $scope.RestService.getWordTree($scope.college, $scope.searchTerm)
            .then(function(response) {
                var root = response.data.data;

                var totals = root.children.map(function(d) {
                  return d.total;
                });

                var xScale = d3.scale.linear()
                                .domain([0, d3.max(totals)])
                                .range([0, 1]);

                var svg = d3.select('#word-tree').append('svg')
                    .attr('width', width)
                    .attr('height', height)
                  .append('g')
                    .attr('transform', 'translate(40,0)');


                var nodes = cluster.nodes(root);
                var links = cluster.links(nodes);

                var link = svg.selectAll('.link')
                    .data(links)
                  .enter().append('path')
                    .attr('class', 'link')
                    .attr('d', diagonal)
                    .attr('stroke-width', function(d) {
                      return (xScale(d.target.total)) * 10 + 'px';
                    });

                var node = svg.selectAll('.node')
                    .data(nodes)
                  .enter().append('g')
                    .attr('class', 'node')
                    .attr('transform', function(d) { return 'translate(' + d.y + ',' + d.x + ')'; })

                node.append('circle')
                    .attr('r', 4.5);

                node.append('text')
                    .attr('dx', function(d) { return d.children ? -8 : 8; })
                    .attr('dy', 3)
                    .style('text-anchor', function(d) { return d.children ? 'end' : 'start'; })
                    .text(function(d) { return d.name; });
            });
        };
    };

    return directive;
}

function CokeywordsGraph() {
  var directive = {
    scope: {
      college: '=',
      keyword: '='
    },
    restrict: 'AE',
    replace: true,
    templateUrl: '../../templates/cokeywordsgraph.html'
  };

  directive.controller = function($scope, RestService, $state) {
    $scope.RestService = RestService;
    $scope.$state = $state;
  };

  directive.link = function($scope, $element, $attrs) {
    $scope.RestService.getCoKeywords($scope.college, $scope.keyword)
        .then(function(response) {
        var root = response.data.data;
        root.total = root.children.length;
        var width = $element.width();
        var height = 400;

        var cluster = d3.layout.cluster()
            .size([height, width / 2])
            .separation(function (a, b) {
              return (a.parent == b.parent ? 1 : 2) / a.depth;
            });

        var diagonal = d3.svg.diagonal()
            .projection(function(d) { return [d.y, d.x]; });

        var totals = root.children.map(function(d) {
          return d.total;
        });
        var xScale = d3.scale.linear()
                        .domain([0, d3.max(totals)])
                        .range([0, 1])
                        .clamp(true);

        var svg = d3.select('#cokeywords-tree').append('svg')
            .attr('width', width)
            .attr('height', height)
          .append('g')
            .attr('transform', 'translate(80,0)');


        var nodes = cluster.nodes(root);
        var links = cluster.links(nodes);

        var link = svg.selectAll('.link')
            .data(links)
          .enter().append('path')
            .attr('class', 'link')
            .attr('d', diagonal)
            .attr('stroke-width', function(d) {
                    return xScale(d.target.total) * 15 + 'px';
            })
            .on('mouseover', function(d) {
                    d3.select(this)
                        .transition()
                        .duration(250)
                        .attr('stroke', '#ff9800');
            })
            .on('mouseleave', function(d) {
                    d3.select(this)
                        .transition()
                        .duration(250)
                        .attr('stroke', '#2196f3');
            });

        var node = svg.selectAll('.node')
            .data(nodes)
          .enter().append('g')
            .attr('class', 'node')
            .attr('transform', function(d) { return 'translate(' + d.y + ',' + d.x + ')'; })
            .style('cursor', 'pointer')
            .on('click', function(d) {
              $scope.$state.go('dashboard.keyword', {keyword: d.name});
            });

        node.append('circle')
            .attr('r', function(d) {
              return xScale(d.total) * 12 + 'px';
            });

        node.append('text')
            .attr('dx', function(d) { return d.children ? -15 : 15; })
            .attr('dy', 3)
            .attr('font-size', function(d) {
                return xScale(d.total) * 15 + 'px';
            })
            .style('text-anchor', function(d) { return d.children ? 'end' : 'start'; })
            .text(function(d) { return d.name; });
    });
  };
  return directive;
}

function SubmissionCard() {
     var directive = {
        scope: {
            submission: '='
        },
        restrict: 'AE',
        templateUrl: '../templates/submissioncard.html',
        replace: true
    };

    directive.controller = function($scope) {
        $scope.keywords = $scope.submission ? $scope.submission.keywords.slice(3) : [];
    };

    directive.link = function($scope, $element, $attrs) {
        $scope.numReplies = $scope.submission ? $scope.submission.comments.length : 0;
    };

    return directive;
}

function BigQueryGraph() {
    var directive = {
        scope: {
            
        },
        restrict: 'AE',
        templateUrl: '../templates/bigquerygraph.html',
        replace: true
    };

    directive.controller = function($scope, $http) {
        $scope.selected = {};
        $scope.vm = {};
        $http.get('/bigquery/subreddits')
            .success(function(response){
                $scope.subreddits = response;
            })
            .error(function(error) {
                alert(error);
            });

        $scope.selectSubreddit = function(subreddit) {
            if (subreddit in $scope.selected) {
                delete $scope.selected[subreddit];
            }
            else {
                $scope.selected[subreddit] = true;
            }
            $scope.vm.selected = $scope.getSelected();
            console.log($scope.selected);
        };

        $scope.getSelected = function() {
            return Object.keys($scope.selected);
        };

        $scope.graph = function() {
            var params = {
                subreddits: $scope.getSelected()
            };
            $http.get('/bigquery/score', {params: params}).then(function(response) {
                render(response.data);
            });
        };

        function render(data) {
            data = data.map(transformer);
            var flattened = d3.merge(data.map(function(i) {return i.data}));
            var dateDomain = d3.extent(flattened, function(i) {return i.date});
            var dateMin = dateDomain[0];
            var dateMax = dateDomain[1];

            var avgDomain = d3.extent(flattened, function(i) {return i.average});
            var avgMin = avgDomain[0];
            var avgMax = avgDomain[1];

            var MARGIN = {
                top: 20,
                right: 20,
                bottom: 20,
                left: 20
            };

            var WIDTH = 900 - MARGIN.left - MARGIN.right;
            var HEIGHT = 600 - MARGIN.bottom;

            var svg = d3.select('#bigquerygraph').append('svg')
                .attr('width', WIDTH)
                .attr('height', HEIGHT)
                .append('g')
                .attr('transform',
                    'translate(' + MARGIN.left + ',' + 0+ ')');

            var xScale = d3.time.scale()
                .domain(dateDomain)
                .range([MARGIN.left, WIDTH - MARGIN.right - MARGIN.left]);

            var yScale = d3.scale.linear()
                .domain(avgDomain)
                .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

            var area = d3.svg.area()
                .x(function(d) {return xScale(d.date);})
                .y0(HEIGHT - MARGIN.bottom)
                .y1(function(d) {return yScale(d.average);});

            var line = d3.svg.line()
                .x(function(d) {return xScale(d.date);})
                .y(function(d) {return yScale(d.average);})
                .interpolate('monotone');

            var yAxis = d3.svg.axis().scale(yScale).orient('left');
            var xAxis = d3.svg.axis().scale(xScale).orient('bottom')
                .ticks(d3.time.day)
                .tickFormat(d3.time.format('%b %Y'));

            svg.append('g')
                .attr('class', 'x axis')
                .attr('transform',
                    'translate(' + 0 + ',' + (HEIGHT - MARGIN.bottom) + ')')
                .call(xAxis);

            svg.append('g')
                .attr('class', 'y axis')
                .attr('transform', 'translate(' + MARGIN.left + ',' + 0 + ')')
                .call(yAxis)

            data.forEach(function(i) {
                var path = svg.append("path")
                    .datum(i.data)
                    .attr("class", "line")
                    .attr('class', 'area')
                    .attr('fill', 'none')
                    .style('stroke', 'red')
                    .style('stroke-width', '3px')
                    .attr("d", line);

                var points = svg.selectAll(".point")
                    .data(i.data)
                    .enter().append("svg:circle")
                    .attr("stroke", "none")
                    .attr("fill", 'red')
                    .attr("cx", function(d) {
                        return xScale(d.date)
                    })
                    .attr("cy", function(d) {
                        return yScale(d.average)
                    })
                    .attr("r", 5);
            });
        };

        function transformer(dataObj) {
            var data = dataObj.data.map(function(i) {
                return {
                    date: new Date(+i.year, +i.month, 1),
                    average: i.average_score,
                    total: i.total_activity
                };
            });
            data.sort(function(a, b) { return a.date - b.date});
            return {
                subreddit: dataObj.subreddit,
                data: data
            };
        }
    };

    directive.link = function($scope, element, $attrs, $http) {
        
    };


    return directive;
}
