'use strict'
var george = angular.module('george', ['ui.router']);

george.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');
    $stateProvider
        .state('home', {
            url:'/home',
            templateUrl: '../views/home.html',
            controller: 'HomeController',
            controllerAs: 'home',
            resolve: {
                data: function(RestService) {
                    return RestService.getCollegeList().then(function(response) {
                       return response.data;
                    });
                }
            }
        });
});