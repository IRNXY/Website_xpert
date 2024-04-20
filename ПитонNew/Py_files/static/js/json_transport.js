function del_items(id_item){
    obj = {"id": id_item};
    fetch("http://127.0.0.1:5000/bin",
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
    location.reload();
           }

function send_order(){
    let obj = {};
    let need = document.getElementsByClassName('num_of_prod');
    for (var i in need){
        obj[need[i].id] = need[i].innerText;
    }

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

    fetch("http://127.0.0.1:5000/bin",
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


