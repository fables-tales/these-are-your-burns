var MemeLookup = (function() {
    return function(memes) {
        var memes = memes;
        var that = this;
        var images = [];
        var canvases = [];


        this.load_memes = function(callback) {
            for (var i = 0; i < memes.length; i++) {
                var img = new Image();
                img.src = memes[i]["image_url"];
                images.push(img)
            }

            for (var i = 0; i < images.length; i++) {
                img = images[i];
                meme = memes[i];
                img.onload = load_callback(i, meme, img, callback);
            }
        }

        load_callback = function(index, meme, image, callback) {
            return function() {
                var c = document.createElement('canvas');
                c.width = this.width;
                c.height = this.height;
                image = Meme(this.src, c, meme.top_text, meme.bottom_text, function() {
                    canvases.push([index, c.toDataURL()]);
                    if (canvases.length == memes.length) {
                        sorted = canvases.sort(function(a,b) { return a[0] - b[0]});
                        canvases = sorted.map(function(element) { return element[1] });
                        console.log(canvases);
                        callback(canvases);
                    }
                });
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
