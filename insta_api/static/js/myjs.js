
$(".like-Unlike").click(function(e) {
    if ($(this).html() == "Like") {
        $(this).html('Unlike');
    }
    else {
        $(this).html('Like');

    }
    return false;
});

function myFunction(x) {
 if (x.style.color == "red"){
     x.style.color = "black";
 }
 else{
 x.style.color = "red";



}
}






