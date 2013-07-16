from django.db import models
from django.contrib.auth.models import User

class ApiKey(models.Model):
    owner = models.ForeignKey(User, related_name='keys', null=False)
    key   = models.CharField(max_length=128, blank=False, null=False)

    def __unicode__(self):
        return "%s: %s" % (self.owner, self.key)

class Zone(models.Model):
    aws_access_key = models.CharField(max_length=256, blank=False, null=False)
    aws_secret_key = models.CharField(max_length=256, blank=False, null=False)
    zone_name      = models.CharField(max_length=512, blank=False, null=False)
    zone_id        = models.CharField(max_length=256, blank=True,  null=False)
    owner          = models.ForeignKey(User, related_name='zones', null=False)

    def __unicode__(self):
        return self.zone_name

class Domain(models.Model):
    zone         = models.ForeignKey(Zone, related_name='domains', null=False)
    api_key      = models.ForeignKey(ApiKey, related_name='domains', null=False)
    domain_name  = models.CharField(max_length=512, blank=False, null=False)
    record_type  = models.CharField(max_length=10, blank=True, null=False, default='A')
    record_value = models.CharField(max_length=15, blank=True, null=False)
    
    def __unicode__(self):
        return "%s.%s" % (self.domain_name, self.zone)
