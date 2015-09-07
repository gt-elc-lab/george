var george = angular.module('george');

george.directive('dropdownMultiselect', DropdownMultiselect);
george.directive('timeSeriesGraph', ['RestService', TimeSeriesGraph]);

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
            $scope.getColor = ColorHashService.colorFromString;
            $scope.getData = RestService.getTermFrequencyData;
    };

    directive.link = function($scope, $element, $attrs) {
        var vis = d3.select('#timeseries-graph');

        var WIDTH = $element.width();
        var HEIGHT = 500;
        var MARGIN = {
            top: 20,
            right: 20,
            bottom: 20,
            left: 20
        };

        var svg = vis.append('svg')
            .attr('width', WIDTH)
            .attr('height', HEIGHT)
            .append('g')
            .attr('transform',
                'translate(' + MARGIN.left + ',' + MARGIN.right + ')');

        var xScale = d3.time.scale()
            .range([MARGIN.left, WIDTH - MARGIN.right]);
        var yScale = d3.scale.linear()
            .range([HEIGHT - MARGIN.top, MARGIN.bottom]);

        var line = d3.svg.line()
            .x(function(d) {
                return xScale(new Date(d.date));
            })
            .y(function(d) {
                return yScale(d.total);
            });

        $scope.$on('timeseries-graph', function(e, args) {
            $scope.colleges = args.colleges.map(function(college) {
                return {
                        name: college,
                        color: '#' + $scope.getColor(college)
                    };
            });

            $scope.getData(args.term, args.colleges).success(function(response) {
                var data = response.data;

                var maxTotal = max(data.map(function(collegeData) {
                    return max(collegeData.data.map(function(d) {return d.total}));
                }));

                var minTotal = min(data.map(function(collegeData) {
                    return min(collegeData.data.map(function(d) {return d.total}));
                }));
                yScale.domain([minTotal, maxTotal]);

                var startDate = min(data.map(function(collegeData) {
                    return min(collegeData.data.map(function(d) {
                        return new Date(d.date);
                    }));
                }));

                var endDate = max(data.map(function(collegeData) {
                    return max(collegeData.data.map(function(d) {
                        return new Date(d.date);
                    }));
                }));
                xScale.domain([new Date(startDate), new Date(endDate)]);

                var yAxis = d3.svg.axis().scale(yScale).orient('left');
                var xAxis = d3.svg.axis().scale(xScale).orient('bottom')
                    .tickFormat(d3.time.format('%m / %d'));

                svg.append('g')
                    .attr('class', 'x axis')
                    .attr('transform',
                        'translate(' + 0 + ',' + (HEIGHT - MARGIN.bottom - MARGIN.top) + ')')
                    .call(xAxis);

                svg.append('g')
                    .attr('class', 'y axis')
                    .attr('transform', 'translate(' + MARGIN.left + ',' + 0 + ')')
                    .call(yAxis)

                data.forEach(function(college) {
                    svg.append("path")
                    .datum(college.data)
                    .attr("class", "line")
                    .attr('fill', 'none')
                    .style('stroke', '#' + $scope.getColor(college.college))
                    .style('stroke-width', '3px')
                    .attr("d", line);

                    var points = svg.selectAll(".point")
                        .data(college.data)
                        .enter().append("svg:circle")
                        .attr("stroke", "black")
                        .attr("fill", '#' + $scope.getColor(college.college))
                        .attr("cx", function(d) {
                            return xScale(new Date(d.date))
                        })
                        .attr("cy", function(d) {
                            return yScale(d.total)
                        })
                        .attr("r", 5);
                });

            }).error(function(error) {
                alert('an error occured');
                console.log(error);
            });
        });

    }

    function min(array) {
        return Math.min.apply(null, array);
    }

    function max(array) {
        return Math.max.apply(null, array);
    }

    return directive;
}