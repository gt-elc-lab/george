require('angular');
require('angular-ui-router');
require('angular-resource');


var gthealth = angular.module('gthealth', ['ui.router', 'ngResource']);
gthealth.service('CurrentUserService', CurrentUserService);
gthealth.service('AuthenticationService', AuthenticationService);
gthealth.service('Post', Post);
gthealth.service('ResponseListModel', ResponseListModel);

gthealth.directive('feedPostCard', FeedPostCard);
gthealth.directive('responseCard', ResponseCard);

gthealth.controller('LoginStateController', LoginStateController);
gthealth.controller('RegisterStateController', RegisterStateController);
gthealth.controller('MainStateController', MainStateController);
gthealth.controller('ReplyStateController', ReplyStateController)


gthealth.config(function($httpProvider, $stateProvider, $urlRouterProvider) {
    $httpProvider.interceptors.push(function() {
        var apiUrl = 'http://localhost:5000';
        return {
            request: function(config) {
                if (config.url.startsWith('/api')) {
                    config.url = apiUrl + config.url;
                }
                return config;
            }
        };
    });

    $urlRouterProvider.otherwise("/home");
    $stateProvider
        .state('home', {
            url: '/home',
            templateUrl: 'partials/home.html'
        })
        .state('home.login', {
             url: '/login',
            templateUrl: 'partials/login.html',
            controller: 'LoginStateController',
            controllerAs: 'Login'
        })
        .state('home.register', {
            url: '/register',
            templateUrl: 'partials/register.html',
            controller: 'RegisterStateController',
            controllerAs: 'Register'
        })
        .state('home.about', {
            url: '/about',
            templateUrl: 'partials/about.html'
        })
        .state('main', {
            url: '/main',
            templateUrl: 'partials/main.html',
            controller: 'MainStateController',
            controllerAs: 'Main'
        })
        .state('main.reply', {
            url: '/reply/:_id',
            templateUrl: 'partials/reply.html',
            controller: 'ReplyStateController',
            controllerAs: 'Reply',
            params: {
                post: null
            }
        })
        .state('main.settings', {
            url: '/settings',
            templateUrl: 'partials/settings.html'
        });
});

Post.$inject = ['$resource'];
function Post($resource) {
    return $resource('/api/post/:_id', {_id: '@_id'}, {
        query: {
            method: 'GET',
            isArray: true
        }
    });
}

ResponseCard.$inject = ['$state'];
function ResponseCard() {
    return {
        scope: {
            response: '=',
            sendResponse: '&'
        },
        restrict: 'AE',
        templateUrl: 'partials/responsecard.html',
        link: function($scope, $element, $attrs) {

        },
        controller: function($scope, $state) {
            $scope.message = {
                visble: false,
                text: 'Reply with this message?'
            };

            $scope.reply = function() {
                $scope.sendResponse()($scope.response);
            };

            $scope.use = function() {
                $scope.message.visible = true;
            };

            $scope.no = function() {
                $scope.message.visible = false;
            };

        }
    }
}

FeedPostCard.$inject = ['$state'];
function FeedPostCard() {
    return {
        scope: {
            post: '='
        },
        restrict: 'AE',
        templateUrl: 'partials/feedpostcard.html',
        link: function($scope, $element, $attrs) {
            $scope.$on('$destroy', function() {
                $element.remove();
            });
        },
        controller: function($scope, $state) {
            var textLimit = 500;
            var showMoreText = 'show more';
            var showLessText = 'show less';

            $scope.textLimit = textLimit;
            $scope.textPrompt = showMoreText;
            $scope.shouldShowButton = $scope.post.content.length > textLimit;

            $scope.message = {
                visible: false,
                text: 'Are you sure you want to discard this message?'
            };

            $scope.showMessage = function() {
                $scope.message.visible =  !$scope.message.visible;
            };

            $scope.show = function() {
                var fn = $scope.textPrompt == showMoreText ? showMore : showLess;
                fn();
                return;
            };

            $scope.discard = function() {
                $scope.post.$delete().then(function(response) {
                    $scope.$destroy();
                }, function(error) {

                })
            };

            $scope.reply = function() {
                $state.go('main.reply', {_id: $scope.post._id, post: $scope.post});
                return;
            }

            function showMore() {
                $scope.textLimit = Infinity;
                $scope.textPrompt = showLessText;
                return;
            }

            function showLess() {
                $scope.textLimit = textLimit;
                $scope.textPrompt = showMoreText;
                return;
            }

        }
    }
}

LoginStateController.$inject = ['$state', 'AuthenticationService'];
function LoginStateController($state, AuthenticationService) {
    this.error = null;
    this.login = function() {
        this.error = null;
        AuthenticationService.login(this.email, this.password).then(function(response) {
            $state.go('main');
        }.bind(this), function(error) {
            this.error = error;
        }.bind(this));
    };
}

RegisterStateController.$inject = ['$state', 'AuthenticationService'];
function RegisterStateController($state, AuthenticationService) {
    this.error = null;
    this.register = function() {
        this.error = null;
        AuthenticationService.register(this.email, this.password)
            .then(function(response) {
            $state.go('main');
        }.bind(this), function(error) {
            this.error = error;
        }.bind(this));
    };
}

MainStateController.$inject = ['$state', '$http', 'Post', 'AuthenticationService', 'CurrentUserService'];
function MainStateController($state, $http, Post, AuthenticationService, CurrentUserService) {
    this.posts = Post.query();
}

RegisterStateController.$inject = ['$state', 'Post', '$timeout', 'ResponseListModel', 'CurrentUserService'];
function ReplyStateController($state, Post, $timeout, ResponseListModel, CurrentUserService) {
    var currentUser = CurrentUserService.getCurrentUser();
    this.post = $state.params.post ? $state.params.post : Post.get({_id: $state.params._id});
    this.responses = ResponseListModel;

    this.successMessage = {
        visible: false,
        text: "Reply sent!"
    };

    this.sendResponse = respond.bind(this);

    function respond(message) {
        this.successMessage.visible = true;
        $timeout(function() {
            $state.go('main');
        }, 1500);
    }
}

function CurrentUserService() {
    var currentUser = null;

    this.getCurrentUser = function() {
        return currentUser;
    };

    this.setCurrentUser = function(user) {
        this.currentUser = user;
    };
}

AuthenticationService.$inject = ['$http', '$q', 'CurrentUserService'];
function AuthenticationService($http, $q, CurrentUserService) {

    this.login = function(email, password) {
        var deferred = $q.defer();
        $http.post('/api/login', {email: email, password: password})
            .then(function(response) {
            CurrentUserService.setCurrentUser(response.data);
            deferred.resolve(response.data);
        }, function(error) {
            deferred.reject(error.data);
        });
        return deferred.promise;
    };

    this.logout = function() {

    };

    this.register = function(email, password) {
        var deferred = $q.defer();
        $http.post('/api/register', {email: email, password: password})
            .then(function(response) {
            CurrentUserService.setCurrentUser(response.data);
            deferred.resolve(response.data);
        }, function(error) {
            deferred.reject(error.data);
        });
        return deferred.promise;
    };
}

function ResponseListModel() {
    // TODO(simplyfaisal): Create content
    var responses = [{
            title: 'Informational Response',
            content: 'This will be a response that provides a link to the counseling service website',
        }, {
            title: 'Provide Resources Response',
            content: 'This will be a response providing detailed information about all of the avaible resources and how access them',
        }];

    return responses;
}