require('angular');
require('angular-ui-router');

var controllers = require('./controllers');
var utils = require('./utils');
var directives = require('./directives');


var george = angular.module('george', ['ui.router'])
    .controller('ShellController', controllers.ShellController)
    .controller('WordsearchController', controllers.WordsearchController)

    .directive('topicGraph', directives.TopicGraph)
    .directive('keywordFrequencyGraph', directives.KeywordFrequencyGraph)
    .directive('sentimentTable', directives.SentimentTable)

    .service('TopicNotifier', utils.TopicNotifier)
    .factory('TooltipFactory', utils.TooltipFactory)
    .factory('RestService', utils.RestService);


