document.querySelectorAll(".modal").forEach(modal => {
    modal.addEventListener("click", (event) => {
        if (!(["div"].includes(event.target.nodeName.toLowerCase()) || event.target.hasAttribute("data-modal-close"))) return;

        modal.classList.remove("active");
    });
});

const open_modal = (name) => {
    document.querySelector(name)?.classList?.add("active");
}

document.querySelectorAll(".switch span").forEach(span => span.addEventListener("click", () => {
    span.parentNode.querySelectorAll("span.active").forEach(x => x.classList.remove("active"));
    span.classList.add("active");
}));

const showNotification = (title, content, color = "red", time = 8000) => {
    document.querySelector(".notification__container").insertAdjacentHTML("beforeend", `
        <div class="col primary">
            <p class="title">${title}</p>
            <p class="content">${content}</p>
            <div class="bar" style="background: ${color};"></div>
        </div>
    `);
    let element = document.querySelector(".notification__container div.primary:last-of-type");
    if (!element || time == null) return;
    element.querySelector(".bar").animate([ { width: '100%', opacity: 1 }, { width: '0%', opacity: 0 } ], { duration: time, fill: 'forwards' } ).onfinish = () => element.remove();
}