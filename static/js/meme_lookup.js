var MemeLookup = (function() {
    return function(memes) {
        var memes = memes;
        var that = this;
        var images = [];
        var canvases = [];

        this.on_ready = function() {};

        for (var i = 0; i < memes.length; i++) {
            var img = Image.new;
            img.src = memes[i]["image_url"];
            images.push(img)
        }

        for (var i = 0; i < images.length; i++) {
            img = images[i];
            img.onload = function() {
                var c = new Canvas();
                c.width = img.width;
                c.height = img.height;
                Meme(img.src, c);
                canvases.push(canvas);
                if (canvases.length == memes.length) {
                    that.on_ready();
                }
            }
        }

        this.current_meme = function(time) {
            var accumulated_time = 0;
            var i = 0;
            while (time < accumulated_time) {
                accumulated_time += memes[i]["transition_after"];
                i += 1;
            }

            return memes[i];
        }
    };
}());
