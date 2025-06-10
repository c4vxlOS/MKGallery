let container = document.querySelector(".gallery__items");
let extensionMappings = {
    video: /(^data:video\/)|(\.(mp4|webm|ogg)$)/i,
    audio: /(^data:audio\/)|(\.(mp3|wav)$)/i,
    img: /(^data:image\/)|(\.(jpg|jpeg|png|fig|bpm|svg|gif)$)/i,
    embed: /(^data:application\/pdf)|(\.pdf$)/i,
    pre: /(^data:text\/)|(\.(txt|md|log)$)/i
};
const template = document.documentElement.outerHTML;

let items = [];

let filters = [ "All" ];
let filterType = 0;
let categories = [];
let current = null;

const init_item_metadata = () => {
    items = items.map((item, id) => {
        item = typeof item === "string" ? { "src": item } : item;

        let name = item.src.split("/").reverse()[0].split("?")[0].split("#")[0].split(";")[0];
        name = name + (item.src.startsWith("data:") ? "." + item.src.split(";")[0].split("/")[1] : "");
        let type = Object.entries(extensionMappings).find(x => x[1].test(item.src.split("?")[0].split("#")[0]));
        type = type ? type[0] : "unknown";
        let html = type === "audio" || type === "video" ? `<${type} class="display" controls src="${item.src}"></${type}>` :
                     type === "img" ? `<img class="display" src="${item.src}" alt="${name}"` :
                     type === "embed" ? `<embed class="display" src="${item.src}">` :
                     `<a href="${item.src}">View data</a>`;
        
        return {
            "src": item.src, "origin": item.origin || item.src,
            "name": item.name || name, "id": id,
            "categories": item.categories || [ type.replace("img", "image") ], "type": type, "html": html
        };
    });
}

const export_page = (title = document.title) => {
    let newItems = items.map(item =>
        item.origin == item.src ? { "src": item.src, "categories": item.categories } : { "src": item.src, "origin": item.origin, "categories": item.categories }
    );
    let source = template.replace(/let items = \[\s*(\{[^{}]*\}\s*,\s*)*(\{[^{}]*\})?\s*\]/, (match, p1) => `let items = ${JSON.stringify(newItems)};`);
    source = source.replace(`<title>${document.title}</title>`, `<title>${title}</title>`);
    download(source, `${title}.html`);
}

const add_items = (str) => {
    items = [...str.split("\n").map(x =>  {
        let parts = x.split("]");
        return parts.length == 2 ? { "src": parts[1], "categories": parts[0].replace("[", "").split(";") } : { "src": parts[0] };
    }), ...items];
    reload();
    warn_unsaved();
}

const add_item_to_container = (item) => {
    container.insertAdjacentHTML("beforeend", `
        <div class="item col center" data-id="${item.id}" onclick="this.classList.toggle('active');">
            <div class="item__content">
                <div class="option__buttons row">
                    <button class="primary col center ${item.categories.includes("Favorites") ? "fav" : ""}" style="padding-top: 6px;" onclick="this.parentNode.parentNode.parentNode.click(); toggle_favorite(${item.id})">✯</button>
                    <button class="primary col center" style="padding-bottom: 6px;" onclick="this.parentNode.parentNode.parentNode.click(); open_options_modal(${item.id})">...</button>
                </div>
                ${item.html}
            </div>
        </div>`);
}

const open_options_modal = (itemID) => {
    current = items.find(i => i.id == itemID);

    let modal = document.querySelector(".gallery__item__options__modal");
    modal.querySelector("p").innerHTML = current.name;
    modal.querySelector(".categories__content").innerHTML = current.categories.map(c => `<span class="primary">${c} <span onclick="remove_category('${c}')">X</span></span>`).join("");

    modal.classList.add("active");
}

