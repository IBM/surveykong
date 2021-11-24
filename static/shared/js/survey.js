(function ($) {
	
	var viewingPage, previousButton, nextButton, submitButton;
	
	
	function scrollToTop () {
		window.scrollTo({
			top: 0,
			left: 0,
			behavior: 'smooth'
		});
	}
	
	
	function setupSurveySubmit () {
		document.getElementById('custom-survey-form').addEventListener('submit', function (evt) {
			evt.preventDefault();
			
			document.getElementById('custom-processing').removeAttribute('style');

			var $form = $(evt.target),
				formData = $form.serialize();
			
			$.ajax({
				url: $form.attr('action'),
				type: $form.attr('method'), 
				data: formData,
				success: function (data) {
					document.getElementById('custom-content').innerHTML = data.message;
				},
				error: function (response) {
					document.getElementById('custom-form-error-message').innerHTML = 'Error: ' + response.responseJSON.results.message;
					document.getElementById('custom-form-error-message').classList.remove('dn');
					document.getElementById('custom-processing').style.display = 'none';
					SK.scrollToTop();
				}
			});
		});
	}
	
	
	// Paging
	function adjustPaging () {
		document.getElementById('custom-survey-buttons').classList.add('dn');
		
		if (viewingPage.nextElementSibling.classList.contains('custom-survey-page')) {
			showNextButton();
		}
		else {
			showsubmitButton();
		}
		
		if (viewingPage.previousElementSibling.classList.contains('custom-survey-page')) {
			showPreviousButton();
		}
		else {
			hidePreviousButton();
		}
		
		setTimeout(function () {
			document.getElementById('custom-survey-buttons').classList.remove('dn');
		}, 487);
	}
	
	function showPage (el) {
		viewingPage.classList.remove('custom-showing');
		el.classList.add('custom-showing');
		scrollToTop();
		viewingPage = el;
		adjustPaging();
	}
	
	function setupPagingButtons () {
		nextButton.addEventListener('click', function (evt) {
			evt.preventDefault();
			
			var valid = true;
			$(viewingPage).find('[required]').each(function() {
				if (valid == true && !this.checkValidity()) {
					valid = false;
					this.closest('form').querySelector('#custom-submit-button button').click();
					return;
				}
			})
			
			if (valid) {
				showPage(viewingPage.nextElementSibling);
			}
		});
		previousButton.addEventListener('click', function (evt) {
			evt.preventDefault();
			showPage(viewingPage.previousElementSibling);
		});
	}
	
	function showNextButton () {
		nextButton.classList.remove('dn');
		submitButton.classList.add('dn');
	}
	
	function showsubmitButton () {
		nextButton.classList.add('dn');
		submitButton.classList.remove('dn');
	}
	
	function showPreviousButton () {
		previousButton.classList.remove('dn');
	}
	
	function hidePreviousButton () {
		previousButton.classList.add('dn');
	}
	
	
	function setupQuestionDependency () {
		function toggleQuestion (selectedVal, targetVal, targetAction, childCon) {
			// If it's a match, do the action,
			// Otherwise do the opposite of the action.
			if (selectedVal == targetVal) {
				if (targetAction === 'show') {
					showQuestion(childCon, true);
				}
				else {
					showQuestion(childCon, false);
					clearAnswer(childCon);
				}
			}
			else {
				if (targetAction === 'hide') {
					showQuestion(childCon, true);
				}
				else {
					showQuestion(childCon, false);
					clearAnswer(childCon);
				}
			}
		}
		
		
		function showQuestion (container, b) {
			if (b) {
				$(container).slideDown();
			}
			else {
				$(container).slideUp();
			}
		}
		
		
		function clearAnswer (container) {
			$(container).find("textarea").val("").end().find("input:checked").prop("checked",false);
		}
		
		
		// Now bind each dependent question to it's parent's onchange.
		$("[data-parent-question]").each(function () {
			var childCon = $(this),
				parentCon = $('#q_' + $(this).data('parent-question') + '_container'),
				targetVal = $(this).data('parent-answer'),
				targetAction = $(this).data('parent-answer-action');
				
			parentCon.on("change", "select, input", function (evt) {
				toggleQuestion ($(evt.target).val(), targetVal, targetAction, childCon);
			});
			toggleQuestion ('_', targetVal, targetAction, childCon);
		});
		
		
		
	}
	
	
	// JS is at bottom of page. Fire at will.
	viewingPage = document.querySelector('.custom-survey-page.custom-showing');
	previousButton = document.getElementById('custom-previous-button');
	nextButton = document.getElementById('custom-next-button');
	submitButton = document.getElementById('custom-submit-button');
	
	if (nextButton) {
		setupPagingButtons();
		adjustPaging();
	}
	if (submitButton) {
		setupSurveySubmit();
	}
	
	setupQuestionDependency();
	
})(jQuery);
