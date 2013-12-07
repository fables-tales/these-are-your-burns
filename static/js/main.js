var Burner = (function() {
    return function() {
        var that = this;
        var canvas = null;
        var state = "LOADING";
        var time = 0;
        var meme_lookup = new MemeLookup(memes);
        var last_tick = 0;

        this.create_canvas = function() {
            that.width = get_width();
            that.height = get_height();
            canvas = create_canvas();
            that.context = canvas.getContext("2d");
        }

        this.notify_playstart = function() {
            last_tick = Date.now();
            time = 0;
            state = "PLAYING";
        }

        this.render_frame = function() {
            that.context.fillStyle = "black";
            that.context.fillRect(0, 0, that.width, that.height);
            if (state == "LOADING") {
                var x = canvas.width / 2;
                var y = canvas.height / 2;

                that.context.font = '30pt Helvetica neueu';
                that.context.textAlign = 'center';
                that.context.fillStyle = 'white';
                that.context.fillText('Loading...', x, y);
            } else {
                time += Date.now() - last_tick;
                last_tick = Date.now();
                var meme = meme_lookup.current_meme(time);
                var image_url = meme["image_url"];
                var top_text  = meme["top_text"];
                var bottom_text  = meme["bottom_text"];
                console.log(meme);
                console.log(bottom_text);
                Meme(image_url, "canvas", top_text, bottom_text);
            }
        }

        var create_canvas = function() {
            $("#canvas-holder").append(
                [
                    "<canvas id='canvas' width='",
                    that.width,
                    "' height='",
                    that.height,
                    "'></canvas>"
                ].join("")
            );

            return $("#canvas")[0];
        }

        var get_width = function() {
            return $(window).width();
        }

        var get_height = function() {
            return $(window).height();
        }
    }
}());

$(window).ready(function() {
    var player = $("#player")[0];
    player.volume = 0;

    var burner = new Burner();

    burner.create_canvas();

    function render_frame() {
        burner.render_frame();
    }

    function ready_to_party() {
        player.play();
        burner.notify_playstart();
    }

    setInterval(render_frame, 16);

    $("#player").on("canplaythrough", ready_to_party);
});
