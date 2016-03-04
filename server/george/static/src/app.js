'use strict'
var george = angular.module('george', ['ui.router']);

george.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');
    $stateProvider
    .state('home', {
        url:'/home',
        templateUrl: 'george/templates/home.html',
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
    .state('main', {
        url: '/main/:college',
        templateUrl: 'george/templates/main-template.html',
        controller: 'ShellController',
        controllerAs: 'shell'
    })
    .state('main.dashboard', {
        url: '/dashboard',
        templateUrl: 'george/templates/dashboard-template.html'
    })
    .state('main.wordsearch', {
        url: '/wordsearch',
        templateUrl: 'george/templates/wordsearch-template.html',
        controller: 'WordsearchController',
        controllerAs: 'ws'
    });
});
