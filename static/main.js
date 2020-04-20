$("#ipt").keyup(function(e) {
    var inputVal = (e.target.value);
    for(let i = inputVal.length - 1; i>=0; i--) {
        if(i%3 === 0) {
            
        }
    }
    $(this).val(inputVal.toUpperCase());
})