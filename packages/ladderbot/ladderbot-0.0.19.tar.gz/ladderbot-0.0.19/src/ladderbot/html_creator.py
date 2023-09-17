import importlib.resources

def make_game_html(uname, uid, hash):
    game_html =  """<!doctype html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
    <title>Ladder Slasher v1.32.2</title>

    <style type="text/css" media="all">
    @import url("https://ladderslasher.d2jsp.org/v1.32/lsWS.css?v=8");

    </style>
    <script src=""" + str(importlib.resources.files("ladderbot")) + "\\o.js" +"?v=5" + """></script>
    <script>

    window.addEventListener("contextmenu",e=>e.preventDefault());
    function pload() {
        mld();
    """ + f"njs.h='{hash}'; njs.uid={uid}; njs.uname='{uname}';" + """Login.draw();
    }
    </script>
    <body onload="pload();"

        ondragstart="return false" draggable="false"
        ondragenter="event.dataTransfer.dropEffect='none'; return eSP(window.event)"
        ondragover="event.dataTransfer.dropEffect='none'; return eSP(window.event)"
        ondrop="event.dataTransfer.dropEffect='none'; return eSP(window.event)"
    >

    <div id="stage">
    </div>

    </body>
    </html>"""
    with open(str(importlib.resources.files("ladderbot")) + "\\index.html", "w") as f:
        f.write(game_html)
