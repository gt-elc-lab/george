var george = angular.module('george');
george.service('RestService', RestService);

RestService.$inject = ['$http'];
function RestService($http) {
    var service = {};

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
        return $http.get('/comments/' + postId);
    };

    service.getTermFrequencyData = function(term, colleges, opt_start, opt_end) {
        var params = {
                term: term,
                colleges: colleges
            };
        if (opt_start && opt_end) {
            params.start = opt_start;
            params.end = opt_end;
        }
        return $http.get('/wordsearch', { params: params });
    };

    return service;
}

