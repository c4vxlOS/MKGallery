import argparse
import re
import mimetypes
import base64
import requests
import sys
import os

presets = {
    "1": { "background": "#101011", "primary": "#121212", "accent": "#ffffff", "highlight": "#d6d0d0", "font": "Verdana" }
}

def generate_html(items: list, title: str,
                  background: str, primary: str, accent: str, highlight: str, font: str,
                  item_width: str = "50ch", item_height: str = "50ch", item_zoom_scale: str = "2") -> str:
    return """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><style> :root {{ --bg: {bg}; --bg-1: hsl(from var(--bg) h s 7%); --bg-2: hsl(from var(--bg) h s 10%); --highlight: {highlight}; --border: hsl(from var(--bg) h s 25%); --primary: {primary}; --font: {font}; --accent: {accent}; }} body, html {{ margin: 0; padding: 0; }} body {{ padding: 30px 10px; background: linear-gradient(161deg, var(--bg) 50%, var(--bg-1) 88%); background-repeat: no-repeat; gap: 35px; align-items: center; min-height: 100vh; }} ::-webkit-scrollbar {{ width: 0px; height: 1px; }} ::-webkit-scrollbar-thumb {{ background-color: var(--accent); }} .row, .col {{ display: flex; }} .row {{ flex-direction: row; }} .col {{ flex-direction: column; }} .center {{ align-items: center; justify-content: center; }} .gap {{ gap: 15px; }} .wrap {{ flex-wrap: wrap; }} * {{ box-sizing: border-box; color: var(--accent); outline: none; font-family: var(--font); transition: .2s; }} .primary {{ background: var(--primary); padding: 8px 30px; border: 1px solid var(--border); backdrop-filter: blur(10px); border-radius: 10px; }} button.primary:hover, .primary.active {{ opacity: .6; cursor: pointer; }} input.primary {{ padding: 8px; }} textarea.primary {{ padding: 8px; resize: none; height: 40ch; width: 100%; }} .modal {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg); z-index: 9999; opacity: 0; pointer-events: none; }} .modal.active {{ opacity: 1; pointer-events: unset; }} .modal .modal__content {{ max-width: min(90vw, 90ch); }} .button__panel {{ gap: 2px; margin-top: 20px; width: 100%; }} .button__panel * {{ border-radius: 0; }} .button__panel *:first-child {{ border-radius: 10px 10px 0px 0px; }} .button__panel *:last-child {{ border-radius: 0px 0px 10px 10px; }} .input__bar {{ gap: 2px; }} .input__bar input {{ border-radius: 10px 0px 0px 10px; width: 100%; }} .input__bar button {{ border-radius: 0px 10px 10px 0px; width: max-content; }} .switch {{ display: flex; gap: 2px; border-radius: 10px; overflow: hidden; }} .switch span {{ flex-grow: 1; background: var(--bg-2); padding: 10px 15px; cursor: pointer; }} .switch span.active {{ background: var(--highlight); color: var(--primary); }} .tooltip {{ position: relative; }} .tooltip span {{ position: absolute; top: calc(100% + 5px); background: var(--bg-2); color: var(--text); padding: 5px 20px; border-radius: 10px; opacity: 0; text-align: center; display: none; width: max-content; }} .tooltip:hover span {{ opacity: 1; display: unset; }} .tooltip[tooltip-pos="right"] span {{ right: 5px; border-radius: 10px 0px 10px 10px; }} .options__bar {{ width: max-content; gap: 10px; position: fixed; padding-right: 10px; top: 10px; right: 10px; z-index: 999; }} .options__bar .segment {{ width: 5ch; height: 5ch; background: var(--bg-2); padding: 8px; border-radius: 10px; cursor: pointer; }} .options__bar .segment span {{ white-space: nowrap; }} .options__bar .segment svg {{ height: 100%; width: 100%; stroke: var(--accent); }} .options__bar:hover .segment:not(:hover) {{ background: var(--bg-1); }} :root {{ --item-width: {item_width}; --item-height: {item_height}; --item-zoom-scale: {item_zoom_scale}; }} .gallery__items {{ gap: 15px; }} .gallery__items .item.active {{ position: fixed; top: 0; left: 0; z-index: 999; background: var(--bg); width: 100%; height: 100%; }} .gallery__items .item .item__content {{ position: relative; }} .gallery__items .item .item__content .option__buttons {{ position: absolute; top: 5px; right: 5px; gap: 5px; z-index: 99; }} .gallery__items .item .item__content .option__buttons button {{ width: 4ch; height: 4ch; padding: 0; opacity: 0; }} .gallery__items .item .item__content .option__buttons button.fav {{ color: yellow; }} .gallery__items .item .item__content:hover .option__buttons button {{ opacity: 1; }} .gallery__items .item .display {{ max-width: min(97vw, var(--item-width)); max-height: min(97vh, var(--item-height)); object-fit: contain; border-radius: 10px; z-index: 12; }} .gallery__items .item.active .display {{ max-width: min(97vw, calc(var(--item-width) * var(--item-zoom-scale))); max-height: min(97vh, calc(var(--item-height) * var(--item-zoom-scale))); }} .category__list, .category__list, .categories__content {{ max-width: 100%; display: flex; align-items: center; overflow-x: scroll; gap: 10px; }} .category__list .primary {{ padding: 5px 10px; padding-right: 7px; flex-shrink: 0; cursor: default; text-align: center; }} .category__list .primary span {{ color: red; font-weight: 900; font-size: large; margin-left: 15px; cursor: pointer; }} .filter__list .primary {{ font-size: 100%; padding: 5px 10px; }} .filter__list .primary.sep {{ position: relative; margin-right: 9px; }} .filter__list .primary.sep::after {{ position: absolute; content: ""; height: 70%; width: 1px; background: var(--accent); right: -11px; top: 0px; bottom: 0; margin: auto; }} .notification__container {{ position: fixed; top: 10px; right: 10px; width: min(96vw, 40ch); z-index: 999999; gap: 10px; }} .notification__container .primary {{ width: 100%; padding: 10px 20px; overflow: hidden; padding-bottom: 20px; }} .notification__container .primary button {{ padding: 8px; }} .notification__container .primary button:first-of-type {{ margin-bottom: 3px; }} .notification__container .primary p:nth-child(1) {{ border-bottom: 1px solid var(--border); padding-bottom: 5px; margin-bottom: 8px; font-size: 1.2rem; font-weight: 600; }} .notification__container .primary p {{ margin: 0; color: var(--highlight); opacity: .7; }} .notification__container .primary .bar {{ height: 4px; position: absolute; bottom: 0; left: 0; }} </style></head><body class="col"><div class="notification__container col center" id="notification__container"></div><div class="options__bar row" id="options__bar"><div class="segment row tooltip" onclick="open_modal('.gallery__add__items__modal')"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.19999 4.99999H4.99999M4.99999 4.99999H3.79999M4.99999 4.99999V3.79999M4.99999 4.99999V6.19999" stroke-width="0.4" stroke-linecap="round"/><path d="M9 5C9 6.8856 9 7.82844 8.4142 8.4142C7.82844 9 6.8856 9 5 9C3.11438 9 2.17157 9 1.58579 8.4142C1 7.82844 1 6.8856 1 5C1 3.11438 1 2.17157 1.58579 1.58579C2.17157 1 3.11438 1 5 1C6.8856 1 7.82844 1 8.4142 1.58579C8.80372 1.97528 8.93424 2.52262 8.97796 3.4" stroke-width="0.4" stroke-linecap="round"/></svg><span>Add media</span></div><div class="segment row tooltip" tooltip-pos="right" onclick="open_modal('.gallery__export__modal')"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5.40002 4.60005L8.68002 1.32007" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.99995 2.92V1H7.07996" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M4.59999 1H3.8C1.8 1 1 1.8 1 3.8V6.2C1 8.2 1.8 9 3.8 9H6.19999C8.19999 9 8.99999 8.2 8.99999 6.2V5.4" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Export media</span></div></div><div class="primary" style="max-width: min(80ch, 96%); margin-top: 40px;"><div class="row center gap"><p>Filter type:</p><div class="switch"><span onclick="filterType = 0; reload()" class="active">Match all</span><span onclick="filterType = 1; reload()">Match one</span></div></div><div class="category__list filter__list"><p>Filters:</p><div class="categories__content"><!--JS will generate here--></div></div></div><div class="gallery__items row wrap center"><!--JS will add items here--></div><div class="modal col center gallery__item__options__modal"><div class="modal__content col center primary" style="width: 100%;"><p></p><div class="category__list"><div class="categories__content"><!--JS will generate here--><!--<span class="primary">category <span>X</span></span>--></div><button class="primary" style="width: 4ch; height: 4ch; padding: 0;" onclick="open_modal('.gallery__add__category__modal'); document.querySelector('.gallery__add__category__modal input').focus()">+</button></div><div class="button__panel col"><button class="primary" onclick="window.open(current.src, '_blank')">View source</button><button class="primary" onclick="window.open(current.origin, '_blank')">View origin</button><button class="primary" onclick="copy(current.src)">Copy source</button><button class="primary" onclick="items = items.filter(item => item != current); reload(); warn_unsaved();" data-modal-close>Delete</button><button class="primary" onclick="download_url(current.src, current.name)">Download</button></div></div></div><div class="modal col center gallery__add__category__modal"><div class="modal__content col center primary"><p>Create Category</p><div class="input__bar row"><input type="text" class="primary" list="categories__autocomplete" onkeypress="event.keyCode == 13 ? this.parentNode.querySelector('button')?.click() : null"><datalist id="categories__autocomplete"></datalist><button class="primary" data-modal-close onclick="add_category_to_current(this.parentNode.querySelector('input'))">Add</button></div><br><button class="primary" data-modal-close>Close</button></div></div><div class="modal col center gallery__add__items__modal"><div class="modal__content col center primary" style="width: 100%;"><p>Add media</p><textarea class="primary" placeholder="[Category1;Category2] url"></textarea><br><div class="button__panel col"><button class="primary" onclick="add_items(this.parentNode.parentNode.querySelector('textarea').value)" data-modal-close>Add</button><button class="primary" data-modal-close>Close</button></div></div></div><div class="modal col center gallery__export__modal"><div class="modal__content col center primary" style="width: 100%;"><p>Export</p><div class="button__panel col"><button class="primary" onclick="pb64(); export_page()" data-modal-close>Export as offline mode</button><button class="primary" onclick="export_all_media()" data-modal-close>Export media</button><button class="primary" onclick="download(items_to_enc(), 'sources.txt')" data-modal-close>Export sources</button><button class="primary" onclick="download(items_to_enc(false), 'origins.txt')" data-modal-close>Export origins</button><button class="primary" onclick="let cu = [...items]; items = []; export_page('empty'); items = cu;" data-modal-close>Export empty gallery</button><button class="primary" onclick="export_page()" data-modal-close>Download gallery</button></div></div></div><script> let container = document.querySelector(".gallery__items"); let extensionMappings = {{ video: /(^data:video\\/)|(\\.(mp4|webm|ogg)$)/i, audio: /(^data:audio\\/)|(\\.(mp3|wav)$)/i, img: /(^data:image\\/)|(\\.(jpg|jpeg|png|fig|bpm|svg|gif)$)/i, embed: /(^data:application\\/pdf)|(\\.pdf$)/i, pre: /(^data:text\\/)|(\\.(txt|md|log)$)/i }}; const template = document.documentElement.outerHTML; let items = {items}; let filters = [ "All" ]; let filterType = 0; let categories = []; let current = null; const init_item_metadata = () => {{ items = items.map((item, id) => {{ item = typeof item === "string" ? {{ "src": item }} : item; let name = item.src.split("/").reverse()[0].split("?")[0].split("#")[0].split(";")[0]; name = name + (item.src.startsWith("data:") ? "." + item.src.split(";")[0].split("/")[1] : ""); let type = Object.entries(extensionMappings).find(x => x[1].test(item.src.split("?")[0].split("#")[0])); type = type ? type[0] : "unknown"; let html = type === "audio" || type === "video" ? `<${{type}} class="display" controls src="${{item.src}}"></${{type}}>` : type === "img" ? `<img class="display" src="${{item.src}}" alt="${{name}}"` : type === "embed" ? `<embed class="display" src="${{item.src}}">` : `<a href="${{item.src}}">View data</a>`; return {{ "src": item.src, "origin": item.origin || item.src, "name": item.name || name, "id": id, "categories": item.categories || [ type.replace("img", "image") ], "type": type, "html": html }}; }}); }}; const export_page = (title = document.title) => {{ let newItems = items.map(item => item.origin == item.src ? {{ "src": item.src, "categories": item.categories }} : {{ "src": item.src, "origin": item.origin, "categories": item.categories }} ); let source = template.replace(/let items = \\[\\s*(\\{{[^{{}}]*\\}}\\s*,\\s*)*(\\{{[^{{}}]*\\}})?\\s*\\]/, (match, p1) => `let items = ${{JSON.stringify(newItems)}};`); source = source.replace(`<title>${{document.title}}</title>`, `<title>${{title}}</title>`); download(source, `${{title}}.html`); }}; const add_items = (str) => {{ items = [...str.split("\\n").map(x => {{ let parts = x.split("]"); return parts.length == 2 ? {{ "src": parts[1], "categories": parts[0].replace("[", "").split(";") }} : {{ "src": parts[0] }}; }}), ...items]; reload(); warn_unsaved(); }}; const add_item_to_container = (item) => {{ container.insertAdjacentHTML("beforeend", ` <div class="item col center" data-id="${{item.id}}" onclick="this.classList.toggle('active');"><div class="item__content"><div class="option__buttons row"><button class="primary col center ${{item.categories.includes("Favorites") ? "fav" : ""}}" style="padding-top: 6px;" onclick="this.parentNode.parentNode.parentNode.click(); toggle_favorite(${{item.id}})">✯</button><button class="primary col center" style="padding-bottom: 6px;" onclick="this.parentNode.parentNode.parentNode.click(); open_options_modal(${{item.id}})">...</button></div> ${{item.html}} </div></div>`); }}; const open_options_modal = (itemID) => {{ current = items.find(i => i.id == itemID); let modal = document.querySelector(".gallery__item__options__modal"); modal.querySelector("p").innerHTML = current.name; modal.querySelector(".categories__content").innerHTML = current.categories.map(c => `<span class="primary">${{c}} <span onclick="remove_category('${{c}}')">X</span></span>`).join(""); modal.classList.add("active"); }}; const toggle_favorite = (itemID) => {{ current = items.find(i => i.id == itemID); current.categories.includes("Favorites") ? remove_category("Favorites", false) : add_category_to_current({{ "value": "Favorites" }}, false); container.querySelector(`.item[data-id="${{itemID}}"] button`)?.classList?.toggle("fav"); if (items.filter(x => x.categories.includes("Favorites")).length == 0) document.querySelector(".filter__list .primary").click(); warn_unsaved(); }}; const add_category_to_current = (inp, open = true) => {{ let category = inp.value; if (category == "") return; current.categories = [...new Set([...current.categories, category])]; reload(); if (open) open_options_modal(current.id); inp.value = ""; warn_unsaved(); }}; const remove_category = (c, open = true) => {{ current.categories = current.categories.filter(x => x != c); reload(); if (open) open_options_modal(current.id); warn_unsaved(); }}; const reload_categories = () => {{ categories = [...new Set(items.flatMap(item => item.categories))]; let list = document.querySelector(".filter__list .categories__content"); let elements = ["All", ...(categories.includes("Favorites") ? [ "Favorites" ] : []), ...categories.filter(x => x != "Favorites")]; let hasFav = elements.includes("Favorites"); let useSep = categories.length != 0 && !(categories.length == 1 && categories[0] == "Favorites"); list.innerHTML = elements.map(c => `<button class="primary ${{(hasFav && c == "Favorites" || !hasFav && c == "All") && useSep ? "sep" : ""}}">${{c}}</button>`).join(""); let canReload = false; list.querySelectorAll(".primary").forEach(element => {{ let filter = element.innerHTML; let all = [...element.parentNode.querySelectorAll(".primary")]; let allButton = all.find(x => x.innerHTML == "All"); element.addEventListener("click", () => {{ if (filter == "All") {{ all.forEach(x => x.classList.remove("active")); element.classList.add("active"); }} else {{ allButton?.classList?.remove("active"); element.classList.toggle("active"); }} let active = [...list.querySelectorAll(".primary.active")].map(x => x.innerHTML); filters = active; if (filters.length == 0) allButton?.click(); if (canReload) reload(); }}); }}); filters.map(x => [...list.querySelectorAll(".primary")] .filter(r => r.textContent == x)[0] ).forEach(x => x?.click()); canReload = true; document.querySelector("#categories__autocomplete").innerHTML = categories.map(x => `<option value="${{x}}"></option>`).join(""); }}; let timeouts = []; const reload = async () => {{ let currentSrc = current?.src; items.sort((a, b) => (a.categories?.[0] || "z").toLowerCase().localeCompare((b.categories?.[0] || "z").toLowerCase())); init_item_metadata(); current = items.find(x => x.src == currentSrc); let validItems = items.filter(item => filters.includes("All") ? true : filterType == 0 ? !filters.some(c => !item.categories.includes(c)) : filterType == 1 ? filters.some(c => item.categories.includes(c)) : false ); reload_categories(); let domIds = [...container.querySelectorAll(".item")].map(x => Number(x.dataset.id)); let locIds = validItems.map(x => x.id); let didChange = domIds.length !== locIds.length || domIds.some((v, i) => v !== locIds[i]); if (validItems.length == 0) container.innerHTML = "<p>No items found. <b>Check your filters!</b></p>"; if (!didChange) return; container.innerHTML = ""; timeouts.forEach(clearTimeout); timeouts = []; validItems.forEach((item, i) => timeouts.push(setTimeout(() => add_item_to_container(item), item.src.startsWith("data:") ? i * 100 : (validItems.length > 500 ? i * 50 : 0)))); }}; reload(); document.querySelectorAll(".modal").forEach(modal => {{ modal.addEventListener("click", (event) => {{ if (!(["div"].includes(event.target.nodeName.toLowerCase()) || event.target.hasAttribute("data-modal-close"))) return; modal.classList.remove("active"); }}); }}); const open_modal = (name) => {{ document.querySelector(name)?.classList?.add("active"); }}; document.querySelectorAll(".switch span").forEach(span => span.addEventListener("click", () => {{ span.parentNode.querySelectorAll("span.active").forEach(x => x.classList.remove("active")); span.classList.add("active"); }})); const showNotification = (title, content, color = "red", time = 8000) => {{ document.querySelector(".notification__container").insertAdjacentHTML("beforeend", ` <div class="col primary"><p class="title">${{title}}</p><p class="content">${{content}}</p><div class="bar" style="background: ${{color}};"></div></div> `); let element = document.querySelector(".notification__container div.primary:last-of-type"); if (!element || time == null) return; element.querySelector(".bar").animate([ {{ width: '100%', opacity: 1 }}, {{ width: '0%', opacity: 0 }} ], {{ duration: time, fill: 'forwards' }} ).onfinish = () => element.remove(); }}; let corsProxy = "https://corsproxy.io/?"; const fetch_cors = async (url) => {{ try {{ return (await fetch(url)); }} catch (e) {{ if (url.startsWith(corsProxy)) {{ showNotification("Error", `Error while downloading: ${{e}}`); return null; }} return fetch_cors(corsProxy + url); }} }}; const copy = (text) => {{ navigator.clipboard?.writeText(text) .then(() => showNotification('Success', 'Successfully copied source.', 'green')) .catch((e) => showNotification('Error', 'Something went wrong.')) || showNotification("Error", "Clipboard api not working on HTTP!") }}; const download = (content, filename) => {{ const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([content], {{ type: "text/plain" }})); a.download = filename; document.body.appendChild(a); a.click(); document.body.removeChild(a); }}; const download_url = (url, filename) => {{ fetch_cors(url).then(x => x.blob()).then(x => download(x, filename)); }}; const export_all_media = async () => {{ items.forEach((item, i) => setTimeout(async () => download_url(item.src, `[${{item.categories[0]}}] ${{item.name}}`), i * 500 ) ) }}; const items_to_enc = (src = true) => {{ return items.map(item => {{ let c = item.categories.filter(c => c != item.type).join(";"); let u = src ? item.src : item.origin; return c ? `[${{c}}] ${{u}}` : u; }}).join("\\n"); }}; const asBase64 = async (url) => {{ if (/^data:[a-zA-Z]+\\/[a-zA-Z0-9.-]+;base64,/.test(url)) return url; console.log(`Converting ${{url}}`); try {{ let response = await fetch_cors(url); return `data:${{response.headers.get("content-type")}};base64,` + btoa(new Uint8Array(await response.arrayBuffer()).reduce(function (data, byte) {{ return data + String.fromCharCode(byte); }}, '')); }} catch (error) {{ return null; }}; }}; const pb64 = async () => {{ showNotification("Important", "Compressing media. This might take a while!"); let encoded = await Promise.all(items.map(src => asBase64(src.src))); encoded = encoded.filter(encodedUrl => encodedUrl !== null); items = encoded.map((src, idx) => {{ items[idx].src = src; return items[idx]; }}); }}; let unsaveWarn = false; const warn_unsaved = () => {{ if (unsaveWarn) return; unsaveWarn = true; showNotification("Warning", "You have unsaved changes!<br><br><button class='primary' onclick='export_page(); unsaveWarn = false; this.parentNode.parentNode.remove()'>Save</button><br><button class='primary' onclick='unsaveWarn = false; this.parentNode.parentNode.remove()'>Ignore</button>", "red", null); }}; </script></body></html>""" \
        .format(items=str(items), title=title, bg=background, primary=primary, accent=accent, highlight=highlight, font=font,
                item_width=item_width, item_height=item_height, item_zoom_scale=item_zoom_scale)

