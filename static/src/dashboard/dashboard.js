(function(angular, d3) {

var george = angular.module('george');

george.directive('topicGraph', TopicGraph);
george.directive('keywordFrequencyGraph', KeywordFrequencyGraph);
george.directive('sentimentTable', SentimentTable);

TopicGraph.$inject = ['$http', '$stateParams'];
function TopicGraph($http, $stateParams) {
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
                    .size([w, h])
                    .start();

                var frequencyScale = d3.scale.linear()
                    .domain(d3.extent(data.nodes, function(d) {return d.frequency}))
                    .range([2, 10]);

                var edges = svg.selectAll('line')
                    .data(data.links)
                    .enter()
                    .append('line')
                    .style('stroke', '#ccc')
                    .style('stroke-width', 1)
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

                var nodes = svg.selectAll('g')
                    .data(data.nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node')
                    .call(force.drag)

                var circle = nodes.append('circle')
                    .attr('r', function(d) {
                        return frequencyScale(d.frequency);
                    })
                    .attr("cx", function(d) {
                        return d.x;
                    })
                    .attr("cy", function(d) {
                        return d.y;
                    })
                    .attr('stroke-width', '4px');

                var text = nodes.append('text')
                    .attr("dx", 12)
                    .attr("dy", ".35em")
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

KeywordFrequencyGraph.$inject = ['$http'];
function KeywordFrequencyGraph() {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'src/dashboard/keyword-frequency-graph.html',
        controller: function($scope, $stateParams) {

        },
        link: function($scope, $element, $attrs) {

        }
    };
}

SentimentTable.$inject = ['$http'];
function SentimentTable($http) {
    return {
        restrict: 'E',
        scope: {},
        templateUrl: 'src/dashboard/sentiment-table.html',
        controller: function($scope, $stateParams) {

        },
        link: function($scope, $element, $attrs) {

        }
    };
}

})(angular, d3)