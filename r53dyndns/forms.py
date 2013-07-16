from boto.route53.connection import Route53Connection as RC
from boto.route53.exception import DNSServerError
from django import forms
from r53dyndns.models import Zone

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone

    def clean_zone_name(self):
        z = self.cleaned_data['zone_name']
        if not z.endswith('.'):
            raise forms.ValidationError("Zone Name must end with '.'")
        return z

    def clean_zone_id(self):
        try:
            zn = self.cleaned_data['zone_name']
        except:
            return self.cleaned_data['zone_id']
        zi = self.cleaned_data['zone_id']
        route = RC(self.cleaned_data['aws_access_key'], self.cleaned_data['aws_secret_key'])
        try:
            zone = route.get_zone(zn)
        except DNSServerError as e:
            if not zi:
                if e.error_code == 'AccessDenied':
                    raise forms.ValidationError("Cannot retrieve ZoneID, you must enter it here")
                else:
                    raise forms.ValidationError(e.error_message)
        else:
            if zi:
                if zi == zone.id:
                    return zi
                else:
                    raise forms.ValidationError("ZoneID does not match Route53 Zone information")
            else:
                self.cleaned_data['zone_id'] = zone.id
        return self.cleaned_data['zone_id']