def get_content(path: str):
    if path.startswith("http://") or path.startswith("https://"):
        response = requests.get(path, headers={ "User-Agent": "Mozilla/5.0" })
        return response.content if response.status_code == 200 else None
    elif path.startswith("data:"):
        return base64.b64decode(path.split(";base64,")[1])
    else:
        with open(path, "rb") as f:
            return f.read()
        
    return None

def as_b64(path):
    try:
        return f"data:{mimetypes.guess_type(path)[0]};base64,{base64.b64encode(get_content(path)).decode('utf-8')}"
    except:
        return None

def parse_items(items: list) -> list:
    out = []
    for item in items:
        if type(item) == str:
            categories = item.split("] ")[0].removeprefix("[").split(";") if item.__contains__("] ") else []
            src = item.split("] ")[-1]
        else:
            categories = item.get("categories", [])
            src = item.get("src", item.get("url", None))
            if src == None: continue
        
        out.append({ "src": src, "categories": categories })
    return out

def items_to_str(items: list) -> str:
    items = parse_items(items)
    total = ""
    for i, item in enumerate(items):
        x = item.get("src", None)
        if x == None: continue
        if len(item.get("categories", [])) != 0:
            x = f"[{';'.join(item.get('categories'))}] {x}"
        total += x + ("\n" if i != len(items) -1 else "")
    return total
        
