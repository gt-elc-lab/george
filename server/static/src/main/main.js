(function(angular) {

var george = angular.module('george');

george.controller('ShellController', ShellController);


function ShellController($state) {
    this.vm = {};
    this.vm.college = $state.params.college;
}

})(angular);