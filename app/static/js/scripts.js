$(document).ready(function () {
    $(".btn-secondary").click(function () {
        //disable the default form submission
        event.preventDefault();
        //grab all form data
        var formData = {yt_url: $("#videoFrame").attr('src'),
                        comment: $("#yt_comment").text(),
                        label: $(this).attr('value')};

        $.ajax({
            url: 'process',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            async: true,
            cache: false,
            processData: false,
            success: function (result) {
                $("#videoFrame").attr('src', result['yt_url'])
                $("#yt_comment").text(result['comment'])

                $("#progress").css('width', result['progress'])
                $("#progress").text(result['progress'])
            },
            error: function(){
                alert("error in ajax form submission");
            }
        });

        return false;
    });
});