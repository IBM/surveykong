{% load static %}
<script>
	window.BH = {
		'urls': {
			'cdnPath': '{{ CDN_FILES_URL }}',
		}
	};
</script>

<script src="{% static 'shared/js/jquery.min.js' %}"></script>
<script src="{% static 'shared/js/select2.min.js' %}"></script>
<script src="{% static 'shared/js/micromodal.min.js' %}"></script>
<script src="{% static 'shared/js/bo-common.min.js' %}"></script>
<script src="{% static 'shared/js/site-common.js' %}"></script>
