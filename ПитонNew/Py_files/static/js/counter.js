var count = 1
function handleClick_item(arg) {
    count = Number(document.getElementById("counter-display").textContent);
    if ( count + arg >= 1){
        count += arg;
        document.getElementById("counter-display").innerHTML = count;
    }
}

function handleClick_bin(arg, id) {
    count = Number(document.getElementById("counter-display" + id).textContent);
    if ( count + arg >= 1){
        count += arg;
        document.getElementById("counter-display" + id).innerHTML = count;
    }
}