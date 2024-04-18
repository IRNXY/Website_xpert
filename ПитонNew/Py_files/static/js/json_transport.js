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
