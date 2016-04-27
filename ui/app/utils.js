var d3 = require('d3');
var d3tooltip = require('d3-tip')(d3);

exports.TopicNotifier = TopicNotifier;
exports.TooltipFactory = TooltipFactory;
exports.RestService = RestService;

function TopicNotifier() {

    var callbacks = [];

    this.notify = function(data) {
        callbacks.forEach(function(cb) {
            cb(data);
        });
    };

    this.subscribe = function(cb) {
        callbacks.push(cb);
    };
}


TooltipFactory.$inject = ['$templateCache', '$interpolate'];
function TooltipFactory($templateCache, $interpolate) {
    var factory = {};

    factory.getToolTip = function(templateId) {
        return d3tooltip().attr('class', 'd3-tip')
            .html(function(d) {
                return $interpolate($templateCache.get(templateId))(d);
            });
    };
    return factory;
}


RestService.$inject = ['$http'];
function RestService($http) {
    var service = {};
    var offset = new Date().getTimezoneOffset()

    service.getPost = function(postId) {
        return $http.get('/api/post/' + postId);
    };

    service.getComment = function(commentId) {
        return $http.get('/api/comment/' + commentId);
    };

    service.getCollegeList = function() {
        return $http.get('/api/colleges', {cache: true});
    };

    service.getCommentsForPost = function(postId) {
        return $http.get('/api/comments/' + postId, {cache: true});
    };

    service.getTermFrequencyData = function(term, colleges, opt_start, opt_end) {
        var params = {
                term: term,
                colleges: colleges
            };
        if (opt_start && opt_end) {
            params.start = Math.floor(opt_start.valueOf() / 1000);
            params.end = Math.floor(opt_end.valueOf() / 1000);
        }
        return $http.get('/api/wordsearch', { params: params });
    };

    service.getCoKeywords = function(college, keyword) {
        var params = {
            college: college,
            keyword: keyword
        };
        return $http.get('/api/cokeywords', {params: params});
    }
    return service;
}
