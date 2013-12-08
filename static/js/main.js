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

        var create_canvas = function() {
            $("#canvas-holder").append(
                    [
                    "<canvas id='kenburns' width='",
                    that.width,
                    "' height='",
                    that.height,
                    "'></canvas>"
                    ].join("")
                    );

            return $("#kenburns")[0];
        }

        var get_width = function() {
            return $(window).width();
        }

        var get_height = function() {
            return $(window).height();
        }
    }
}());

function play_audio() {
    var playable = false;
    var player = $("#player")[0];
    console.log("yo");
    var burner = new Burner();
    burner.create_canvas();
    var lookup = new MemeLookup(memes);
    lookup.load_memes(function(canvases) {
        $("#player")[0].play();
        console.log("HIIIIIIIIIIIIIIIIIIIIII");
        console.log(canvases);
        setTimeout(function() {
            console.log("GO");
            $('#kenburns').kenburns({
                images:canvases,
                frames_per_second: 60,
                display_time: 500,
                fade_time: 1000,
                zoom: .6,
                background_color:'#ffffff',
            })
        }, intro_time);
    });
}

$(window).ready(function() {
    $("#player")[0].load();
    play_audio();
});
