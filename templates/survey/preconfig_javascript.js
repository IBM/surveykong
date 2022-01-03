(function () {
	var xhr = new XMLHttpRequest();
	
	xhr.withCredentials = true;
	
	xhr.onreadystatechange = function () {
		if (xhr.readyState == 4 && xhr.status == 200) {
			var script = document.createElement("script");
			script.type = "text/javascript";
			script.text = xhr.responseText;
			document.body.appendChild(script);
		}
	};
	xhr.open('POST', '{% if not debug %}https://REPLACE_ME.com{% endif %}{% url 'survey:project_config_javascript' uid=projectUid %}');
	xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhr.send('url='+window.location.href);
})();
