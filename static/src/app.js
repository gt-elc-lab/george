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
            data: colleges
        }
    })
    .state('app', {
        url: '/app',
        templateUrl: '../views/app.html'
    })
    .state('app.wordsearch', {
        url: '/wordsearch',
        templateUrl:'../views/wordsearch.html',
        controller: 'WordSearchController',
        controllerAs:'wordSearch',
        resolve: {
            data: colleges
        }
    })
    .state('app.trending', {
        url: '/trending/:college',
        templateUrl:'../views/trending.html',
        controller: 'TrendingController',
        controllerAs:'trending',
        resolve: {
            data: colleges
        }
    });

    function colleges(RestService) {
        return RestService.getCollegeList().then(function(response) {
            return response.data;
        });
    }
});
