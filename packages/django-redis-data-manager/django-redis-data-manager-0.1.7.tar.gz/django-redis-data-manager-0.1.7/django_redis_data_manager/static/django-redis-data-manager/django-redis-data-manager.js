;!(function($){
    $(document).ready(function(){

        $(".django-redis-data-manager").each(function(index, element){
            var tree = $(element).find(".django-redis-data-manager-key-tree");
            var config = $.parseJSON(tree.attr("django-redis-data-manager-config"));
            var data_api_url = config["data-api-url"];
            var detail_api_url = config["detail-api-url"];
            var flushdb_api_url = config["flushdb-api-url"];
            var delete_api_url = config["delete-api-url"];
            var form = $(element).find(".django-redis-data-manager-key-search-form");
            var refresh_button = $(element).find(".django-redis-data-manager-key-tree-refresh");
            var search_keyword = $(element).find("#django-redis-data-manager-key-tree-search-keyword");
            var reset_button = $(element).find(".django-redis-data-manager-key-tree-search-reset");
            var detail_header = $(element).find(".django-redis-data-manager-key-detail-header");
            var detail_info = $(element).find(".django-redis-data-manager-key-detail-info");
            var flushdb_button = $(element).find(".django-redis-data-manager-flushdb-button");
            var delete_button = $(element).find(".django-redis-data-manager-delete-button");
            var selected_node_id = "";
            console.log(flushdb_button);
            tree.jstree({
                core: {
                    data: {
                        url: data_api_url + "?q=" + search_keyword.val(),
                        dataType: "json",
                    }
                }
            });
            tree.on("select_node.jstree", function(event, data) {
                detail_info.html("<span>Loading...</span>");
                selected_node_id = data.node.id;
                $.ajax({
                    method: "GET",
                    url: detail_api_url,
                    data: {
                        "key": data.node.id,
                    },
                    dataType: "json",
                    success: function(data){
                        detail_info.html("");
                        detail_info.append($(data.html));
                    }
                });
            });
            refresh_button.click(function(){
                tree.jstree("refresh");
            });
            reset_button.click(function(){
                search_keyword.val("");
            });
            flushdb_button.click(function(){
                console.log("flushing...");
                $.ajax({
                    method: "GET",
                    url: flushdb_api_url,
                    dataType: "json",
                    success: function(data){
                        window.location.reload();
                    }
                });
            });
            delete_button.click(function(){
                console.log("deleting..");
                $.ajax({
                    method: "GET",
                    url: delete_api_url,
                    data: {
                        "key": selected_node_id
                    },
                    dataType: "json",
                    success: function(data){
                        window.location.reload();
                    }
                })
            });
        });



    });
})(jQuery);