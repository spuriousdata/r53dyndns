import json
from functools import wraps

from django.http import HttpResponse,HttpResponseForbidden, \
    HttpResponseNotFound,HttpResponseServerError
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from boto.route53.connection import Route53Connection as RC
from boto.route53.record import ResourceRecordSets as RR, Record
from boto.route53.exception import DNSServerError

from r53dyndns.models import Domain, Zone, ApiKey

import logging
log = logging.getLogger('default')

class R53View(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            k = request.POST['apikey']
            self.apikey = ApiKey.objects.get(key=k)
        except:
            return HttpResponseForbidden('Invalid API Key\n')
        else:
            return super(R53View, self).dispatch(request, *args, **kwargs)

class ListView(R53View):
    def post(self, request, **kwargs):
        data = []
        for zone in self.apikey.owner.zones.all():
            data.append({
                zone.zone_name:{
                    '__id': zone.id,
                    '__domains': dict([(x.domain_name, x.id) for x in zone.domains.all()])
            }})
        return HttpResponse(json.dumps(data), mimetype='text/javascript')

class UpdateView(R53View):
    def post(self, request, fqdn, **kwargs):
        remote_addr = request.META.get('REMOTE_ADDR')
        try:
            if not fqdn.endswith('.'):
                fqdn += '.'
            d,z = fqdn.split('.', 1)
            domain = Domain.objects.get(
                        api_key=self.apikey, 
                        domain_name=d,
                        zone__zone_name=z)
        except Domain.DoesNotExist:
            return HttpResponseNotFound(
                json.dumps({'status':'error', 'code':404, 'msg': "Domain does not exist."}),
                mimetype="text/javascript")
        except Domain.MultipleObjectsReturned:
            return HttpResponseServerError(
                json.dumps({'status':'error', 'code':500, 'msg': "Domain name provided is ambiguous."}),
                mimetype="text/javascript")
        except:
            return HttpResponseServerError(
                json.dumps({'status':'error', 'code':500, 'msg': "Internal Server Error."}),
                mimetype="text/javascript")
        else:
            if domain.record_value == remote_addr:
                return HttpResponse(
                    json.dumps({'status':'OK','msg':'No Changes.'}),
                    mimetype="text/javascript")
            else:
                conn = RC(domain.zone.aws_access_key, domain.zone.aws_secret_key)
                entries = conn.get_all_rrsets(domain.zone.zone_id)
                rr = RR(connection=conn, hosted_zone_id=domain.zone.zone_id)
                for e in entries:
                    if e.type != 'A' or e.name != fqdn:
                        continue

                    log.info("Deleting record %s", fqdn)
                    ch = rr.add_change('DELETE', fqdn, 'A', ttl=e.ttl)
                    [ch.add_value(x) for x in e.resource_records]
                log.info("Creating record %s(A):%s", fqdn, remote_addr)
                rec = rr.add_change('CREATE', fqdn, 'A', ttl=60)
                rec.add_value(remote_addr)
                resp = rr.commit()
                domain.record_value = remote_addr
                domain.save()
                return HttpResponse(
                    json.dumps({'status':'OK','msg':resp}),
                    mimetype="text/javascript")
