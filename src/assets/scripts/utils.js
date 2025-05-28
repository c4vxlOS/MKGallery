let corsProxy = "https://corsproxy.io/?";
const fetch_cors = async (url) => {
    try {
        return (await fetch(url));
    } catch (e) {
        if (url.startsWith(corsProxy)) {
            showNotification("Error", `Error while downloading: ${e}`);
            return null;
        }
        return fetch_cors(corsProxy + url);
    }
}

const copy = (text) => {
    navigator.clipboard?.writeText(text)
        .then(() => showNotification('Success', 'Successfully copied source.', 'green'))
        .catch((e) => showNotification('Error', 'Something went wrong.')) || showNotification("Error", "Clipboard api not working on HTTP!")
}

const download = (content, filename) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

const download_url = (url, filename) => {
    fetch_cors(url).then(x => x.blob()).then(x => download(x, filename));
}

const export_all_media = async () => {
    items.forEach((item, i) => 
        setTimeout(async () =>
            download_url(item.src, `[${item.categories[0]}] ${item.name}`),
            i * 500
        )
    )
}

const items_to_enc = (src = true) => {
    return items.map(item => {
        let c = item.categories.filter(c => c != item.type).join(";");
        let u = src ? item.src : item.origin;
        return c ? `[${c}] ${u}` : u;
    }).join("\n");
}

const asBase64 = async (url) => {
    if (/^data:[a-zA-Z]+\/[a-zA-Z0-9.-]+;base64,/.test(url)) 
        return url;
    console.log(`Converting ${url}`);
    try {
        let response = await fetch_cors(url);
        return `data:${response.headers.get("content-type")};base64,` + 
            btoa(new Uint8Array(await response.arrayBuffer()).reduce(function (data, byte) {
                return data + String.fromCharCode(byte);
            }, ''));
    } catch (error) { return null; };
}

const pb64 = async () => {
    showNotification("Important", "Compressing media. This might take a while!");

    let encoded = await Promise.all(items.map(src => asBase64(src.src)));
    encoded = encoded.filter(encodedUrl => encodedUrl !== null);

    items = encoded.map((src, idx) => {
        items[idx].src = src;
        return items[idx];
    });
}

let unsaveWarn = false;
const warn_unsaved = () => {
    if (unsaveWarn) return;
    unsaveWarn = true;
    showNotification("Warning", "You have unsaved changes!<br><br><button class='primary' onclick='export_page(); unsaveWarn = false; this.parentNode.parentNode.remove()'>Save</button><br><button class='primary' onclick='unsaveWarn = false; this.parentNode.parentNode.remove()'>Ignore</button>", "red", null);
}