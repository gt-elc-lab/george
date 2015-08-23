var george = angular.module('george');

george.controller('HomeController', HomeController);

HomeController.$inject = ['FlaskService'];
function HomeController(FlaskService) {

}