require('angular');
require('angular-ui-router');
require('angular-resource');

var app = angular.module('app',
    ['ui.router', 'ngResource', 'gthealth', 'george']);

require('./george');
require('./gthealth');
