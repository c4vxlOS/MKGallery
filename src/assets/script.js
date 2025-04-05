document.querySelectorAll(".modal:not([no-click])").forEach(modal =>
    modal.addEventListener("click", (event) => {
        if (event.target == modal) modal.classList.remove("active");
    })
);

document.querySelectorAll(".toggle__button").forEach(button =>
    button.addEventListener("click", () => button.classList.toggle("active"))
);

document.querySelectorAll(".option__switcher span").forEach(element => 
    element.addEventListener("click", () => {
        element.parentNode.querySelectorAll('span').forEach(x => x.classList.remove("active"));
        element.classList.add("active");
    })
);

document.querySelectorAll("input, textarea").forEach(x => x.addEventListener("focus", () => x.select()));

let hasUnsavedWarning = false;
const warnUnsavedChanges = () => {
    if (hasUnsavedWarning) return;
    hasUnsavedWarning = true;
    showNotification("Warning", 
        `Unsaved changes!<br><br>
        <div class="row">
        <button class='secondary' onclick="hasUnsavedWarning=false; exportPage()">Save</button>
        <button class='secondary' onclick="hasUnsavedWarning=false; this.parentNode.parentNode.parentNode.remove()">Discard</button>
        </div>
        
        `, "#1b9a9e", 999999999999);
}

const asBase64 = async (url) => {
    if (/^data:[a-zA-Z]+\/[a-zA-Z0-9.-]+;base64,/.test(url)) 
        return url;
    console.log(`Converting ${url}`);
    try {
        let response = await fetch(url);
        return `data:${response.headers.get("content-type")};base64,` + 
            btoa(new Uint8Array(await response.arrayBuffer()).reduce(function (data, byte) {
                return data + String.fromCharCode(byte);
            }, ''));
    } catch (error) { return null; };
};

const showNotification = async (title, content, color = "red", time=8000) => {
    document.querySelector(".notifications").insertAdjacentHTML("beforeEnd", `
    <section>
        <p>${title}</p>
        <span>${content}</span>
        <div class="progress" style="background: ${color};"></div>
    </section>
    `);
    let element = document.querySelector(".notifications section:last-of-type");
    element.querySelector(".progress").animate([ { width: '100%', opacity: 1 }, { width: '0%', opacity: 0 } ], { duration: time, fill: 'forwards' } ).onfinish = () => element.remove();
}

const copy = (text) => {
    navigator.clipboard.writeText(text)
        .then(() => showNotification('Success', 'Successfully copied source.', 'green'))
        .catch((e) => showNotification('Error', 'Something went wrong.'))
}

const download = (content, filename) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};

const downloadURL = (url, filename) => {
    fetch(url)
        .then(response => response.blob())
        .then(response => download(response, filename))
        .catch(e => showNotification("Error", "Error while downloading. (CORS)"));
}

const downloadMedia = async () => {
    items.forEach((item, i) => 
        setTimeout(async () =>
            downloadURL(`[${item.categories[0]}] ${item.filename}`),
            i * 500
        )
    )
};

let items = [];
const template = document.documentElement.outerHTML; // cache for exportPage
let filters = [ "all" ];
let filterType = 0;
let current = null;
let categories;

const loadItemsMetadata = () => {
    items = items.map(item => {
        item = typeof item === "string" ? { "url": item } : item;
        let filename = item.url.split("/").reverse()[0].split("?")[0].split("#")[0].split(";")[0];
        let filetype = item.url.startsWith("data:") ? item.url.split(";")[0].split("/")[1] : filename.split(".").reverse()[0];
        let type = [ "mp4", "avi", "mkv", "mov", "flv", "webm", "wmv" ].includes(filetype) ? "video" : 
                   [ "png", "jpg", "jpeg", "gif", "webp" ].includes(filetype) ? "image" : "unknown";
        return { "url": item.url, "origin": item.origin || item.url, "filename": item.filename || filename, "filetype": item.filetype || filetype, "categories": item.categories || [ type ], "type": type }
    });
}

const createCategory = (name) => {
    categories.push(name.toLowerCase());
    current.categories.push(name.toLowerCase());
    loadCategories();
    warnUnsavedChanges();
}

