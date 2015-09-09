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
                        color: '#' + $scope.getColor(college)
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
                    var color = '#' + $scope.getColor(college.college);
                    var path = svg.append("path")
                        .datum(college.data)
                        .attr("class", "line")
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