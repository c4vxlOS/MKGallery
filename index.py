import argparse
import re
import mimetypes
import base64
import requests
import sys
import os

presets = {
    "blue": { "bg": "#1b1b1b", "text": "#ffffff", "primary": "#2e3e4d", "secondary": "#687e92", "font": "system-ui" },
    "green": { "bg": "#18121c", "text": "#ffffff", "primary": "#39534c", "secondary": "#436f42", "font": "system-ui" },
}

def default(a, b): return a if a else b

def generate_html(items: list, title: str, max_width: str, font: str, text: str, background: str, primary: str, secondary: str) -> str:
    return """<!DOCTYPE html><html><head><meta charset='utf-8'><meta http-equiv='X-UA-Compatible' content='IE=edge'><title>{title}</title><meta name='viewport' content='width=device-width, initial-scale=1'><style> .gallery__items {{ display: flex; flex-direction: column; gap: 20px; }} .gallery__items section.active {{ background: var(--bg); position: fixed; top: 0; left: 0; width: 100vw; height: 100dvh; z-index: 9999; display: flex; align-items: center; justify-content: center; }} .gallery__items section .content {{ width: 97vw; max-width: var(--max-width); height: min-content; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 10px; overflow: hidden; cursor: pointer; gap: 2px; background: var(--bg-2); }} .gallery__items section.active .content {{ width: auto; max-width: 140ch; max-height: 90vh; }} .gallery__items section.active .content .display {{ max-height: calc(90vh - 6ch); }} .gallery__items section button {{ width: 100%; border-radius: unset; }} .gallery__items section .content .display {{ width: auto; max-width: 100%; height: auto; user-select: none; -webkit-user-drag: none; }} body.grid__view .gallery__items {{ flex-direction: row; flex-wrap: wrap; justify-content: center; }} body.grid__view .gallery__items section:not(.active) {{ background-color: var(--bg-2); border-radius: 10px; }} body.grid__view .gallery__items section:not(.active) .display {{ object-fit: contain; height: 100%; }} body:not(.list__view) .gallery__items section p, body.list__view .gallery__items section.active p {{ display: none; }} body .gallery__items section p {{ text-overflow: ellipsis; overflow: hidden; flex-grow: 1; white-space: nowrap; }} body.list__view .gallery__items section:not(.active) .content {{ background: var(--primary); flex-direction: row-reverse; justify-content: end; width: 90vw; max-width: 140ch; padding: 0 20px; }} body.list__view .gallery__items section:not(.active) .content button {{ width: max-content; border-radius: 10px; }} body.list__view .gallery__items section:not(.active) .display {{ display: none; }} #item__options__modal p {{ max-width: 90vw; text-align: center; }} </style><style> .tooltip {{ position: relative; }} .tooltip span {{ position: absolute; top: calc(100% + 5px); background: var(--bg-2); color: var(--text); padding: 5px 20px; border-radius: 10px; opacity: 0; text-align: center; display: none; width: max-content; }} .tooltip:hover span {{ opacity: 1; display: unset; }} .tooltip[tooltip-pos="right"] span {{ right: 5px; border-radius: 10px 0px 10px 10px; }} .modal {{ position: fixed; top: 0; width: 100vw; height: 100dvh; background: var(--bg); flex-direction: column; align-items: center; justify-content: center; display: none; }} .modal.active {{ display: flex; z-index: 9999; }} .modal .modal__content {{ display: flex; flex-direction: column; align-items: center; justify-content: center; width: 90vw; max-width: 100ch; }} .option__switcher {{ width: max-content; display: flex; gap: 1px; border-radius: 10px; overflow: hidden; }} .option__switcher span {{ padding: 10px 20px; cursor: pointer; background: var(--primary); color: var(--text); }} .option__switcher span:not(.active):hover {{ opacity: .9; }} .option__switcher span.active {{ background: var(--secondary); }} .primary, .secondary, .input {{ background: var(--primary); color: var(--text); border: none; padding: 8px 20px; border-radius: 13px; border: 1px solid var(--primary); cursor: pointer; outline: none; }} .input {{ background: none; border-radius: 0; border: none; border-bottom: 1px solid var(--primary); padding-left: 5px; }} .secondary {{ background: none; }} .primary:hover, .primary.active, .secondary:hover, .secondary.active {{ background: var(--secondary); }} </style><style> :root {{ --primary: {primary}; --secondary: {secondary}; --text: {text}; --bg: {bg}; --bg-1: hsl(from var(--bg) h s 15%); --bg-2: hsl(from var(--bg) h s 10%); --font: {font}; --max-width: {max_width}; }} ::-webkit-scrollbar {{ height: 2px; width: 2px; }} ::-webkit-scrollbar-thumb {{ background: var(--bg-1); }} body, html {{ width: 100vw; background: var(--bg); margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow-x: hidden; }} * {{ transition: .2s; font-family: var(--font); box-sizing: border-box; user-select: none; }} label, p, h1, span, textarea::placeholder {{ color: var(--text); }} h1 {{ font-weight: 100; }} .row, .flow-right {{ display: flex; align-items: center; justify-content: center; gap: 15px; }} .flow-right {{ width: max-content; flex-direction: column; align-items: end; }} .options__bar {{ width: max-content; gap: 10px; position: fixed; padding-right: 10px; top: 10px; right: 10px; }} .options__bar .segment {{ width: 5ch; height: 5ch; background: var(--bg-2); padding: 8px; border-radius: 10px; cursor: pointer; }} .options__bar .segment span {{ white-space: nowrap; }} .options__bar .segment svg {{ height: 100%; width: 100%; stroke: var(--text); }} .options__bar:hover .segment:not(:hover) {{ background: var(--bg-1); }} .filters__list {{ display: flex; gap: 15px; max-width: 100%; overflow-y: scroll; padding-bottom: 5px; }} .filters__list span {{ background: var(--primary); padding: 4px 10px; border-radius: 10px; cursor: pointer; color: var(--text); height: max-content; white-space: nowrap; }} .filters__list span.active {{ background: var(--secondary); }} #export__modal .modal__content {{ border-radius: 10px; overflow: hidden; gap: 1px; }} #export__modal .modal__content button {{ width: 100%; border-radius: 0; }} .filter__panel {{ width: 98vw; max-width: 90ch; border: 1px solid var(--text); padding: 20px; border-radius: 10px; margin: 20px 0; }} .rounded__container {{ overflow: hidden; border-radius: 10px; width: 100%; display: flex; flex-direction: column; gap: 1px; }} .rounded__container * {{ width: 100%; border-radius: 0; }} </style><style> .notifications {{ position: fixed; top: 0; right: 0; width: 30ch; z-index: 999999; padding: 10px; display: flex; flex-direction: column; gap: 10px; overflow-y: scroll; }} .notifications section {{ position: relative; background-color: var(--bg-1); max-width: 100%; padding: 10px 15px; border-radius: 10px; padding-bottom: 25px; }} .notifications section p {{ font-size: 130%; margin: 3px 0; }} .notifications section .progress {{ position: absolute; content: ""; bottom: 0px; left: 0; height: 4px; width: 100%; }} </style></head><body><div class="notifications"></div><div class="options__bar row" id="options__bar"><div class="segment row tooltip" onclick="document.querySelector('#add__media__modal').classList.toggle('active')"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.19999 4.99999H4.99999M4.99999 4.99999H3.79999M4.99999 4.99999V3.79999M4.99999 4.99999V6.19999" stroke-width="0.4" stroke-linecap="round"/><path d="M9 5C9 6.8856 9 7.82844 8.4142 8.4142C7.82844 9 6.8856 9 5 9C3.11438 9 2.17157 9 1.58579 8.4142C1 7.82844 1 6.8856 1 5C1 3.11438 1 2.17157 1.58579 1.58579C2.17157 1 3.11438 1 5 1C6.8856 1 7.82844 1 8.4142 1.58579C8.80372 1.97528 8.93424 2.52262 8.97796 3.4" stroke-width="0.4" stroke-linecap="round"/></svg><span>Add media</span></div><div class="segment row tooltip" onclick="document.querySelector('#settings__modal').classList.toggle('active')"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.78393 3.69449L8.62856 3.60805C8.60446 3.59463 8.59258 3.58789 8.58091 3.58091C8.46504 3.51151 8.36741 3.41561 8.29613 3.30088C8.28896 3.28934 8.28221 3.27723 8.26838 3.25331C8.25459 3.22941 8.24759 3.2173 8.24114 3.20531C8.17725 3.08595 8.14267 2.95293 8.14059 2.81755C8.14038 2.80394 8.14042 2.79003 8.14089 2.76238L8.14394 2.58195C8.14878 2.29321 8.15124 2.1484 8.11063 2.01843C8.07461 1.90299 8.01432 1.79666 7.93379 1.70643C7.84278 1.60443 7.71677 1.53166 7.46453 1.38631L7.25502 1.26557C7.0035 1.12063 6.8777 1.04813 6.74414 1.02049C6.62602 0.996042 6.50408 0.997175 6.38638 1.0236C6.2535 1.05343 6.12926 1.12781 5.88097 1.2765L5.87953 1.27718L5.72942 1.36707C5.7057 1.38128 5.69369 1.38844 5.68177 1.39506C5.56369 1.4607 5.43191 1.497 5.29686 1.50134C5.28328 1.50177 5.26941 1.50177 5.24174 1.50177C5.21425 1.50177 5.19978 1.50177 5.18621 1.50134C5.0509 1.49698 4.91882 1.46049 4.80057 1.39457C4.78865 1.38793 4.77686 1.38071 4.7531 1.36643L4.60201 1.27573C4.35198 1.12563 4.22679 1.05046 4.09319 1.02049C3.975 0.993976 3.85267 0.993242 3.73409 1.01801C3.60021 1.04597 3.47437 1.11901 3.22269 1.26508L3.22157 1.26557L3.01466 1.38566L3.01237 1.38706C2.76296 1.53182 2.63795 1.60437 2.5477 1.70596C2.46762 1.7961 2.40775 1.90226 2.37192 2.0174C2.33142 2.14754 2.33358 2.29267 2.33846 2.58277L2.34149 2.76294C2.34195 2.79022 2.34275 2.80378 2.34255 2.8172C2.34054 2.95287 2.3055 3.08616 2.24139 3.20573C2.23505 3.21755 2.22822 3.22938 2.21457 3.253C2.20092 3.27664 2.1943 3.28839 2.18723 3.2998C2.11564 3.41514 2.01753 3.51159 1.90094 3.58112C1.8894 3.588 1.87725 3.59461 1.85337 3.60784L1.69996 3.69286C1.44472 3.8343 1.31714 3.90508 1.2243 4.00581C1.14217 4.09493 1.08012 4.20061 1.04225 4.31576C0.999441 4.44589 0.999475 4.5918 1.00014 4.88358L1.00068 5.12211C1.00134 5.41194 1.00224 5.55679 1.04515 5.68603C1.08311 5.80037 1.1447 5.90547 1.22637 5.99402C1.31869 6.09415 1.445 6.1645 1.6983 6.3054L1.85034 6.39C1.87622 6.40439 1.88924 6.41147 1.90172 6.41902C2.01725 6.48857 2.11459 6.58475 2.18557 6.69944C2.19323 6.71182 2.2006 6.72468 2.21532 6.75043C2.22985 6.77581 2.23729 6.78849 2.24402 6.80122C2.30625 6.91904 2.33957 7.04998 2.34184 7.1832C2.34208 7.19759 2.34187 7.21214 2.34138 7.24142L2.33846 7.41431C2.33355 7.70542 2.3314 7.85111 2.37214 7.98162C2.40819 8.09707 2.46842 8.2034 2.54895 8.29364C2.63996 8.39564 2.76615 8.46836 3.01839 8.61372L3.22787 8.73439C3.4794 8.87937 3.60513 8.95175 3.73867 8.97942C3.85681 9.00385 3.97879 9.00292 4.09651 8.97649C4.22956 8.94662 4.35422 8.87199 4.60324 8.72285L4.75335 8.63299C4.77711 8.61873 4.78916 8.6116 4.80104 8.60498C4.91912 8.53935 5.05077 8.50286 5.18582 8.49853C5.1994 8.49811 5.21328 8.49811 5.24094 8.49811C5.26869 8.49811 5.28252 8.49811 5.29614 8.49853C5.43144 8.5029 5.56395 8.53952 5.6822 8.60541C5.69259 8.61122 5.70303 8.6175 5.72131 8.62849L5.88093 8.72429C6.13096 8.87441 6.25591 8.94933 6.38952 8.97933C6.50768 9.00585 6.63013 9.00691 6.74872 8.98217C6.88254 8.95421 7.00864 8.88102 7.2602 8.73503L7.47022 8.61313C7.71978 8.46828 7.8449 8.39564 7.93519 8.29403C8.0153 8.20391 8.07525 8.09779 8.11106 7.98264C8.15128 7.85345 8.14886 7.70945 8.14403 7.42352L8.14089 7.23705C8.14042 7.20976 8.14038 7.19619 8.14059 7.18278C8.14258 7.04709 8.17703 6.91374 8.24114 6.79418C8.24751 6.78234 8.25438 6.77042 8.26796 6.74687C8.28162 6.72328 8.28871 6.71148 8.29579 6.70007C8.36737 6.58471 8.46555 6.48818 8.58218 6.41864C8.59355 6.41185 8.60531 6.40536 8.6286 6.39246L8.62941 6.39208L8.78279 6.30706C9.03804 6.16564 9.16587 6.09474 9.25871 5.99402C9.34085 5.90492 9.40279 5.79936 9.44068 5.68425C9.48324 5.55488 9.4829 5.40982 9.48226 5.12143L9.48171 4.87781C9.48103 4.58794 9.48069 4.44313 9.4378 4.31389C9.39982 4.19955 9.33788 4.09446 9.2562 4.00588C9.16401 3.90586 9.03748 3.83549 8.7847 3.69485L8.78393 3.69449Z" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M3.54419 5.00001C3.54419 5.9373 4.30402 6.69715 5.24132 6.69715C6.17865 6.69715 6.93846 5.9373 6.93846 5.00001C6.93846 4.06269 6.17865 3.30286 5.24132 3.30286C4.30402 3.30286 3.54419 4.06269 3.54419 5.00001Z" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Settings</span></div><div class="segment row tooltip" tooltip-pos="right" onclick="document.querySelector('#export__modal').classList.toggle('active')"><svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5.40002 4.60005L8.68002 1.32007" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.99995 2.92V1H7.07996" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M4.59999 1H3.8C1.8 1 1 1.8 1 3.8V6.2C1 8.2 1.8 9 3.8 9H6.19999C8.19999 9 8.99999 8.2 8.99999 6.2V5.4" stroke-width="0.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Export media</span></div></div><br><br><br><div class="filter__panel" id="filter__panel"><div class="row"><label>Filter type:</label><div class="option__switcher"><span style="font-size: small;" onclick="filterType=0; reload();" class="active">MATCH ALL</span><span style="font-size: small;" onclick="filterType=1; reload();">MATCH ONE</span></div></div><br><div class="row"><p>Filters:</p><div class="filters__list"><span class="active">All</span></div></div></div><div class="gallery__items"><!--Script will generate here--></div><div class="modal" id="export__modal"><div class="modal__content"><button class="primary" onclick="(async () => {{ await packageB64(); exportPage(); }})()">Export as offline mode</button><button class="primary" onclick="downloadMedia()">Export media</button><button class="primary" onclick="download(items.map(x => `[${{x.categories.join(';')}}] ${{x.url}}`).join('\\n'), 'sources.txt')">Export sources</button><button class="primary" onclick="download(items.map(x => `[${{x.categories.join(';')}}] ${{x.origin}}`).join('\\n'), 'origins.txt')">Export origins</button><button class="primary" onclick="let itemB = [...items]; items = []; exportPage('New Gallery'); items = itemB;">Export new empty gallery</button><button class="primary" onclick="exportPage()">Download this gallery</button></div></div><div class="modal" id="item__options__modal"><div class="modal__content"><p style="position: absolute; top: 10px;">Some filename</p><div class="row filter__panel" style="padding: 2px 15px;"><p>Filters:</p><div class="filters__list"><span onclick="document.querySelector('#create__category__modal').classList.add('active')">+</span></div></div><div class="rounded__container" style="max-width: 90ch;"><button class="primary" onclick="window.open(current.url, '_blank').focus()">View source</button><button class="primary" onclick="window.open(current.origin, '_blank').focus()">View origin</button><button class="primary" onclick="copy(current.url)">Copy source</button><button class="primary" onclick="downloadURL(current.url, current.filename)">Download</button><button class="primary" onclick="items = items.filter(x => x != current); this.parentNode.parentNode.parentNode.click(); reload(); warnUnsavedChanges()">Delete</button></div></div></div><div class="modal" id="create__category__modal" no-click><div class="modal__content"><h1>Create Filter</h1><input type="text" class="input" placeholder="Filter name"><br><br><div class="row"><button class="primary" onclick="this.parentNode.querySelector('.secondary').click(); createCategory(this.parentNode.parentNode.querySelector('input').value)">Create</button><button class="secondary" onclick="this.parentNode.parentNode.parentNode.classList.remove('active')">Close</button></div></div></div><div class="modal" id="add__media__modal" no-click><div class="modal__content"><h1>Add media</h1><textarea name="" id="" class="primary" style="width: 90%; height: 50vh; max-height: 60ch;" placeholder="Place your urls: [Category1;Category2;...] https://url1/ ..."></textarea><br><br><div class="row"><button class="primary" onclick="this.parentNode.querySelector('.secondary').click(); addURLs(this.parentNode.parentNode.querySelector('textarea').value)">Add</button><button class="secondary" onclick="this.parentNode.parentNode.parentNode.classList.remove('active')">Close</button></div></div></div><div class="modal" id="settings__modal"><div class="modal__content flow-right"><div class="row"><label>Grid view:</label><div class="option__switcher"><span onclick="document.body.classList.remove('grid__view')" class="active">Off</span><span onclick="document.body.classList.add('grid__view')">On</span></div></div><div class="row"><label>List view:</label><div class="option__switcher"><span onclick="document.body.classList.remove('list__view')" class="active">Off</span><span onclick="document.body.classList.add('list__view')">On</span></div></div></div></div><script> document.querySelectorAll(".modal:not([no-click])").forEach(modal => modal.addEventListener("click", (event) => {{ if (event.target == modal) modal.classList.remove("active"); }}) ); document.querySelectorAll(".toggle__button").forEach(button => button.addEventListener("click", () => button.classList.toggle("active")) ); document.querySelectorAll(".option__switcher span").forEach(element => element.addEventListener("click", () => {{ element.parentNode.querySelectorAll('span').forEach(x => x.classList.remove("active")); element.classList.add("active"); }}) ); document.querySelectorAll("input, textarea").forEach(x => x.addEventListener("focus", () => x.select())); let hasUnsavedWarning = false; const warnUnsavedChanges = () => {{ if (hasUnsavedWarning) return; hasUnsavedWarning = true; showNotification("Warning", `Unsaved changes!<br><br><div class="row"><button class='secondary' onclick="hasUnsavedWarning=false; exportPage()">Save</button><button class='secondary' onclick="hasUnsavedWarning=false; this.parentNode.parentNode.parentNode.remove()">Discard</button></div> `, "#1b9a9e", 999999999999); }}; let corsProxy = "https://corsproxy.io/?"; const getURLData = async (url) => {{ try {{ return (await fetch(url)); }} catch {{ if (url.startsWith(corsProxy)) {{ showNotification("Error", `Error while downloading: ${{e}}`); return null; }}; return getURLData(corsProxy + url); }};}}; const asBase64 = async (url) => {{ if (/^data:[a-zA-Z]+\\/[a-zA-Z0-9.-]+;base64,/.test(url)) return url; console.log(`Converting ${{url}}`); try {{ let response = await getURLData(url); return `data:${{response.headers.get("content-type")}};base64,` + btoa(new Uint8Array(await response.arrayBuffer()).reduce(function (data, byte) {{ return data + String.fromCharCode(byte); }}, '')); }} catch (error) {{ return null; }}; }}; const showNotification = async (title, content, color = "red", time=8000) => {{ document.querySelector(".notifications").insertAdjacentHTML("beforeEnd", ` <section><p>${{title}}</p><span>${{content}}</span><div class="progress" style="background: ${{color}};"></div></section> `); let element = document.querySelector(".notifications section:last-of-type"); element.querySelector(".progress").animate([ {{ width: '100%', opacity: 1 }}, {{ width: '0%', opacity: 0 }} ], {{ duration: time, fill: 'forwards' }} ).onfinish = () => element.remove(); }}; const copy = (text) => {{ navigator.clipboard?.writeText(text) .then(() => showNotification('Success', 'Successfully copied source.', 'green')) .catch((e) => showNotification('Error', 'Something went wrong.')) || showNotification("Error", "Clipboard api not working on HTTP!") }}; const download = (content, filename) => {{ const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([content], {{ type: "text/plain" }})); a.download = filename; document.body.appendChild(a); a.click(); document.body.removeChild(a); }}; const downloadURL = (url, filename) => {{ getURLData(url).then(x => x.blob()).then(x => download(x, filename)); }}; const downloadMedia = async () => {{ items.forEach((item, i) => setTimeout(async () => downloadURL(item.url, `[${{item.categories[0]}}] ${{item.filename}}`), i * 500 ) ) }}; let items = {items}; const template = document.documentElement.outerHTML; let filters = [ "all" ]; let filterType = 0; let current = null; let categories; const loadItemsMetadata = () => {{ items = items.map(item => {{ item = typeof item === "string" ? {{ "url": item }} : item; let filename = item.url.split("/").reverse()[0].split("?")[0].split("#")[0].split(";")[0]; let filetype = item.url.startsWith("data:") ? item.url.split(";")[0].split("/")[1] : filename.split(".").reverse()[0]; let type = [ "mp4", "avi", "mkv", "mov", "flv", "webm", "wmv" ].includes(filetype) ? "video" : [ "png", "jpg", "jpeg", "gif", "webp" ].includes(filetype) ? "image" : "unknown"; return {{ "url": item.url, "origin": item.origin || item.url, "filename": item.filename || filename, "filetype": item.filetype || filetype, "categories": item.categories || [ type ], "type": type }}; }}); items = items.map(item => {{ item.id = items.indexOf(item); return item; }}); }}; const createCategory = (name) => {{ categories.push(name.toLowerCase()); current.categories.push(name.toLowerCase()); loadCategories(); warnUnsavedChanges(); }}; const exportPage = (title = document.title) => {{ let newItems = items.map(item => item.origin == item.url ? {{ "url": item.url, "categories": item.categories }} : {{ "url": item.url, "origin": item.origin, "filename": item.filename, "categories": item.categories }}); let source = template.replace(/let items = \\[\\s*(\\{{[^{{}}]*\\}}\\s*,\\s*)*(\\{{[^{{}}]*\\}})?\\s*\\]/, (match, p1) => `let items = ${{JSON.stringify(newItems)}};`); source = source.replace(`<title>{title}</title>`, `<title>{title}</title>`); download(source, `${{title}}.html`); }}; const addURLs = (urls) => {{ urls.split("\\n").map(url => url.startsWith("[") ? {{ "url": url.split("]")[1], "categories": url.split("]")[0].replace("[", "").split(";") }} : {{ "url": url }}) .forEach(x => items.push(x)); reload(); loadCategories(); warnUnsavedChanges(); }}; const loadCategories = () => {{ categories = categories || [...new Set(items.flatMap(x => x.categories))]; [...document.querySelectorAll(".filters__list span")].filter(x => !["all", "+"].includes(x.innerHTML.toLowerCase())).forEach(x => x.remove()); document.querySelectorAll(".filters__list").forEach(list => list.innerHTML += categories.map(c => `<span>${{c.toUpperCase()}}</span>`).join("\\n") ); document.querySelectorAll(".filters__list span").forEach(element => {{ let filter = element.innerHTML.toLowerCase(); let all = [...element.parentNode.querySelectorAll("span")]; let allButton = all.find(x => x.innerHTML.toLowerCase() == "all"); element.addEventListener("click", () => {{ if (filter == "all") {{ all.forEach(x => x.classList.remove("active")); element.classList.add("active"); }} else {{ allButton?.classList.remove("active"); element.classList.toggle("active"); }}; let aFilters = [...element.parentNode.querySelectorAll("span.active")].map(x => x.innerHTML.toLowerCase()).filter(x => x != "+"); if (element.parentNode.parentNode.parentNode.id == "filter__panel") {{ filters = aFilters; if (filters.length == 0) allButton?.click(); }} else {{ current.categories = aFilters; }}; reload(); }}); }}); }}; const openItemOptions = (id) => {{ current = items[id]; document.querySelector("#item__options__modal p").innerHTML = current.filename; document.querySelectorAll("#item__options__modal .filters__list span").forEach(element => current.categories.includes(element.innerHTML.toLowerCase()) ? element.classList.add("active") : element.classList.remove("active") ); document.querySelector("#item__options__modal").classList.add("active"); }}; const packageB64 = async () => {{ showNotification("Important", "Compressing media. This might take a while!"); let encoded = await Promise.all(items.map(url => asBase64(url.url))); encoded = encoded.filter(encodedUrl => encodedUrl !== null); items = encoded.map((url, idx) => {{ items[idx].url = url; return items[idx]; }}); }}; const displayItem = (item) => {{ document.querySelector(".gallery__items").insertAdjacentHTML("beforeend", ` <section onclick="this.classList.toggle('active');" oncontextmenu="event.preventDefault(); this.querySelector('button').click()" id="${{item.id}}"><div class="content"><button class="primary" onclick="this.parentNode.parentNode.click(); openItemOptions('${{item.id}}')">Options</button> ${{ item.type == "video" ? `<video src="${{item.url}}" class="display" loop controls></video>` : item.type == "image" ? `<img src="${{item.url}}" class="display" alt="${{item.filename}}">` : "<br><span>Filetype not supported!</span><br>" }}<p>${{item.filename}}</p></div></section>`); }}; let timeouts = []; const reload = async () => {{ timeouts.forEach(clearTimeout); timeouts = []; document.querySelector(".gallery__items").innerHTML = ""; categories = [...new Set(items.flatMap(x => x.categories))]; loadItemsMetadata(); let validItems = items.filter(item => filters.includes("all") || (filterType == 0 ? !filters.map(c => item.categories.includes(c)).includes(false) : filterType == 1 ? item.categories.some(c => filters.includes(c)) : false)); validItems.forEach((item, i) => {{ timeouts.push(setTimeout(() => displayItem(item), i * 100)); }}); if (validItems.length == 0) {{ document.querySelector(".gallery__items").innerHTML = "<p>No items found. <b>Check your filters!</b></p>"; }};}}; loadItemsMetadata(); loadCategories(); reload(); </script></body></html>""".format(bg=background, primary=primary, secondary=secondary, text=text, title=title, font=font, max_width=max_width, items=str(items))

