$('#close').click(function(){
	$(this).parent().toggleClass('closed');
    $(this).prev().focus();
});

setTimeout(function() {
    $('#close').click();
}, 100);

setTimeout(function() {
    $('#close').click();
}, 1500);
