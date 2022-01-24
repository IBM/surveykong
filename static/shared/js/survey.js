(function ($) {
	
	var viewingPage, previousButton, nextButton, submitButton;
	
	
	function scrollToTop () {
		window.scrollTo({
			top: 0,
			left: 0,
			behavior: 'smooth'
		});
	}
	
	
	// Listen for parent to send custom form vars and create each as hidden fields.
	window.addEventListener('message', function (event) {
		if (event.data.message == 'customFormData') {
			var nameValuePairs = event.data.customFormData;
			
			document.getElementById('custom-parent-page-data').innerHTML = '';
			
			for (var key in nameValuePairs) {
				document.getElementById('custom-parent-page-data').innerHTML += '<input type="hidden" name="' + key + '" value="' + nameValuePairs[key] + '">';
			}
			// Have to dispatch event else event listener below won't work.
			document.querySelector('#custom-submit-button button').click();
		}
	});
	
	
	var checkedCustomVars = false;
	function setupSurveySubmit () {
		document.getElementById('custom-survey-form').addEventListener('submit', function (evt) {
			evt.preventDefault();
			
			// If in iframe and we haven't fetched custom data yet, fetch it.
			// The event listener (above) for the return message triggers submit again after
			//   it injects custom name/value pairs.
			if (!checkedCustomVars && window !== top) {
				checkedCustomVars = true;
				window.parent.postMessage({message:'sendCustomFormData'},'*');
				return;
			}
			
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
	
	
	function pageHasVisibleQustions (pageEl) {
		var visibleQuestioncCount = $(pageEl).find('.custom-question-con').not('.dn').length;
		if (visibleQuestioncCount > 0) {
			return true;
		}
		else {
			return false;
		}
	}
	
	
	function setupPagingButtons () {
		nextButton.addEventListener('click', function (evt) {
			evt.preventDefault();
			
			// Find required fields that aren't hidden and check if they are validly selected.
			// If any not, trigger submit to do native form error checking and notification.
			var valid = true,
				foundPage = false;
			
			$(viewingPage).find(':not(".dn") [required]').each(function() {
				if (valid == true && !this.checkValidity()) {
					valid = false;
					this.closest('form').querySelector('#custom-submit-button button').click();
					return;
				}
			})
			
			if (valid) {
				// Find the next page that has visible question and go to it.
				// else if none, we just submit it.
				$(viewingPage).nextAll('.custom-survey-page').each(function () {
					if (pageHasVisibleQustions(this)) {
						showPage(this);
						foundPage = true;
						return false;
					}
				});
				// Fallback when there are no next pages to show.
				if (!foundPage) {
					evt.target.closest('form').querySelector('#custom-submit-button button').click();
				}
			}
		});
		
		previousButton.addEventListener('click', function (evt) {
			evt.preventDefault();
			
			// Find the previous page that has visible question and go to it.
			// else if none, nothing
			$(viewingPage).prevAll('.custom-survey-page').each(function () {
				if (pageHasVisibleQustions(this)) {
					showPage(this);
					return false;
				}
			});			
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
		function toggleQuestion (selectedValuesArr, targetValuesArr, targetAction, childCon) {
			// If it's a match, do the action,
			// Otherwise do the opposite of the action.
			// Find if any value in the target matches a selected value.
			intersection = selectedValuesArr.filter(element => targetValuesArr.includes(element));
			
			if (intersection.length > 0) {
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
				// If the parent field is a checkbox, we need to pass all selected vals.
				var parentField = evt.target,
					selectedValues = $(parentField).val();
				
				if (parentField.type && parentField.type === 'checkbox') {
					var checkedVals = parentCon.find(':checkbox:checked').map(function() {
						return this.value;
					}).get();
					selectedValues = checkedVals.join(",");
				}
				
				// If it's an array, convert it to a string CSV to normalize it.
				if (Array.isArray(selectedValues)) {
					selectedValues = selectedValues.join(',');
				}
				
				// Convert string CSVs to arrays, setting #s to be numbers not strings.
				targetValuesArr = targetValues.split(',').map(function(item) {
					return isNaN(item) ? item : Number(item);
				});
				selectedValuesArr = selectedValues.split(',').map(function(item) {
					return isNaN(item) ? item : Number(item);
				});
				
				toggleQuestion(selectedValuesArr, targetValuesArr, targetAction, childCon);
			});
			// Run onload to set questions
			toggleQuestion(['none'], ['empty'], targetAction, childCon);
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
