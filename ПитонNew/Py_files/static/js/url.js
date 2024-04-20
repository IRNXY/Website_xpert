
function addOrUpdateUrlParam(name, value){
    var href = window.location.href;
    var regex = new RegExp("[&\\?]" + name + "=");
    if(!regex.test(href)){
        if(href.indexOf("?") > -1)
            window.location.href = href + "&" + name + "=" + value + "-" + count;
        else
            window.location.href = href + "?" + name + "=" + value + "-" + count;
    }else{location.reload();}
}


window.addEventListener('keydown',function(e) {
        if (e.keyIdentifier=='U+000A' || e.keyIdentifier=='Enter' || e.keyCode==13) {
            if (e.target.nodeName=='INPUT' && e.target.type=='text') {
                e.preventDefault();
                return false;
            }
        }
    }, true);