$(document).ready(function () {
    $("#grid .imgSmall").click(function () {
        $(".imgBig").attr("src", $(this).prop("src"));
        $(".overlay").show("slow");
        $(".overlayContent").show("slow");
    });

    $(".imgBig").click(function () {
        $(".imgBig").attr("src", "");
        $(".overlay").hide();
        $(".overlayContent").hide();
    });
});
