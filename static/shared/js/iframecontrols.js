(function () {

	const FOCUSABLE_ELEMENTS = [
		'a[href]',
		'input:not([disabled]):not([type="hidden"]):not([aria-hidden])',
		'select:not([disabled]):not([aria-hidden])',
		'textarea:not([disabled]):not([aria-hidden])',
		'button:not([disabled]):not([aria-hidden])',
		'[tabindex]:not([tabindex^="-"])'
	];
	
	
	window.BH.closeModal = function () {
		window.parent.postMessage({message: 'removeOverlay'},'*');
	}
	
	
	// A11Y.
	function getFocusableNodes () {
		const nodes = document.body.querySelectorAll(FOCUSABLE_ELEMENTS)
		return Array(...nodes)
	}
	
	function setFocusToFirstNode () {
		var focusableNodes = getFocusableNodes()
		
		// Remove nodes on whose click, the modal closes
		const nodesWhichAreNotCloseTargets = focusableNodes.filter(node => {
			return !node.classList.contains('surveykong-overlay-close')
		})
		if (nodesWhichAreNotCloseTargets.length > 0) nodesWhichAreNotCloseTargets[0].focus()
		if (nodesWhichAreNotCloseTargets.length === 0) focusableNodes[0].focus()
	}
	
	function retainFocus (evt) {
		var focusableNodes = getFocusableNodes();
		
		focusableNodes = focusableNodes.filter(node => {
			return (node.offsetParent !== null);
		})
		
		const focusedItemIndex = focusableNodes.indexOf(document.activeElement);
		
		if (evt.shiftKey && focusedItemIndex === 0) {
			focusableNodes[focusableNodes.length - 1].focus();
			evt.preventDefault();
		}
		
		if (!evt.shiftKey && focusableNodes.length > 0 && focusedItemIndex === focusableNodes.length - 1) {
			focusableNodes[0].focus()
			evt.preventDefault()
		}
	}
	
	// Fire away.
	setFocusToFirstNode();
	document.addEventListener('keydown', function (evt) {
		if (evt.keyCode === 27) BH.closeModal();
		if (evt.keyCode === 9) retainFocus(evt)
	});
	
})();
