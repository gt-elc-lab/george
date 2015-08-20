var george = angular.module('george');

george.service('FlaskService', FlaskService);

FlaskService.$inject = ['$http'];
function FlaskService($http) {
    var service = {};

    service.getPost = function(postId) {

    };

    service.getComment = function(commentId) {

    };

    service.getCollegeList = function() {

    };

    service.getCommentsForPost = function(postId) {

    };

    return service;
}

