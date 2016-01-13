(function(angular, d3) {

var george = angular.module('george');

george.directive('topicGraph', TopicGraph);
george.directive('keywordFrequencyGraph', KeywordFrequencyGraph);
george.directive('sentimentTable', SentimentTable);

george.service('TopicNotifier', TopicNotifier);

TopicGraph.$inject = ['$http', '$stateParams', 'TopicNotifier'];
function TopicGraph($http, $stateParams, TopicNotifier) {
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
                    .linkDistance(60)
                    .charge(-80)
                    .size([w, h])
                    .start();

                var frequencyScale = d3.scale.linear()
                    .domain(d3.extent(data.nodes, function(d) {return Math.sqrt(d.frequency)}))
                    .range([5, 25]);

                var edgeWeightScale = d3.scale.linear()
                    .domain(d3.extent(data.links, function(d) {return d.weight}))
                    .range([3, 15]);

                function radius(n) {
                    return frequencyScale(Math.sqrt(n));
                }

                var edges = svg.selectAll('line')
                    .data(data.links)
                    .enter()
                    .append('line')
                    .style('stroke', '#ccc')
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


                circle.on('mouseover', handleMouseOver);
                circle.on('mouseout', handleMouseOut);
                circle.on('click', handleClick);

                function handleMouseOver(d, i) {
                    // Use D3 to select element, change color and size
                    d3.select(this).attr({
                      r:  radius(d.frequency) * 1.2
                    });
                }

                function handleMouseOut(d, i) {
                    d3.select(this).attr({
                        r: radius(d.frequency)
                    });
                }

                function handleClick(d, i) {
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
            TopicNotifier.subscribe(function(data) {
                console.log('frequency recieved data')
            });
        }
    };
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
            TopicNotifier.subscribe(function(data) {
                console.log('sentiment recieved data')
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

})(angular, d3)