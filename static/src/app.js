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
            data: function colleges(RestService) {
                return RestService.getCollegeList().then(function(response) {
                    return response.data;
                });
            }
        }
    })
    .state('dashboard', {
        url: '/dashboard/:college',
        templateUrl: '../views/dashboard.html',
        controller: 'DashboardController',
        controllerAs: 'dashboard',
        resolve: {
            activity: function(RestService, $stateParams) {
                return RestService.getTodaysActivitySummary($stateParams.college)
                    .then(function(response) {
                        return response.data.activity;
                    });
            }
        }
    })
});
