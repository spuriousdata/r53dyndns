import json
import boto3
from r53dyndns import app, get_db, log, settings
from flask import request, make_response


@app.route('/list', methods=['POST', 'GET'])
def list():
    data = []
    cur = get_db()
    r = cur.execute("""
                    SELECT z.id, z.name
                    FROM zones z
                    INNER JOIN owners o
                        ON o.name = z.owner
                    WHERE o.key = ?
                    """,
                    (request.values['apikey'],))
    for zone in [x for x in r.fetchall()]:
        sql = "SELECT name, value FROM domains WHERE zone_id = ?"
        data.append({
            zone['name']: {
                '__id': zone['id'],
                '__domains': dict([(x['name'], x['value'])
                                   for x in cur.execute(sql, (zone['id'],))]),
            }
        })
    return json_response(data)


def json_response(data, code=200):
    resp = make_response(json.dumps(data), 200)
    resp.headers['Content-Type'] = 'application/json'
    return resp


def remote_addr():
    if settings.remote_ip_header:
        return request.headers[settings.remote_ip_header]
    return request.remote_addr


@app.route('/update/<string:fqdn>', methods=['POST', 'GET'])
def update(fqdn):
    try:
        if not fqdn.endswith('.'):
            fqdn += '.'
        if fqdn.count('.') > 2:
            d, z = fqdn.split('.', 1)
        else:
            d, z = '', fqdn

        r = get_db().execute("""
                    SELECT d.name, d.zone_id, d.value,
                             z.aws_access_key, z.aws_secret_key
                    FROM domains d
                    INNER JOIN zones z
                        ON z.id = d.zone_id
                    INNER JOIN owners o
                        ON o.name = z.owner
                    WHERE d.name=? AND z.name=? AND o.key=?""",
                             (d, z, request.values['apikey']))
        rows = r.fetchall()
        if len(rows) > 1:
            raise RuntimeError("Multiple Objects returned for domain query")
        domain = rows[0]
    except IndexError:
        return json_response({
                    'status': 'error',
                    'code': 404,
                    'msg': "Domain does not exist."}, 404)
    except Exception as e:
        raise
        return json_response({
                    'status': 'error',
                    'code': 500,
                    'msg': "Internal Server Error. %s" % repr(e)}, 500)
    else:
        if domain['value'] == remote_addr():
            return json_response({'status': 'OK', 'msg': 'No Changes.'})
        else:
            r53 = boto3.client('route53',
                               aws_access_key_id=domain['aws_access_key'],
                               aws_secret_access_key=domain['aws_secret_key'])

            rr = r53.list_resource_record_sets(
                    HostedZoneId=domain['zone_id'],
                    StartRecordName=fqdn,
                    StartRecordType='A',
                    MaxItems='1',
            )
            rec = rr['ResourceRecordSets'][0]
            rec['ResourceRecords'][0]['Value'] = remote_addr()
            r53.change_resource_record_sets(
                HostedZoneId=domain['zone_id'],
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': rec,
                        }
                    ]
                }
            )
            log.info("Creating record %s(A):%s", fqdn, remote_addr())
            cur = get_db()
            cur.execute(
                "UPDATE domains SET value=? WHERE zone_id=? AND name=?",
                (remote_addr(), domain['zone_id'], domain['name'])
            )
            cur.commit()
            return json_response({'status': 'OK', 'msg': rr})
