exports.ResponseCard = ResponseCard;
exports.FeedPostCard = FeedPostCard;

ResponseCard.$inject = ['$state'];
function ResponseCard() {
    return {
        scope: {
            response: '=',
            sendResponse: '&'
        },
        restrict: 'AE',
        templateUrl: 'gthealth/templates/responsecard.html',
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
        templateUrl: 'gthealth/templates/feedpostcard.html',
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
                $state.go('gthealth.main.reply', {_id: $scope.post._id, post: $scope.post});
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