var george = angular.module('george', ['ui.router']);

george.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');
    $stateProvider
        .state('home', {
            url:'/home',
            templateUrl: '../views/home.html'
        })
});