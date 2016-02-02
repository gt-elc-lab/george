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
    .state('main', {
        url: '/main/:college',
        templateUrl: 'src/main/main-template.html',
        controller: 'ShellController',
        controllerAs: 'shell'
    })
    .state('main.dashboard', {
        url: '/dashboard',
        templateUrl: 'src/dashboard/dashboard-template.html'
    })
    .state('main.wordsearch', {
        url: '/wordsearch/:vizType?',
        params: {
            vizType: 'frequency'
        },
        templateUrl: 'src/wordsearch/wordsearch-template.html',
        controller: 'WordsearchController',
        controllerAs: 'ws'
    });
});
