function show_form(){
    let need = document.getElementsByClassName('num_of_prod');
    if (need.length == 0){
        document.getElementById("label_empty").style.display = 'block';
    }else{
        document.getElementById("label_empty").style.display = 'none';
        document.getElementById("gray_screen").style.display = 'block';
    }
}

function hide_form(){
    document.getElementById("gray_screen").style.display = 'none';
}


function footer() {
    const
        main = document.getElementsByTagName('main')[0],
        footer = document.getElementsByTagName('footer')[0]
    console.log(main)
    main.style.paddingBottom = footer.clientHeight + 'px';
}

window.addEventListener('load', footer);
window.addEventListener('resize', footer);

let need = document.getElementById('object');

// console.log(need[0]);
