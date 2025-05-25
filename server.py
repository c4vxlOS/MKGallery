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

json.dump(mkg.parse_items(mkg.get_content("sources.txt").decode().split("\n")), open("db/1", "w"))

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