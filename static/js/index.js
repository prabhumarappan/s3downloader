$(document).ready(function(){
    $(".searchbar").on('keyup', function(){
        
        search_value = $(".searchbar").val();
        results = document.querySelectorAll(".result");
        for(var i=0; i<results.length; i++){
            loop_id = results[i].id;
            if(!loop_id.includes(search_value)){
                console.log("Nope");
                results[i].style.display = "none";
            }
            else{
                console.log("Match");
                results[i].style.display = "block";
            }
        }

    });
});