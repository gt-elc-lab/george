exports.LoginStateController = LoginStateController;
exports.RegisterStateController = RegisterStateController;
exports.MainStateController = MainStateController;
exports.RegisterStateController = RegisterStateController;


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
            $state.go('gthealth.main');
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
            $state.go('gthealth.main');
        }, 1500);
    }
}