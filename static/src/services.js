var george = angular.module('george');

george.factory('RestService', RestService);
george.factory('ColorHashService', ColorHashService);

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

    service.getTrendingGraph = function(college) {
        return $http.get('/trendinggraph/' + college);
    };

    service.getTodaysActivitySummary = function(college) {
        var params = {
            college: college,
            offset : offset
        };
        return $http.get('/daily', {params: params, cache: true});
    };

    service.getTrendingKeywords = function(college, dayLimit) {
        var params = {
            college: college,
            days_ago: dayLimit,
            offset: offset
        };
        return $http.get('/trending', {params: params, cache: true});
    };

    service.getActivity = function(college, dayLimit) {
        var params = {
            college: college,
            days_ago: dayLimit,
            offset: offset
        };

        return $http.get('/activity', {params: params, cache: true});
    };

    service.getWordTree = function(college, term) {
        var params = {
            college: college,
            term: term
        };
        return $http.get('/suffixtree', {params: params});
    }

    service.getCoKeywords = function(college, keyword) {
        var params = {
            college: college,
            keyword: keyword
        };
        return $http.get('/cokeywords', {params: params});
    }
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

        return '#' + "00000".substring(0, 6 - c.length) + c;
    }

    return service;
}

