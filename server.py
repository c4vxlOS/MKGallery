from flask import Flask, request, jsonify
import main as mkg
import argparse
import os
import re
import json

DB_PATH = "./db"
DEFAULT_COLORS = None

def get_items(id):
    path = DB_PATH + "/" + id
    try:
        return json.load(open(path, "r"))
    except:
        return []

def set_items(id, val):
    path = DB_PATH + "/" + id
    if val == []:
        os.remove(path)
        return
    os.makedirs(DB_PATH, exist_ok=True)
    json.dump(val, open(path, "w"))

def _prepare_gallery(id, **args):
    src = mkg.generate_html(get_items(id), id, **args)
    src = re.sub(r"(const init_item_metadata = \(\) => \{.*?};\s*\}\);\s*\};)", r"\1 init_item_metadata(); let __items_clone = items;", src)

    src = re.sub(r"const warn_unsaved = \(\) => \{.*?\}", """const warn_unsaved = () => { 
        let gn = location.pathname.split("/").reverse()[0];
        __items_clone.forEach((item, id) => {
            let match = items.find(x => x.src == item.src);
            if (!match) fetch(`update/${gn}/?action=remove&id=${id}`);
            if (match?.categories?.length != item.categories.length || match?.categories?.some((v, i) => v !== item.categories[i]) == true)
                 fetch(`update/${gn}/?id=${id}&action=set_categories&categories=${JSON.stringify(match.categories)}`);
        });
        items.forEach((item, id) => {
            let match = __items_clone.find(x => x.src == item.src);
            if (!match) fetch(`update/${gn}/?action=add&src=${item.src}&categories=${JSON.stringify(item.categories)}`);
        });
        __items_clone = items;
    }""", src)

    return src

def create_flask_server():
    app = Flask(__name__)

    @app.route("/")
    def _root():
        return """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>MKGallery Server</title><style> :root { --bg: #101011; --bg-1: hsl(from var(--bg) h s 7%); --bg-2: hsl(from var(--bg) h s 10%); --highlight: #d6d0d0; --border: hsl(from var(--bg) h s 25%); --primary: #121212; --font: Verdana; --accent: #ffffff; } body, html { margin: 0; padding: 0; background: linear-gradient(161deg, var(--bg) 50%, var(--bg-1) 88%); background-repeat: no-repeat; gap: 35px; padding: 30px 10px; align-items: center; min-height: 100vh; } ::-webkit-scrollbar { width: 0px; height: 1px; } ::-webkit-scrollbar-thumb { background-color: var(--accent); } .row, .col { display: flex; } .row { flex-direction: row; } .col { flex-direction: column; } .center { align-items: center; justify-content: center; } .gap { gap: 15px; } .wrap { flex-wrap: wrap; } * { box-sizing: border-box; color: var(--accent); outline: none; font-family: var(--font); transition: .2s; } .primary { background: var(--primary); padding: 8px 30px; border: 1px solid var(--border); backdrop-filter: blur(10px); border-radius: 10px; } button.primary:hover, .primary.active { opacity: .6; cursor: pointer; } input.primary { padding: 8px; } textarea.primary { padding: 8px; resize: none; height: 40ch; width: 100%; } .modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg); z-index: 9999; opacity: 0; pointer-events: none; } .modal.active { opacity: 1; pointer-events: unset; } .modal .modal__content { max-width: min(90vw, 90ch); } .button__panel { gap: 2px; margin-top: 20px; width: 100%; } .button__panel * { border-radius: 0; } .button__panel *:first-child { border-radius: 10px 10px 0px 0px; } .button__panel *:last-child { border-radius: 0px 0px 10px 10px; } .input__bar { gap: 2px; } .input__bar input { border-radius: 10px 0px 0px 10px; } .input__bar button { border-radius: 0px 10px 10px 0px; } .switch { display: flex; gap: 2px; border-radius: 10px; overflow: hidden; } .switch span { flex-grow: 1; background: var(--bg-2); padding: 10px 15px; cursor: pointer; } .switch span.active { background: var(--highlight); color: var(--primary); } .tooltip { position: relative; } .tooltip span { position: absolute; top: calc(100% + 5px); background: var(--bg-2); color: var(--text); padding: 5px 20px; border-radius: 10px; opacity: 0; text-align: center; display: none; width: max-content; } .tooltip:hover span { opacity: 1; display: unset; } .tooltip[tooltip-pos="right"] span { right: 5px; border-radius: 10px 0px 10px 10px; } </style><style> body, html { margin: 0; padding: 0; max-height: 100vh; overflow: hidden; } </style></head><body class="col center"><div class="primary" style="width: min(97vw, 70ch);"><p style="font-size: 1.5rem; margin-bottom: 3px;">MKGallery</p><hr><p style="opacity: .7;">Using MKGallery you'll be able to create, manage and share you own collections of all sorts of media.</p><br><div class="input__bar row" style="width: 100%;"><input id="searchbar" autofocus type="text" class="primary" placeholder="Search for a name or create one" style="flex-grow: 1;"><button class="primary" onclick="window.location.href = this.parentNode.querySelector('input').value">Go</button><script> document.querySelector("#searchbar").value = crypto.randomUUID(); </script></div><br><br><p>Made by <a href="https://c4vxl.de">c4vxl</a></p></div></body></html>"""

    @app.route("/<id>", methods=["GET"])
    def _view_gallery(id):
        return _prepare_gallery(id, **DEFAULT_COLORS)
    
    @app.route("/update/<id>/", methods=["GET"])
    def _update(id):
        data = get_items(id)
        
        action = request.args.get("action")
        if not action:
            return jsonify({ "success": False })
        

        if action == "add":
            data.append({ "src": request.args.get("src"), "categories": json.loads(request.args.get("categories")) })
        else:
            obj = int(request.args.get("id", -1))
            if obj == -1:
                return jsonify({ "success": False })

            if action == "remove":
                data.pop(obj)
        
            elif action == "set_categories":
                data[obj]["categories"] = json.loads(request.args.get("categories"))
        
        set_items(id, data)

        return jsonify({ "success": True })

    return app