def parse_urls(urls: list[str]) -> list[dict]:
    return [ 
        ({ "url": u.split("] ")[1], "categories": u.split("] ")[0].removeprefix("[").split(";") } if u.startswith("[") else { "url": u }) if type(u) == str
        else u for u in urls ]

def extract_data(file):
    found = re.search(r"let items = \[(.*?)\];", open(file, "r").read(), re.DOTALL)
    if found:
        data = eval(found.group().removeprefix("let items = ").removesuffix(";"))
        for i, d in enumerate(data):
            if type(d) is dict:
                if "categories" in d.keys():
                    continue
                d = d["url"]
            
            t = mimetypes.guess_type(d)[0]
            if t.startswith("video/"):
                t = "video"
            elif t.startswith("image/"):
                t = "image"
            else: t = "unknown"
            data[i] = { "url": d, "categories": [ t ] }
        return data
    else: sys.exit("Error. Not a valid gallery.")

def get_item_content(path):
    if path.startswith("http://") or path.startswith("https://"):
        response = requests.get(path, headers={ "User-Agent": "Mozilla/5.0" })
        return response.content if response.status_code == 200 else None
    elif path.startswith("data:"):
        return base64.b64decode(path.split(";base64,")[1])
    else:
        with open(path, "rb") as file: return file.read()

