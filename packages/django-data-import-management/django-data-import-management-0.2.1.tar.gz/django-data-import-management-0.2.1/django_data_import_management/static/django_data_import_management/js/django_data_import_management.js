;(function($){
    $(document).ready(function(){
        $(".django_data_import_management_do_parse_button").click(function(event){
            event.stopPropagation();
            var url =  $(this).attr("href");
            $.ajax({
                method: "GET",
                url: url,
                success: function(data){
                    console.log("do parse response:", data);
                    alert(data.message);
                    window.location.reload();
                },
                error: function(error){
                    console.log("do parse failed:", error);
                    alert("do parse failed...");
                }
            })
            return false;
        });
        $(".django_data_import_management_do_import_button").click(function(event){
            event.stopPropagation(); 
            var url =  $(this).attr("href");
            $.ajax({
                method: "GET",
                url: url,
                success: function(data){
                    console.log("do import response:", data);
                    alert(data.message);
                    window.location.reload();
                },
                error: function(error){
                    console.log("do import failed:", error);
                    alert("do import failed...");
                }
            })
            return false;
        });
    });
})(jQuery);


