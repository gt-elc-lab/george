require('angular');
require('angular-ui-router');

var controllers = require('./controllers');
var utils = require('./utils');
var directives = require('./directives');


var george = angular.module('george', ['ui.router'])
    .controller('ShellController', controllers.ShellController)
    .controller('WordsearchController', controllers.WordsearchController)
    .controller('HomeController', controllers.HomeController)

    .directive('topicGraph', directives.TopicGraph)
    .directive('keywordFrequencyGraph', directives.KeywordFrequencyGraph)
    .directive('sentimentTable', directives.SentimentTable)

    .service('TopicNotifier', utils.TopicNotifier)
    .factory('TooltipFactory', utils.TooltipFactory)
    .factory('RestService', utils.RestService);

george.config(function($httpProvider, $stateProvider, $urlRouterProvider) {
     $httpProvider.interceptors.push(function() {
        var apiUrl = 'http://localhost:5000';
        return {
            request: function(config) {
                if (config.url.startsWith('/george')) {
                    config.url = apiUrl + config.url;
                }
                return config;
            }
        };
    });

    $stateProvider
        .state('george', {
            url:'/george',
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
        .state('george.main', {
            url: '/main/:college',
            templateUrl: 'george/templates/main-template.html',
            controller: 'ShellController',
            controllerAs: 'shell'
        })
        .state('george.main.dashboard', {
            url: '/dashboard',
            templateUrl: 'george/templates/dashboard-template.html'
        })
        .state('george.main.wordsearch', {
            url: '/wordsearch',
            templateUrl: 'george/templates/wordsearch-template.html',
            controller: 'WordsearchController',
            controllerAs: 'ws'
        });
});
