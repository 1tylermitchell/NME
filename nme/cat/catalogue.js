window.addEvent('domready', function() {
	
	//create our Accordion instance
	var myAccordion = new Accordion($('accordion'), 'h2.toggler', 'div.element', {
		opacity: false,
		onActive: function(toggler, element){
			toggler.setStyle('color', '#0d2b61');
		},
		onBackground: function(toggler, element){
			toggler.setStyle('color', '#41464D');
		}
	});

});
