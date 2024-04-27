function show_quick_form(){
    document.getElementById("gray_screen").style.display = 'block';
}


function fast_order(id){
    let obj = {};
    let need = document.getElementById('counter-display');
    obj["counter_display" + id] = need.innerText;

    number = document.getElementById('phone').value;
    client_name = document.getElementById('name').value;

    if (!/^[a-zA-Zа-яА-Я][a-zA-Zа-яА-Я-]+[a-zA-Zа-яА-Я]?$/.test(client_name)){
        document.getElementById("name_error").style.display = 'block';
        return
    }else{
        document.getElementById("name_error").style.display = 'none';
    }

    if (!isFinite(number) || !(number.length == 11)){
        document.getElementById("phone_error").style.display = 'block';
        return
    }else{
        document.getElementById("phone_error").style.display = 'none';
    }


    obj["name"] = client_name;
    obj["phone"] = number;

    fetch("",
        {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                'Accept': 'application/json'
            },
        body:JSON.stringify(obj)}).then(res=>{
                if(res.ok){
                    return res.json()
                }else{
                    alert("something is wrong")
                }
            }).then(jsonResponse=>{

                // Log the response data in the console
                console.log(jsonResponse)
            }
            ).catch((err) => console.error(err));
            window.location.href = 'http://127.0.0.1:5000/';
           }