const toggle_favorite = (itemID) => {
    current = items.find(i => i.id == itemID);
    current.categories.includes("Favorites") ? remove_category("Favorites", false) : add_category_to_current({ "value": "Favorites" }, false);
    container.querySelector(`.item[data-id="${itemID}"] button`)?.classList?.toggle("fav");

    // Switch to "All" category if last item was unfavorited
    if (items.filter(x => x.categories.includes("Favorites")).length == 0)
        document.querySelector(".filter__list .primary").click();

    warn_unsaved();
}

const add_category_to_current = (inp, open = true) => {
    let category = inp.value;
    if (category == "") return;

    current.categories = [...new Set([...current.categories, category])];

    reload();
    if (open) open_options_modal(current.id);
    inp.value = "";
    warn_unsaved();
}

const remove_category = (c, open = true) => {
    current.categories = current.categories.filter(x => x != c);
    
    reload();
    if (open) open_options_modal(current.id);
    warn_unsaved();
}

const reload_categories = () => {
    categories = [...new Set(items.flatMap(item => item.categories))];

    // Create filter buttons
    let list = document.querySelector(".filter__list .categories__content");
    let elements = ["All", ...(categories.includes("Favorites") ? [ "Favorites" ] : []), ...categories.filter(x => x != "Favorites")];
    let hasFav = elements.includes("Favorites");
    let useSep = categories.length != 0 && !(categories.length == 1 && categories[0] == "Favorites");
    list.innerHTML = elements.map(c => `<button class="primary ${(hasFav && c == "Favorites" || !hasFav && c == "All") && useSep ? "sep" : ""}">${c}</button>`).join("");

    // Create logic
    let canReload = false;
    list.querySelectorAll(".primary").forEach(element => {
        let filter = element.innerHTML;
        let all = [...element.parentNode.querySelectorAll(".primary")];
        let allButton = all.find(x => x.innerHTML == "All");

        element.addEventListener("click", () => {
            if (filter == "All") {
                all.forEach(x => x.classList.remove("active"));
                element.classList.add("active");
            } else {
                allButton?.classList?.remove("active");
                element.classList.toggle("active");
            }

            let active = [...list.querySelectorAll(".primary.active")].map(x => x.innerHTML);
            filters = active;

            if (filters.length == 0) allButton?.click();
            if (canReload) reload();
        });
    });

    // Highlight currently active filters
    filters.map(x => 
        [...list.querySelectorAll(".primary")]
            .filter(r => r.textContent == x)[0]
        ).forEach(x => x?.click());
    canReload = true;

    // Update category suggestions
    document.querySelector("#categories__autocomplete").innerHTML = categories.map(x => `<option value="${x}"></option>`).join("");
}

let timeouts = [];
const reload = async () => {
    let currentSrc = current?.src;

    // Sort items by first category
    items.sort((a, b) => (a.categories?.[0] || "z").toLowerCase().localeCompare((b.categories?.[0] || "z").toLowerCase()));
    init_item_metadata();

    current = items.find(x => x.src == currentSrc);

    // Filter items
    let validItems = items.filter(item =>
        filters.includes("All") ? true :                                     // Accept all items
        filterType == 0 ? !filters.some(c => !item.categories.includes(c)) : // Must match all filters
        filterType == 1 ? filters.some(c => item.categories.includes(c)) :   // Must match at least one filter
        false                                                                // Filter type in an unknown state: just accept none
    );

    reload_categories();

    let domIds = [...container.querySelectorAll(".item")].map(x => Number(x.dataset.id));
    let locIds = validItems.map(x => x.id);
    let didChange = domIds.length !== locIds.length || domIds.some((v, i) => v !== locIds[i]);
    if (validItems.length == 0) container.innerHTML = "<p>No items found. <b>Check your filters!</b></p>";
    if (!didChange) return;
    container.innerHTML = "";

    // Load items
    timeouts.forEach(clearTimeout);
    timeouts = [];
    validItems.forEach((item, i) => timeouts.push(setTimeout(() => add_item_to_container(item), item.src.startsWith("data:") ? i * 100 : (validItems.length > 500 ? i * 50 : 0))));
}

reload();