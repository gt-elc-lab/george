exports.ResponseListModel = ResponseListModel;
exports. Post = Post;

Post.$inject = ['$resource'];
function Post($resource) {
    return $resource('/api/post/:_id', {_id: '@_id'}, {
        query: {
            method: 'GET',
            isArray: true
        }
    });
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