def items_from_dir(dir: str) -> list:
    if not os.path.isdir(dir):
        return []
    
    out = []
    for dp, _, fns in os.walk(dir):
        for fn in fns:
            path = dir + "/" + "/".join(f"{dp}/{fn}".split("/")[1:])
            out.append({ "src": path, "categories": path.split("/")[1:-1] })
    
    return out

def name_from_url(url):
    return "/".join(url.split("/")[-1:]).split("?")[0].split("#")[0]

def convert_items_b64(items: list, keep_origin: bool = True) -> list:
    items = parse_items(items)
    for item in items:
        if keep_origin:
            item["origin"] = item["src"]
        item["name"] = name_from_url(item["src"])
        item["src"] = default(as_b64(item["src"]), item["src"])
    return items

def extract_items(source: str) -> list:
    found = re.search(r"let items = \[(.*?)\];", source, re.DOTALL)
    if not found:
        sys.exit("No data could be found!")

    data = eval(found.group().removeprefix("let items = ").removesuffix(";"))
    return parse_items(data)

def export_media(items, dest = "out"):
    items = parse_items(items)
    for i, item in enumerate(items):
        name = name_from_url(item["src"])
        categories = sorted(item["categories"])
        dir = dest + "/" + "/".join(categories)
        os.makedirs(dir, exist_ok=True)

        try:
            content = get_content(item["src"])
            if content != None:
                open(dir + "/" + name, "wb").write(content)
        except Exception as e:
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MKGallery is a utility application for creating galleries out of files.")
    parser.add_argument("--item-width", "-iw", type=str, help="Set the maximal width of an item. (Default: 50ch)", default="50ch")
    parser.add_argument("--item-height", "-ih", type=str, help="Set the maximal height of an item. (Default: 50ch)", default="50ch")
    parser.add_argument("--scale-factor", "-sf", type=str, help="Set the scale factor when maximizing an item. (Default: 2.0)", default="2.0")
    parser.add_argument("--title", "-t", type=str, help="Set the title of the gallery. (Default: New Gallery)", default="New Gallery")
    parser.add_argument("--font", "-f", type=str, help="Set the font.")
    parser.add_argument("--accent", "-a", type=str, help="Set the accent color.")
    parser.add_argument("--background", "-bg", type=str, help="Set the background color.")
    parser.add_argument("--highlight", "-hl", type=str, help="Set the highlight color.")
    parser.add_argument("--primary", "-p", type=str, help="Set the primary color.")
    parser.add_argument("--colorpreset", "-cp", type=str, help="Set a color preset. (See --list-presets; Default: 1)", default="1")
    parser.add_argument("--list-presets", "-lp", action="store_true", help="Get a list of all presets.")
    parser.add_argument("--add-item", "-i", type=str, action="append", help="Specify the path/url to an item you wish to add.", default=[])
    parser.add_argument("--add-url-file", "-auf", type=str, action="append", help="Add a path/url to a file with the items to add. (May be passed multiple times)", default=[])
    parser.add_argument("--add-dir", "-ad", type=str, action="append", help="Add a directory with items. Place in sub-folders to add categories. (May be passed multiple times)", default=[])
    parser.add_argument("--stdin", "-si", action="store_true", help="Use the system stdin as input.")
    parser.add_argument("--no-stdout", "-nso", action="store_true", help="Disable stdout.")
    parser.add_argument("--base64", "-b64", action="store_true", help="Convert all items to base64 for offline access.")
    parser.add_argument("--with-origin", "-wo", action="store_true", help="Keep a reference to the original url of files converted to b64.")
    parser.add_argument("--out", "-o", type=str, help="Set the path to the output file.")
    parser.add_argument("--extract", "-e", type=str, help="Pass a gallery to extract all items of.")
    parser.add_argument("--export-media", "-em", type=str, help="Pass a gallery to export the items of.")

    args = parser.parse_args()

    def default(a, b): return a if a else b

    preset = presets[args.colorpreset]
    settings = dict(
        title = args.title,
        item_width = args.item_width,
        item_height = args.item_height,
        item_zoom_scale = args.scale_factor,
        accent = default(args.accent, preset["accent"]),
        background = default(args.background, preset["background"]),
        highlight = default(args.highlight, preset["highlight"]),
        primary = default(args.primary, preset["primary"]),
        font = default(args.font, preset["font"]),
    )

    def handle(urls):
        source = generate_html(urls, **settings)

        if not args.no_stdout:
            print(source)

        if args.out:
            open(args.out.removesuffix(".html") + ".html", "w").write(source)

    if args.list_presets:
        print("ID \t Background \t Primary \t Accent \t Highlight \t Font")
        for p, c in presets.items():
            print(f"{p} \t {c['background']} \t {c['primary']} \t {c['accent']} \t {c['highlight']} \t {c['font']}")
    
    elif args.extract:
        print(items_to_str(extract_items(get_content(args.extract).decode())))

    elif args.export_media:
        export_media(extract_items(get_content(args.export_media).decode()), args.out if args.out else "./out")

    else:
        items = args.add_item
        
        # Append urls from url file
        for uf in args.add_url_file:
            items += [ line.strip() for line in get_content(uf).decode().split("\n") if line.strip() ]

        # Append std in
        if args.stdin or not sys.stdin.isatty():
            items += [ line.strip() for line in sys.stdin if line.strip() ]
        
        # Append dir
        for dir in args.add_dir:
            items += items_from_dir(dir)

        items = parse_items(items)
        
        # Encode to b64
        if args.base64:
            items = convert_items_b64(items, args.with_origin)

        handle(items)