const exportPage = (title = document.title) => {
    let newItems = items.map(item => 
        item.origin == item.url ? { "url": item.url, "categories": item.categories } :
        { "url": item.url, "origin": item.origin, "filename": item.filename, "categories": item.categories });
    let source = template.replace(/let\s+items\s*=\s*\[(.*?)\]/gs, (match, p1) => `let items = ${JSON.stringify(newItems)};`);
    source = source.replace(`<title>${document.title}</title>`, `<title>${title}</title>`);
    download(source, `${title}.html`);
};

const addURLs = (urls) => {
    urls.split("\n").map(url => url.startsWith("[") ? { "url": url.split("]")[1], "categories": url.split("]")[0].replace("[", "").split(";") } : { "url": url })
        .forEach(x => items.push(x));
    reload();
    loadCategories();
    warnUnsavedChanges();
}

const loadCategories = () => {
    categories = categories || [...new Set(items.flatMap(x => x.categories))];

    [...document.querySelectorAll(".filters__list span")].filter(x => !["all", "+"].includes(x.innerHTML.toLowerCase())).forEach(x => x.remove());
    
    document.querySelectorAll(".filters__list").forEach(list =>
        list.innerHTML += categories.map(c => `<span>${c.toUpperCase()}</span>`).join("\n")
    );

    document.querySelectorAll(".filters__list span").forEach(element => {
        let filter = element.innerHTML.toLowerCase();
        let all = [...element.parentNode.querySelectorAll("span")];
        let allButton = all.find(x => x.innerHTML.toLowerCase() == "all");

        element.addEventListener("click", () => {    
            if (filter == "all") {
                all.forEach(x => x.classList.remove("active"));
                element.classList.add("active");
            } else {
                allButton?.classList.remove("active");
                element.classList.toggle("active");
            }
    
            let aFilters = [...element.parentNode.querySelectorAll("span.active")].map(x => x.innerHTML.toLowerCase()).filter(x => x != "+");
            if (element.parentNode.parentNode.parentNode.id == "filter__panel") {
                filters = aFilters;
                if (filters.length == 0) allButton?.click();
            } else {
                current.categories = aFilters;
            }
    
            reload();
        });
    });
}

const openItemOptions = (id) => {
    current = items[id];
    document.querySelector("#item__options__modal p").innerHTML = current.filename;
    document.querySelectorAll("#item__options__modal .filters__list span").forEach(element => 
        current.categories.includes(element.innerHTML.toLowerCase()) ? element.classList.add("active") : element.classList.remove("active")
    );
    document.querySelector("#item__options__modal").classList.add("active");
}

const packageB64 = async () => {
    showNotification("Important", "Compressing media. This might take a while!");

    let encoded = await Promise.all(items.map(url => asBase64(url.url)));
    encoded = encoded.filter(encodedUrl => encodedUrl !== null);

    items = encoded.map((url, idx) => {
        items[idx].url = url;
        return items[idx];
    });
};

const displayItem = (item, id) => {
    document.querySelector(".gallery__items").innerHTML += `
    <section onclick="this.classList.toggle('active');" oncontextmenu="event.preventDefault(); this.querySelector('button').click()" id="${id}">
        <div class="content">
            <button class="primary" onclick="this.parentNode.parentNode.click(); openItemOptions('${id}')">Options</button>
            ${ item.type == "video" ? `<video src="${item.url}" class="display" loop controls></video>`
                : item.type == "image" ? `<img src="${item.url}" class="display" alt="${item.filename}">`
                : "<br><span>Filetype not supported!</span><br>" }<p>${item.filename}</p>
        </div>
    </section>`;
}

const reload = async () => {
    document.querySelector(".gallery__items").innerHTML = "";
    categories = [...new Set(items.flatMap(x => x.categories))];
    loadItemsMetadata();
    let validItems = items.filter(item => filters.includes("all") ||
        (filterType == 0 ? !filters.map(c => item.categories.includes(c)).includes(false)
        : filterType == 1 ? item.categories.some(c => filters.includes(c)) : false));
    validItems.forEach(displayItem);

    if (validItems.length == 0) {
        document.querySelector(".gallery__items").innerHTML = "<p>No items found. <b>Check your filters!</b></p>";
    }
}

loadItemsMetadata();
loadCategories();
reload();