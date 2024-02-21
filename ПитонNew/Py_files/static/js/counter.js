let count = 0;

function handleClick(arg) {
    if ( count + arg >= 0){
        count += arg;
        document.getElementById("counter-display").innerHTML = count;
    }
}

function addOrUpdateUrlParam(name, value){
    var href = window.location.href;
    var regex = new RegExp("[&\\?]" + name + "=");
    if(regex.test(href))
    {
    regex = new RegExp("([&\\?])" + name + "=\\d+");
    window.location.href = href.replace(regex, "$1" + name + "=" + value);
    }
    else
    {
    if(href.indexOf("?") > -1)
        window.location.href = href + "&" + name + "=" + value;
    else
        window.location.href = href + "?" + name + "=" + value;
      }
    }