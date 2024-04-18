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
    total = Number(document.getElementById("vert_center_2").textContent);

    price = document.getElementById("prod_price" + id).textContent;
    price = Number(price.substring(0, price.length - 2))
    if ( count + arg >= 1){
        count += arg;
        document.getElementById("counter-display" + id).innerHTML = count;
        document.getElementById("prod_total" + id).innerHTML = (count * price).toFixed(2) + "p.";
        if (arg > 0){
            document.getElementById("vert_center_2").innerHTML = (total + price).toFixed(2) ;
        }else{
            document.getElementById("vert_center_2").innerHTML = (total - price).toFixed(2) ;
        }
    }

    let need = document.getElementsByClassName('num_of_prod');
    console.log(need);
    for (var i in need){
        console.log(need[i].id, need[i].innerText);
    }
}

