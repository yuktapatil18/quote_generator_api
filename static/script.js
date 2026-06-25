// static/script.js

function copyQuote() {

    let quote =
        document.getElementById("quoteText").innerText;

    navigator.clipboard.writeText(quote);

    alert("Quote Copied!");
}