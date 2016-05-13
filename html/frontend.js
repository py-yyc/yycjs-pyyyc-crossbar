

// simplicity for demo: global variable stores our WAMP session
var wamp_session = null;

function update_status(text, color) {
    document.getElementById("status").innerHTML = text;
    document.getElementById("status").style.background = color;
}

function pixel_click(x, y) {
    // console.log("click: " + x + ", " + y);
    if (wamp_session) {
        wamp_session.call("meejah.click", [x, y]);
    }
}

window.onclose = function() {
    if (wamp_session) {
	wamp_session.close();
    }
}

window.onload = function() {
    update_status("Connecting", "#ff9");
    var wsurl = "ws://" + window.location.hostname + ":" + window.location.port + "/ws";
    var connection = new autobahn.Connection(
	{
	    url: wsurl,
	    realm: 'demo',
	    max_retries: 5,
	}
    );
    console.log("connecting to: " + wsurl);

    connection.onopen = function(session) {
        // set our messy global variable
        wamp_session = session;
        update_status("Connected", "#9f9");

        function on_board_update(args, kwargs) {
            console.log("on_board_update:", args, kwargs);
            var x = args[0];
            var y = args[1];
            var color = args[2];
            pix = document.getElementById("pixel_" + x + "_" + y);
            var bgcolor = "rgba(" + color[0] + ", " + color[1] + ", " + color[2] + ", 1.0)";
            pix.style.background = bgcolor;
        }
        session.subscribe('meejah.board_update', on_board_update);

        function on_board_invalid() {
	    console.log("on_board_invalid");
            session.call("meejah.get_board")
                .then(function(board) {
                    for (var x = 0; x < 16; x++) {
			for (var y = 0; y < 16; y++) {
                            var id = "pixel_" + x + "_" + y;
                            var color = "rgb("
                                + board[x][y][0] + ", "
                                + board[x][y][1] + ", "
                                + board[x][y][2] + ")";

                            document.getElementById(id).style.background = color;
                        }
                    }
                });
	    session.call("meejah.get_client_count")
		.then(function(clients) {
		    document.getElementById("client_count").innerHTML = "Clients: " + clients;
		});
        }
        session.subscribe('meejah.board_invalid', on_board_invalid);
        // get the initial board-state
        on_board_invalid();
    };

    connection.onclose = function(e) {
        update_state("Offline", "#f99");
        console.log("Connection closed.");
    };

    connection.open();
}
