from django.conf import settings as st
from django import template
from datetime import datetime
from django.utils import timezone

register = template.Library()

try:
    timezone_settings = st.TIME_ZONE
except:
    timezone_settings = "UTC"

@register.simple_tag
def date(timezone_name=timezone_settings):
    user_timezone = timezone.get_timezone(timezone_name)
    current_time = datetime.now(user_timezone)
    formatted_time = current_time.strftime("%d/%m/%Y")

    return str(formatted_time)

@register.simple_tag
def year_now():
    return str(datetime.now().year)