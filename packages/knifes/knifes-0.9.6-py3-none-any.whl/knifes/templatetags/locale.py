
"""
Create hreflang tags as specified by Google

https://support.google.com/webmasters/answer/189077?hl=en

因translate_url使用到url的反向解析，url配置必须要有namespace或name
"""

from django import template
from django import urls
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.translation.trans_real import get_languages
register = template.Library()


@register.simple_tag(takes_context=True)
def translate_url(context, lang):
	"""
	Translate an url to a specific language.

	@param context: context
	@param lang: Which language should the url be translated to.
	"""
	current_url = context['request'].build_absolute_uri()
	url = urls.translate_url(current_url, lang)
	return mark_safe(url)


@register.simple_tag(takes_context=True)
def hreflang_tags(context):
	current_url = context['request'].build_absolute_uri()
	hreflang_html = []
	for lang in get_languages().keys():
		url = urls.translate_url(current_url, lang)
		hreflang_html.append('<link rel="alternate" hreflang="{}" href="{}"/>\n'.format(lang, url))
	hreflang_html.append('<link rel="alternate" hreflang="{}" href="{}"/>\n'.format('x-default', urls.translate_url(current_url, settings.LANGUAGE_CODE)))
	return mark_safe(''.join(hreflang_html))