def start_flask_server(port = 4420, host = "127.0.0.1"):
    server = create_flask_server()
    server.run(host, port, False)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Host a server synced version of mkgallery.")
    parser.add_argument("--port", "-po", type=int, help="Set the port the server should be running on. (Default: 4420)", default=4420)
    parser.add_argument("--host", "-ht", type=str, help="Set the host the server should be running on. (Default: 127.0.0.1)", default="127.0.0.1")
    parser.add_argument("--font", "-f", type=str, help="Set the default font.")
    parser.add_argument("--accent", "-a", type=str, help="Set the default accent color.")
    parser.add_argument("--background", "-bg", type=str, help="Set the default background color.")
    parser.add_argument("--highlight", "-hl", type=str, help="Set the default highlight color.")
    parser.add_argument("--primary", "-p", type=str, help="Set the default primary color.")
    parser.add_argument("--colorpreset", "-cp", type=str, help="Set a default color preset. (See --list-presets; Default: 1)", default="1")
    parser.add_argument("--list-presets", "-lp", action="store_true", help="Get a list of all presets.")

    args = parser.parse_args()

    def default(a, b): return a if a else b

    if args.list_presets:
        print("ID \t Background \t Primary \t Accent \t Highlight \t Font")
        for p, c in mkg.presets.items():
            print(f"{p} \t {c['background']} \t {c['primary']} \t {c['accent']} \t {c['highlight']} \t {c['font']}")
    
    preset = mkg.presets[args.colorpreset]
    DEFAULT_COLORS = dict(
        accent = default(args.accent, preset["accent"]),
        background = default(args.background, preset["background"]),
        highlight = default(args.highlight, preset["highlight"]),
        primary = default(args.primary, preset["primary"]),
        font = default(args.font, preset["font"])
    )

    start_flask_server(args.port, args.host)