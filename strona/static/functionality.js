function otworzInfo(evt, nazwa) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("info");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("bar-button");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(nazwa).style.display = "block";
    evt.currentTarget.className += " active";
}

function openProcesor(evt, optionName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("item4");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
        odznaczCheckbox(tabcontent[i]);
    }
    tablinks = document.getElementsByClassName("item3");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(optionName).style.display = "block";
    evt.currentTarget.className += " active";
    localStorage.setItem('wybrany', optionName);
}

function odznaczCheckbox(container) {
    var checkboxes = container.getElementsByTagName("input");
    Array.from(checkboxes).forEach(function(checkbox) {
        checkbox.checked = false;
    });
}



var wyswietlany = "";

function wypiszTresc(nazwa) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status == 200) {
            var response = JSON.parse(this.responseText);
            var preElement = document.createElement("pre");
            preElement.textContent = response.tresc;
            document.getElementById("code").innerHTML = "";
            document.getElementById("code").appendChild(preElement);
            
            preElement = document.createElement("pre");
            preElement.textContent = response.assembled;
            document.getElementById("fragment").innerHTML = "";
            document.getElementById("fragment").appendChild(preElement);
            
            localStorage.setItem(wyswietlany, nazwa);
        }
        else {
            document.getElementById("code").innerText = "error " + this.status;
        }
    };
    xhttp.open("GET", "plik/" + nazwa);
    xhttp.send();
}



function kompiluj(event) {
    event.preventDefault();

    var nazwa = localStorage.getItem(wyswietlany);
    if (!nazwa) {
        document.getElementById("code").innerHTML = "Najpierw wybierz plik.";
        return;
    }

    var formData = new FormData(document.getElementById("wyslij"));
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.status == 200) {
            var response = JSON.parse(this.responseText);
            var preElement = document.createElement("pre");
            preElement.textContent = response.tresc;
            document.getElementById("code").innerHTML = "";
            document.getElementById("code").appendChild(preElement);
            
            preElement = document.createElement("pre");
            preElement.textContent = response.assembled;
            document.getElementById("fragment").innerHTML = "";
            document.getElementById("fragment").appendChild(preElement);
        }
        else {
            document.getElementById("code").innerText = "error " + this.status;
        }
    };

    xhttp.open("GET", "plik/" + nazwa + "?" + new URLSearchParams(formData).toString());
    xhttp.send();
}

function pobierz(event) {
    event.preventDefault();

    var nazwa = localStorage.getItem(wyswietlany);
    if (!nazwa) {
        return;
    }

    var formData = new FormData(document.getElementById("wyslij"));
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        if (this.status === 200) {
            var blob = new Blob([this.response], { type: 'application/octet-stream' });
            var downloadLink = document.createElement('a');
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = nazwa.slice(0, -2) + ".asm";
            downloadLink.click();
        }
    };
    
    xhttp.open("GET", "plik/" + nazwa + "?" + new URLSearchParams(formData).toString() + "&submit-form-save");
    xhttp.send();   
}
