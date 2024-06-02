document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('fetch-form');
    const urlInput = document.getElementById('url');

    function ensureHttps(url) {
        if (!/^https?:\/\//i.test(url)) {
            return 'https://' + url;
        }
        return url;
    }

    if (localStorage.getItem('url')) {
        urlInput.value = localStorage.getItem('url');
    }

    form.addEventListener('submit', function(event) {
        const url = urlInput.value;
        const formattedUrl = ensureHttps(url);
        urlInput.value = formattedUrl;
        localStorage.setItem('url', formattedUrl);
    });

    var collapsibles = document.getElementsByClassName("collapsible");

    for (var i = 0; i < collapsibles.length; i++) {
        collapsibles[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
});
