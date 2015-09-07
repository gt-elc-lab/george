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
    };

    directive.link = function($scope, $element, $attrs) {
        $scope.$on('timeseries-graph', function(e, args) {
            console.log(args);
            $scope.colleges = args.colleges.map(function(college) {
                return {
                        name: college,
                        style:  {
                            'background-color': $scope.getColor(college)
                        }
                    };
            });
        });
    }
    return directive;
}