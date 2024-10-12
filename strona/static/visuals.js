/* DARKMODE */  

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.documentElement.classList.add(savedTheme);
}

function changeColorTheme() {
    document.documentElement.classList.toggle('dark-theme');

    const currentTheme = document.documentElement.classList.contains('dark-theme') ? 'dark-theme': '';
    localStorage.setItem('theme', currentTheme);
}



/* RESIZE CODE/FRAGMENT */

let isDragging = false;

function ResetColumnSizes() {
    let page = document.getElementById("grid");
    if (page.clientWidth > 1100) {
        page.style.gridTemplateColumns = "20% 1fr 6px 25%";
    }
    else {
        page.style.gridTemplateColumns = "95vw 5vw";
    }
}

function SetCursor(cursor) {
    let grid = document.getElementById("grid");
    grid.style.cursor = cursor;
}

function disableSelect(event) { // disable text select while resizing
    event.preventDefault();
}

function StartDrag() {
    isDragging = true;
    window.addEventListener('selectstart', disableSelect)

    SetCursor("ew-resize");
}

function EndDrag() {
    isDragging = false;
    window.removeEventListener('selectstart', disableSelect);

    SetCursor("auto");
}

function OnDrag(event) {
    if (isDragging) {
        let grid = document.getElementById("grid");

        let leftColWidth = document.getElementById("file").clientWidth;
        let dragbarWidth = 6;
        let rightColWidth = isDragging ? grid.clientWidth - event.clientX : document.getElementById("fragment").clientWidth;

        let cols = [
            leftColWidth,
            grid.clientWidth - 2 * dragbarWidth - leftColWidth - rightColWidth,
            dragbarWidth,
            rightColWidth
        ];

        let newColDefn = cols.map(c => c.toString() + "px").join(" ");

        grid.style.gridTemplateColumns = newColDefn;

        event.preventDefault();
    }
}
