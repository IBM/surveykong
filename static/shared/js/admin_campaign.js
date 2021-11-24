(function ($) {
	
	function setupShowHideFields () {
		showHideData = [
			{
				'field': 'survey_trigger_type',
				'triggers': [
					{
						values: [''],
						show: [],
						hide: [
							'button',
							'survey_invite',
							'mouseout_trigger',
							'visitor_percent',
							'seconds_on_page_delay',
							'page_view_count',
							'repeat_visitors_only',
						],
					},
					{
						values: ['intercept'],
						show: [
							'survey_invite',
							'mouseout_trigger',
							'visitor_percent',
							'seconds_on_page_delay',
							'page_view_count',
							'repeat_visitors_only',
						],
						hide: [
							'button',
						],
					},
					{
						values: ['button'],
						show: [
							'button',
						],
						hide: [
							'survey_invite',
							'mouseout_trigger',
							'visitor_percent',
							'seconds_on_page_delay',
							'page_view_count',
							'repeat_visitors_only',
						],
					},
				]
				
			}
		];
		
		showHideData.forEach(function (item) {
			$('#id_'+item.field).on('change', function (evt) {
				var val = evt.target.value;
				item.triggers.forEach(function (triggerData) {
					if (triggerData.values.includes(val)) {
						triggerData.hide.forEach(function (hideField) {
							show(hideField+'-row', false);
						});
						triggerData.show.forEach(function (showField) {
							show(showField+'-row', true);
						});
					}
				});
			});
		})
	}
	
	
	function show (ids, b) {
		if (typeof ids === 'string') {
			ids = [ids];
		}
		ids.forEach(function (id) {
			if (b) {
				document.getElementById(id).classList.remove('dn');
			}
			else {
				document.getElementById(id).classList.add('dn');
			}
		});
	}
	
	
	$(function () {
		//document.querySelector('.custom-modelform').addEventListener('submit', formOnsubmitHandler);
		
		setupShowHideFields();
		
		$('#id_survey_trigger_type').trigger('change');
	});
		
		
	
})(jQuery);
