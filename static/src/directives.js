var george = angular.module('george');

george.directive('dropdownMultiselect', DropdownMultiselect);

function DropdownMultiselect() {
    var directive = {
        scope: {
            colleges: '='
        },
        restrict: 'AE',
        templateUrl: '../templates/multiselect.html'
    }

}