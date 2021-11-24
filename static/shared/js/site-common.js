(function($){
	
	function flashMessage (el) {
		el.classList.add('bo-fadein');
		setTimeout(function () {
			el.classList.remove('bo-fadeout');
		}, 10);
		setTimeout(function () {
			el.classList.add('bo-fadeout');
		}, 1600);	
	}
	SK.flashMessage = flashMessage;

	
	function addFieldUnits () {
		$('[data-units]').each(function () {
			$(this).after('<div class="dib ml2">' + $(this).data('units') + '</dib>');
		});
	}
	
	
	SK.scrollToTop = function () {
		window.scrollTo({
			top: 0,
			left: 0,
			behavior: 'smooth'
		});
	}
	
	
	SK.dragEnter = function (evt) {
		evt.target.classList.add('custom-droppable');
	}
	
	SK.dragLeave = function (evt) {
		evt.target.classList.remove('custom-droppable');
	}
	
	SK.allowDrop = function (evt) {
		evt.preventDefault();
	}
	
	SK.drag = function (evt) {
		evt.dataTransfer.setData("text", evt.target.id);
	}
	
	SK.drop = function (evt) {
		evt.preventDefault();
		var data = evt.dataTransfer.getData("text");
		
		if (document.getElementById(data).getAttribute('data-dragtype') == evt.target.getAttribute('data-droptype')) {	
			evt.target.parentElement.before(document.getElementById(data));
		}
		evt.target.classList.remove('custom-droppable');
	}
		
	
	$(function () {
		addFieldUnits();
	});
	
})(jQuery);

