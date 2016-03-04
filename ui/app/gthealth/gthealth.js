require('angular');
require('angular-ui-router');
require('angular-resource');
require('./controllers');


var gthealth = angular.module('gthealth', ['ui.router', 'ngResource']);


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
});

module.exports = gthealth;