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
			
			// Find required fields that aren't hidden and check if they are validly selected.
			// If any not, trigger submit to do native form error checking and notification.
			var valid = true;
			$(viewingPage).find(':not(".dn") [required]').each(function() {
				if (valid == true && !this.checkValidity()) {
					valid = false;
					this.closest('form').querySelector('#custom-submit-button button').click();
					return;
				}
			})
			
			if (valid) {
				// If the next page doesn't have any visible questions, 
				//  and there's a next page, go to that one.
				// Else just go to next one.
				var nextPage = viewingPage.nextElementSibling,
					pageToShow = nextPage;
					
				if ($(nextPage).find('.custom-question-con').not('.dn').length === 0 && nextPage.classList.contains('custom-survey-page')) {
					pageToShow = nextPage.nextElementSibling;
				}
				showPage(pageToShow);
			}
		});
		previousButton.addEventListener('click', function (evt) {
			evt.preventDefault();
			
			// If the previous page doesn't have any visible questions, 
			//  and there's a previous page, go to that one.
			// Else just go to previous one.
			var prevPage = viewingPage.previousElementSibling,
				pageToShow = prevPage;
				
			if ($(prevPage).find('.custom-question-con').not('.dn').length === 0 && prevPage.classList.contains('custom-survey-page')) {
				pageToShow = prevPage.previousElementSibling;
			}
			showPage(pageToShow);
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
		function toggleQuestion (selectedVal, targetValues, targetAction, childCon) {
			// If it's a match, do the action,
			// Otherwise do the opposite of the action.
			selectedVal = isNaN(selectedVal) == false ? parseFloat(selectedVal) : selectedVal;
			
			// Target comes thru as possible CSV, so split it.
			targetValuesArr = targetValues.split(',');
			
			if (targetValuesArr.includes(selectedVal)) {
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
		
		
		function showQuestion (fieldCon, b) {
			if (b) {
				$(fieldCon).slideDown('fast', function () {
					$(fieldCon).removeClass('dn');
				});
				setRequired(fieldCon, b);
			}
			else {
				$(fieldCon).slideUp('fast', function () {
					$(fieldCon).addClass('dn');
				});
				setRequired(fieldCon, b);
			}
		}
		
		
		function clearAnswer (fieldCon) {
			$(fieldCon).find("textarea").val("").end().find("input:checked").prop("checked",false);
		}
		
		
		function setRequired (fieldCon, b) {
			if ($(fieldCon).find('label').data('required') == true) {
				if (b) {
					$(fieldCon).find('label[data-required="true"]').addClass('bo-field-required');
					$(fieldCon).find('input, select, textarea').each(function () {
						// If the field is the auto-generated "other" write-in field, don't make it required.
						if ($(this).closest('[id$="_autoother_container"]')[0]) {
							return;
						}
						else {
							$(this).prop('required', true);
						}
					});
				}
				else {
					$(fieldCon).find('label[data-required="true"]').removeClass('bo-field-required');
					$(fieldCon).find('input, select, textarea').prop('required', false);
				}	
			}
		}
		
		
		// Now bind each dependent question to it's parent's onchange.
		$("[data-parent-question]").each(function () {
			var childCon = $(this),
				parentCon = $('#q_' + $(this).data('parent-question') + '_container'),
				targetValues = $(this).data('parent-answer'),
				targetAction = $(this).data('parent-answer-action');
				
			parentCon.on("change", "select, input", function (evt) {
				toggleQuestion ($(evt.target).val(), targetValues, targetAction, childCon);
			});
			// Run onload to set questions
			toggleQuestion ('_', targetValues, targetAction, childCon);
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
