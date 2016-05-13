var autobahn = require('autobahn');

var connection = new autobahn.Connection({
    url: 'ws://yycjs.meejah.ca/ws',
    realm: 'demo'
});

var _clients = new Map();
function* _color_generator() {
    while (true) {
	yield {r: 255, g: 0, b: 0}
	yield {r: 0, g: 255, b: 0}
	yield {r: 0, g: 0, b: 255}
    }
}
var _client_color = _color_generator();

function client_create(client_id) {
    // each client gets a 16x16 array of bools
    var new_board = new Array(16);
    for (var i=0; i < 16; i++) {
	new_board[i] = new Array(16);
	for (var j=0; j < 16; j++) {
	    new_board[i][j] = false;
	}
    }
    // assign a color to the client
    var new_color = _client_color.next().value;
    // freshly-minted client
    return {
	id: client_id,
	color: new_color,
	board: new_board,
    }
}

function board_click(client_id, x, y) {
    // for each click on a square, we just toggle the state (on/off)
    client = _clients.get(client_id);
    console.log('board_click', client_id, x, y, client.board[x][y]);
    client.board[x][y] = !client.board[x][y];
}

function board_color_at(x, y) {
    // union of all clients' state at a particular location
    var color = [0, 0, 0];

    _clients.forEach(function (client) {
	if (client.board[x][y]) {
	    // taking max of each component, not e.g. average
	    color = [
		Math.max(color[0], client.color.r),
		Math.max(color[1], client.color.g),
		Math.max(color[2], client.color.b),
	    ];
	}
    });
    return color;
}

//board_click(1, 0, 0);
//console.log(board_color_at(0, 0));

connection.onopen = function (session) {
    console.log('joined');

    // an API method, exposed to clients as "meejah.click"
    function client_click(args, kwargs, details) {
	var x = args[0];
	var y = args[1];

	board_click(details.caller, x, y);
	console.log('publish meejah.board_update', [x, y, board_color_at(x, y)]);
	session.publish('meejah.board_update', [x, y, board_color_at(x, y)]);
    }
    session.register('meejah.click', client_click);

    // API method to get entire board-state (e.g. at client startup)
    function board_state() {
	console.log("board_state");
	var board = new Array(16);
	for (var x=0; x < 16; x++) {
	    board[x] = new Array(16);
	    for (var y=0; y < 16; y++) {
		board[x][y] = board_color_at(x, y);
	    }
	}
	return board;
    }
    session.register('meejah.get_board', board_state);

    /* notice when clients come and go */
    function client_left(args) {
	var session_id = args[0];
        _clients.delete(session_id);
	session.publish("meejah.board_invalid");
    }
    function client_join(args) {
	var details = args[0];
	_clients.set(details.session, client_create(details.session));
        session.publish("meejah.board_invalid")	
    }
    session.subscribe("wamp.session.on_join", client_join)
    session.subscribe("wamp.session.on_leave", client_left)

    // API method to get client-count
    session.register(
	'meejah.get_client_count',
	function() { return _clients.size }
    );
};

connection.open();
