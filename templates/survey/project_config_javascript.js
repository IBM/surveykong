{% load common_templatetags %}
{% getTemplateHelpers as templateHelpers %}


(function () {
	window.console.info('%c SurveyKong %c ' + [timer], "color: white; background: blue;", "");
	window.SK = window.SK || {};
	
	function injectOnReady(f){"loading"===document.readyState?document.addEventListener("DOMContentLoaded",f):f()}
	
	function appendToBody(htmlStr) {
		var fragment = document.createDocumentFragment(),
			$elem = document.createElement('div');
			$elem.innerHTML = htmlStr;
		while($elem.firstChild) {
			fragment.appendChild($elem.firstChild);
		}
		document.body.appendChild(fragment);
	}
	
	var activeEl;
	
	SK.activeCampaignsData = {{ activeCampaignsData|safe }};
	
	{##}
	{##}
	{##  Public APIs  #}
	{##}
	{##}
	
	{# PUBLIC function passes campaign UID to local function to show overlay and embed iframe survey #}
	window.SK.showSurvey = function (cuid, b) {
		activeEl = document.activeElement;
		showSurvey("{% url 'survey:survey_iframe_display' %}?cuid="+cuid+(b?'&force=y':''));
	};
			
	{% if flags.hasInvite %}
	
		window.SK.showInvite = function () {
			if (!document.getElementById('surveykong-invite-card')) {
				activeEl = document.activeElement;
				appendToBody(`<style>#surveykong-invite-card{transform:translate3d(101%,-50%,0);transition:transform .5s cubic-bezier(0.4,1,0.5,1);}#surveykong-invite-card.show{transform:translate3d(0,-50%,0);</style><iframe id="surveykong-invite-card" style="background:#fff;z-index:99999999;position:fixed;top:50%;right:0;width:24rem;box-shadow:-2px 2px 15px rgba(0,0,0,0.7);border: 2px solid gray;border-right:0;" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" title="SurveyKong survey" src="{% if not debug %}https://REPLACE_ME.com{% endif %}{% url 'survey:survey_iframe_invite' uid=campaignStats.campaign.uid %}"></iframe>`);
				setTimeout(function () {
					document.getElementById('surveykong-invite-card').classList.add('show');
				}, {{ campaignStats.campaign.seconds_on_page_delay|default:0 }}000);
			}
		};
		
	{% endif %}
	
	{##}
	{##}
	{##  INTERCEPT or BUTTON show/hide methods (not invite)  #}
	{##}
	{##}
	
	{% if flags.hasIntercept or flags.hasButton %}
	
		function moveAndShowButton (el) {
			var styles, 
				pos = '{{ buttonCampaign.button.position|default:'right' }}',
				offset = {{ buttonCampaign.button.offset|default:50 }};
			
			switch (pos) {
				case 'top':
					styles = 'top:0;bottom:auto;';
					if (offset < 50) {
						styles += 'right:auto;left:'+offset+'%;transform:none;'
					}
					else if (offset === 50) {
						styles += 'right:auto;left:'+offset+'%;transform:translate3d(-50%,0,0);'
					}
					else {
						styles += 'right:'+ (100-offset)+'%;left:auto;transform:none;'
					}
					break;
					
				case 'bottom':
					styles = 'top:auto;bottom:0;';
					if (offset < 50) {
						styles += 'right:auto;left:'+offset+'%;transform:none;'
					}
					else if (offset === 50) {
						styles += 'right:auto;left:'+offset+'%;transform:translate3d(-50%,0,0);'
					}
					else {
						styles += 'right:'+ (100-offset)+'%;left:auto;transform:none;'
					}
					break;
			
				case 'left':
					styles = 'right:auto;bottom:auto;left:0;transform-origin:top left;';
					if (offset < 50) {
						styles += 'top:'+offset+'%;transform:rotate(-90deg) translate3d(-100%,0,0);'
					}
					else if (offset === 50) {
						styles += 'top:'+offset+'%;transform:rotate(-90deg) translate3d(-50%,0,0);'
					}
					else {
						styles += 'top:'+offset+'%;transform:rotate(-90deg);'
					}
					break;
					
				case 'right':
					styles = 'right:0;bottom:auto;left:auto;transform-origin:top right;';
					if (offset < 50) {
						styles += 'top:'+offset+'%;transform:rotate(-90deg) translate3d(0%,-100%,0);'
					}
					else if (offset === 50) {
						styles += 'top:'+offset+'%;transform:rotate(-90deg) translate3d(50%,-100%,0);'
					}
					else {
						styles += 'top:'+offset+'%;transform:rotate(-90deg) translate3d(100%,-100%,0);'
					}
					break;
			}
			el.style.cssText += styles;
		}
		
		function showSurvey (url) {
			if (!document.getElementById('surveykong-overlay')) {
				appendToBody(`<div data-surveykong-overlay-close id="surveykong-overlay" style="align-items: center;background: rgba(0,0,0,.7);display: flex;height: 100%;left: 0;position: fixed;top: 0;width: 100%;z-index: 99999999999999999999;"><div id="surveykong-overlay-survey" style="background: #fff;max-height: 90vh;height: 90vh;max-width: 576px;width: 90vw;transition: all .4s cubic-bezier(0.4,1,0.5,1);left: 50%;position: absolute;transform: translate3d(-50%,0,0);"><iframe frameborder="0" marginwidth="0" marginheight="0" scrolling="yes" width="100%" height="100%" src="{% if not debug %}https://REPLACE_ME.com{% endif %}{url}"></iframe></div></div><style>.shrinkToIcon{opacity:0}.shrinkToIcon > div{height:0!important;width:0!important;left:101%!important;opacity:.3}</style>`.replace('{url}', url));
				document.querySelector('#surveykong-overlay').querySelector('iframe').contentWindow.focus();
				document.addEventListener('click', function (evt) {
					if (evt.target.hasAttribute('data-surveykong-overlay-close')) {
						window.postMessage({message: 'removeOverlay'},'*');
					}
				});
			}
		}
		
		function injectReminderIcon () {
			if (!document.getElementById('surveykong-survey-reminder')) {
				document.getElementById('surveykong-buttons-con').innerHTML = `<style>#surveykong-survey-reminder svg{width:2rem;height:2rem;drop-shadow(0px -1px 1px #fff) drop-shadow(1px 0px 3px #fff)}</style><a id="surveykong-survey-reminder" href="#" onclick="SK.rich();return false;" title="Reminder to take the survey" style="display:block;margin-right:1rem;">{{ templateHelpers.html.icons.reminderIconLeft|safe }}</a>` + document.getElementById('surveykong-buttons-con').innerHTML;
				
				if (document.getElementById('surveykong-buttons-con').style.transform.indexOf('(-90deg') > -1) {
					document.getElementById('surveykong-survey-reminder').style.transform = 'rotate(90deg)';
				}
				else if (document.getElementById('surveykong-buttons-con').style.transform.indexOf('(90deg') > -1) {
					document.getElementById('surveykong-survey-reminder').style.transform = 'rotate(-90deg)';
				}
				
				window.SK.rich = function (evt) {
					SK.showSurvey('{{ campaignStats.campaign.uid }}');
				
					var xhr = new XMLHttpRequest(),
						params = 'cuid={{ campaignStats.campaign.uid }}';
					
					xhr.withCredentials = true;
					
					xhr.onreadystatechange = function () {
						if (xhr.readyState == 4 && xhr.status == 200) {
							document.getElementById('surveykong-survey-reminder').remove();
						}
					};
					xhr.open('POST', '{% if not debug %}https://REPLACE_ME.com{% endif %}{% url 'survey:api_campaign_remove_take_later' %}');
					xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
					xhr.send(params);
				};
			}
		}
		
		window.addEventListener('message', function(event) {
			if (event.data.message == 'removeOverlay') {
				try{document.getElementById('surveykong-overlay').remove()}
				catch{}
				activeEl.focus();
			}
			else if (event.data.message == 'shrinkToIcon') {
				try{document.querySelector('#surveykong-overlay').classList.add('shrinkToIcon')}
				catch{}
			}
			else if (event.data.message == 'sizeSurveyIframe') {
				try{document.getElementById('surveykong-overlay-survey').style.height = (event.data.height+85)+'px'}
				catch{}
			}
			else if (event.data.message == 'sendUrl') {
				try{document.querySelector('#surveykong-overlay-survey iframe').contentWindow.postMessage({message:'parentUrl',url:window.location.href}, '*')}
				catch{}
			}
			else if (event.data.message == 'injectReminder') {
				injectReminderIcon();
			}
		});
		
		injectOnReady(function () {
			if (!document.getElementById('surveykong-buttons-con')) {
				appendToBody('<div id="surveykong-buttons-con" style="position:fixed;z-index:99999998;font-family:IBM Plex Sans,helvetica neue,helvetica,sans-serif;display:flex;"></div>');
				moveAndShowButton(document.getElementById('surveykong-buttons-con'));
			}
		});
		
		
	{% endif %}
	
	{##}
	{##}
	{##  INTERCEPT (and reminder) onload injections  #}
	{##}
	{##}
	
	{% if flags.hasIntercept %}
	
		var shown = false;
		
		{% if 'show_survey' == campaignStats.interceptStatus  %}			
			
			document.addEventListener('mouseleave', function (evt) {
				if (!shown && evt.pageY - window.scrollY <= 0) {
					SK.showSurvey('{{ campaignStats.campaign.uid }}');
					shown = true;
				}
			});
			
			{# TODO: Does page delay auto-inject for intercept? or just invite type? #}
			
		{% elif 'show_reminder' == campaignStats.interceptStatus %}
			
			injectOnReady(injectReminderIcon);
			
		{% endif %}
			
	{##}
	{##}
	{##  INVITE injection  #}
	{##}
	{##}
		
	{% elif flags.hasInvite %}
		
		window.addEventListener('message', function(event) {
			if (event.data.message == 'removeInvite') {
				try{document.getElementById('surveykong-invite-card').remove()}
				catch{}
			}
			else if (event.data.message == 'sizeInvite') {
				try{document.getElementById('surveykong-invite-card').height = event.data.height}
				catch{}
			}
		});
		
		{% if 'show_survey' == campaignStats.interceptStatus %}
		
			injectOnReady(SK.showInvite);
		
		{% endif %}
	
	{% endif %}
	
	{##}
	{##}
	{#  BUTTON injection  #}
	{##}
	{##}
	
	{% if flags.hasButton %}
		
		function injectSurveyButton () {
			if (!document.getElementById('surveykong-survey-button')) {
				document.getElementById('surveykong-buttons-con').innerHTML += `<a id="surveykong-survey-button" href="#" onclick="SK.showSurvey('{{ buttonCampaign.uid }}');return false;" style="display:block;background-color:{{ buttonCampaign.button.background_color }};color:{{ buttonCampaign.button.text_color }};padding:.5rem;text-decoration:none;">{{ buttonCampaign.button.text }}</a>`;
			}
		}
		
		injectOnReady(injectSurveyButton);
		
	{% endif %}
	


{##}
{##}
{#  ADMIN stuff below  #}
{##}
{##}

{% if request.user.hasAdminAccess and flags.hasIntercept %}

	function injectAdminBarrel () {
		if (!document.getElementById('surveykong-admin-barrel')) {
			appendToBody(`<a id="surveykong-admin-barrel" href="#" onclick="window.parent.postMessage({message: 'showAdminPanel'},'*');return false;" style="position:fixed;top:32px;right:0;width:1.5rem;height:1.5rem;z-index:99999;"><span>{{ templateHelpers.html.icons.barrel|safe }}</span></a>`);
		}
		if (!document.getElementById('surveykong-admin-panel')) {
			appendToBody(`<style>#surveykong-admin-panel {transition: all .8s cubic-bezier(0.2,1,0.2,1);transform: translate3d(101%,0,0)}#surveykong-admin-panel.show {box-shadow:-2px 2px 15px rgba(0,0,0,0.7);transform: translate3d(0,0,0)}</style><iframe id="surveykong-admin-panel" style="z-index:99999999;position:fixed;top:24px;right:-1px;width:24rem;height0:20rem;background:#fff;" frameborder="0" marginwidth="0" marginheight="0" scrolling="no" title="SurveyKong survey" src="{% if not debug %}https://REPLACE_ME.com{% endif %}{% url 'survey:survey_iframe_admin_debug_box' uid=campaignStats.campaign.uid %}"></iframe>`);
		}	
	}

	window.addEventListener('message', function(event) {
		if (event.data.message == 'hideAdminPanel') {
			try{
				document.getElementById('surveykong-admin-panel').classList.remove('show');
			}
			catch{}
		}
		else if (event.data.message == 'sizeAdminPanel') {
			document.getElementById('surveykong-admin-panel').height = event.data.height;
		}
		else if (event.data.message == 'showAdminPanel') {
			document.getElementById('surveykong-admin-panel').classList.add('show')
		}
		else if (event.data.message == 'forceIntercept') {
			SK.showSurvey('{{ campaignStats.campaign.uid }}',true);
			shown = true;
		}
	});
	
	injectOnReady(injectAdminBarrel);
	
{% endif %}
	
})();
