var george = angular.module('george');

george.service('RestService', RestService);
george.service('ColorHashService', ColorHashService);

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
        return $http.get('/comments/' + postId, {cache: true});
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

function ColorHashService() {
    var service = {};

    service.colorFromString = function(string) {
        return rgbFromInt(hash(string));
    };

    function hash(string) {
        var hash = 0;
        string.split('').forEach(function(ch, i) {
            hash = ch.charCodeAt(0) + ((hash << 5) - hash);
        });
        return hash;
    }

    function rgbFromInt(n) {
        var c = (n & 0x00FFFFFF)
        .toString(16)
        .toUpperCase();

        return "00000".substring(0, 6 - c.length) + c;
    }

    return service;
}

