$(document).ready(function () {
    $(".btn-secondary").click(function () {
        //disable the default form submission
        event.preventDefault();
        //grab all form data
        var formData = {yt_url: $("#videoFrame").attr('src'),
                        comment: $("#yt_comment").text(),
                        comment_id: $("#comment_id").text(),
                        label: $(this).attr('value')};

        $.ajax({
            url: 'process',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            async: false,
            cache: false,
            processData: false,
            success: function (result) {
                if ($("#videoFrame").attr('src') != result['yt_url'] ) {
                    $("#alert").show();
                    $("#videoFrame").attr('src', result['yt_url']);
                } else {
                    $("#alert").hide();
                }

                $("#yt_comment").text(result['comment']);
                $("#comment_id").text(result['comment_id']);
                $("#progress").css('width', result['progress']);
                $("#progress").text(result['progress']);

            },
            error: function(){
                alert("error in ajax form submission");
            }
        });

        return false;
    });
});