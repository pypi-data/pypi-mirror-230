;(function($){
    $(document).ready(function(){
        $(".django-horizontal-list-filter-search").click(function(){
            var parameters = "?";
            var selects = $(this).parents(".django-horizontal-list-filter-bar").find(".django-horizontal-list-filter-group select");
            var inputs = $(this).parents(".django-horizontal-list-filter-bar").find(".django-horizontal-list-filter-group input");
            selects.each(function(){
                var select_parameter = $(this).val();
                if(select_parameter){
                    select_parameter = select_parameter.substring(1);
                    if(select_parameter){
                        parameters += select_parameter + "&";
                    }
                }
            });
            inputs.each(function(){
                var input_parameter = $(this).val();
                var input_name = $(this).attr("name");
                if(input_name && input_parameter){
                    parameters += input_name + "=" + input_parameter + "&";
                }
            });
            window.location.href = parameters;
        });
        $(".django-horizontal-list-filter-reset").click(function(){
            var selects = $(this).parents(".django-horizontal-list-filter-bar").find(".django-horizontal-list-filter-group select");
            var inputs = $(this).parents(".django-horizontal-list-filter-bar").find(".django-horizontal-list-filter-group input");
            selects.each(function(){
                $(this).val("?");
            });
            inputs.each(function(){
                $(this).val("");
            });
            $(".django-horizontal-list-filter-search").click();
        });
    });
})(jQuery);