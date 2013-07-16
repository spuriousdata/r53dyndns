import random
from hashlib import sha512 as sha
from django.contrib import admin
from r53dyndns.models import ApiKey, Zone, Domain
from r53dyndns.forms import ZoneForm

class ApiKeyAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(ApiKeyAdmin, self).get_form(request, obj, **kwargs)
        if form.base_fields['key'].initial is None:
            form.base_fields['key'].initial = sha(str(random.getrandbits(1024))).hexdigest()
        return form

class ZoneAdmin(admin.ModelAdmin):
    form = ZoneForm
    list_display = ('zone_name', 'zone_id', 'owner')

admin.site.register(ApiKey, ApiKeyAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Domain)

