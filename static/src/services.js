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
        return $http.get('/colleges');
    };

    service.getCommentsForPost = function(postId) {
        return $http.get('/comments/' + postId);
    };

    return service;
}

