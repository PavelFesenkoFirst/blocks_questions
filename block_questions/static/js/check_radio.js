var radios = document.getElementsByName('correct');

for(i = 0; i<radios.length; i++ ) {
    let rad = radios[i].id.toString();
    radios[i].onclick = function(e) {
        this.value = rad;
        // alert('Hello');
    };
}