def as_base64(path):
    try:
        return f"data:{mimetypes.guess_type(path)[0]};base64,{base64.b64encode(get_item_content(path)).decode('utf-8')}"
    except:
        return None

def export_media(data, dest):
    for i, d in enumerate(data):
        url = d
        src = d
        if type(d) is dict:
            url = d["url"]
            if "src" in d:
                src = d["src"]
            else:
                src = url

        name = src.split("/")[-1:][0].split("?")[0] if not src.startswith("data:") else str(i) + "." + src.split(";")[0].split("/")[1]
        categories = sorted(default(d["categories"], []))
        dir = dest + "/" + "/".join(categories)
        os.makedirs(dir, exist_ok=True)

        # Download
        print(f"Downloading {url}...")
        try:
            open(dir + "/" + name, "wb").write(get_item_content(url))
        except:
            return

def end(urls, args):
    source = generate_html(urls, **settings)

    if not args.no_stdout:
        print(source)

    if args.output:
        open(args.output.removesuffix(".html") + ".html", "w").write(source)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MKGallery is a utility application for creating galleries out of files.")
    parser.add_argument("--max-width", "-mw", type=str, help="Set the maximal width of an item in the gallery. (Default: 50ch)")
    parser.add_argument("--title", "-t", type=str, help="Set the title of the gallery. (Default: 'New Gallery')")
    parser.add_argument("--font", "-f", type=str, help="Set the font of the gallery. (Default: system)")
    parser.add_argument("--text", "-tx", type=str, help="Set the text color. (Default: #ffffff)")
    parser.add_argument("--background", "-bg", type=str, help="Set the background color.")
    parser.add_argument("--primary", "-pr", type=str, help="Set the primary color.")
    parser.add_argument("--secondary", "-sc", type=str, help="Set the secondary color.")
    parser.add_argument("--output", "-o", type=str, help="Set the output file.")
    parser.add_argument("--preset", "-p", type=str, help="Set a color preset.")
    parser.add_argument("--add-url", "-au", type=str, action="append", help="Specify a url to add to the gallery. (Format: '[category1;category2] https://link/')")
    parser.add_argument("--urls-file", "-uf", type=str, help="Specify a file of urls. (File needs to contain the same format as in the --urls parameter.)")
    parser.add_argument("--list-presets", "-lp", action="store_true", help="Returns a list of all color presets.")
    parser.add_argument("--extract", "-e", type=str, help="Returns a list of all items in a gallery.")
    parser.add_argument("--export-media", "-em", type=str, help="Export all media into a directory. (Pass the gallery)")
    parser.add_argument("--export-out", "-eo", type=str, help="Set the destination directory, where to export media to (Default: ./extracted).")
    parser.add_argument("--dir", "-d", type=str, help="Create a gallery out of the items in a folder. (Use sub-dirs to add categories)")
    parser.add_argument("--base64", "-b64", action="store_true", help="Store all items in base64 format, for offline access.")
    parser.add_argument("--base-only", "-bo", action="store_true", help="Export a gallery with no items.")
    parser.add_argument("--no-origin", "-nor", action="store_true", help="When used in combination with '--base64', only the b64 will be stored (not the origins).")
    parser.add_argument("--no-stdout", "-no", action="store_true", help="When specified, the generated source won't be printed out.")
    args = parser.parse_args()

    preset = presets[default(args.preset, "blue")]
    settings = dict(
        title = default(args.title, "New Gallery"),
        max_width = default(args.max_width, "50ch"),
        font = default(args.font, preset['font']),
        text = default(args.text, preset['text']),
        background = default(args.background, preset['bg']),
        primary = default(args.primary, preset['primary']),
        secondary = default(args.secondary, preset['secondary'])
    )

    if args.list_presets:
        print("Name \t Text \t\t Background \t Primary \t Secondary \t Font\n")
        for p, c in presets.items():
            print(f"{p} \t {c['text']} \t {c['bg']} \t {c['primary']} \t {c['secondary']} \t {c['font']}")

    elif args.extract:
        for item in extract_data(args.extract):
            print(f"[{';'.join(item['categories'])}] {item['url']}")
    
    elif args.export_media:
        export_media(extract_data(args.export_media), default(args.export_out, "./extracted"))

    elif args.base_only:
        end([], args)

    else:
        # Get passed urls
        urls = default(args.add_url, [])

        # Get urls from directory
        if args.dir:
            for dp, _, fns in os.walk(args.dir):
                for fn in fns:
                    if not any(fn.endswith(f".{s}") for s in [ "mp4", "avi", "mkv", "mov", "flv", "webm", "wmv", "png", "jpg", "jpeg", "gif", "webp" ]):
                        continue
                    
                    path = args.dir + "/".join(f"{dp}/{fn}".split("/")[1:])
                    urls.append({ "url": path, "categories": path.split("/")[:-1] })
        
        # Get from url file
        elif args.urls_file:
            urls = [ line.strip() for line in open(args.urls_file, "r").readlines() ]

        # Get urls from stdinput
        elif len(urls) == 0:
            urls = [ line.strip() for line in sys.stdin if line.strip() ]
        
        urls = parse_urls(urls)

        # Convert to b64
        if args.base64:
            for url in urls:
                if not args.no_origin:
                    url["origin"] = url["url"]
                url["url"] = default(as_base64(url["url"]), url["url"])
        
        end(urls, args)