require('angular');
require('angular-ui-router');
require('angular-resource');

var controllers = require('./controllers');
var utils = require('./utils');
var authentication = require('./authentication');
var directives = require('./directives');


var gthealth = angular.module('gthealth', ['ui.router', 'ngResource'])
    .controller('LoginStateController', controllers.LoginStateController)
    .controller('RegisterStateController', controllers.RegisterStateController)
    .controller('MainStateController', controllers.MainStateController)
    .controller('ReplyStateController', controllers.ReplyStateController)

    .directive('feedPostCard', directives.FeedPostCard)
    .directive('responseCard', directives.ResponseCard)

    .service('CurrentUserService', authentication.CurrentUserService)
    .service('AuthenticationService', authentication.AuthenticationService)
    .service('Post', utils.Post)
    .service('ResponseListModel', utils.ResponseListModel);

gthealth.config(function($httpProvider, $stateProvider, $urlRouterProvider) {
     $httpProvider.interceptors.push(function() {
        var apiUrl = 'http://localhost:5000';
        return {
            request: function(config) {
                if (config.url.startsWith('/gthealth')) {
                    config.url = apiUrl + config.url;
                }
                return config;
            }
        };
    });

     $stateProvider
        .state('gthealth', {
            url: '/gthealth',
            templateUrl: 'gthealth/templates/home.html'
        })
        .state('gthealth.login', {
             url: '/login',
            templateUrl: 'gthealth/templates/login.html',
            controller: 'LoginStateController',
            controllerAs: 'Login'
        })
        .state('gthealth.register', {
            url: '/register',
            templateUrl: 'gthealth/templates/register.html',
            controller: 'RegisterStateController',
            controllerAs: 'Register'
        })
        .state('gthealth.about', {
            url: '/about',
            templateUrl: 'gthealth/templates/about.html'
        })
        .state('gthealth.main', {
            url: '/main',
            templateUrl: 'gthealth/templates/main.html',
            controller: 'MainStateController',
            controllerAs: 'Main'
        })
        .state('gthealth.main.reply', {
            url: '/reply/:_id',
            templateUrl: 'gthealth/templates/reply.html',
            controller: 'ReplyStateController',
            controllerAs: 'Reply',
            params: {
                post: null
            }
        })
        .state('gthealth.main.settings', {
            url: '/settings',
            templateUrl: 'partials/settings.html'
        });
});
