var george = angular.module('george');

george.factory('RestService', RestService);

RestService.$inject = ['$http'];
function RestService($http) {
    var service = {};
    var offset = new Date().getTimezoneOffset()

    service.getPost = function(postId) {
        return $http.get('/post/' + postId);
    };

    service.getComment = function(commentId) {
        return $http.get('/comment/' + commentId);
    };

    service.getCollegeList = function() {
        return $http.get('/colleges', {cache: true});
    };

    service.getCommentsForPost = function(postId) {
        return $http.get('/comments/' + postId, {cache: true});
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
        return $http.get('/wordsearch', { params: params });
    };

    service.getCoKeywords = function(college, keyword) {
        var params = {
            college: college,
            keyword: keyword
        };
        return $http.get('/cokeywords', {params: params});
    }
    return service;
}

