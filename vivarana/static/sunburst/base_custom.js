var percentageSliderValue = 0.01;

$(document).ready(function () {
    $.material.init();
    $("#percentage-slider").noUiSlider({
        start: [10],
        step: 10,
	    range: {
		'min': [0],
		'max': [100]
	}
    });

    $("#close").on("click",function(){
            $("#rulegenerator").toggle();
            $("#chart2").toggle();
        return false;
    }
    );

    $("#sequence-rule-gen").on("click",function(){
        $("#chart2").toggle();
        $("#rulegenerator").toggle();
    });


    $(document).on('click', '.yamm .dropdown-menu', function (e) {
        e.stopPropagation();
    });

    $(function () {
        $("[data-toggle='tooltip']").tooltip();
    });


});

