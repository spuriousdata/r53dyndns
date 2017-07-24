import sys
import random
from functools import partial
from hashlib import sha512 as sha
from argparse import ArgumentParser
from r53dyndns import app, get_db
from r53dyndns.schema import schema


def addowner(args):
    with app.app_context():
        cur = get_db()
        r = cur.execute("SELECT name FROM owners WHERE name=?", (args.owner,))
        if r.fetchone():
            print("Error: owner %s already exists" % args.owner)
            sys.exit(1)
        key = sha(str(random.getrandbits(1024)).encode('utf8')).hexdigest()
        cur.execute("INSERT INTO owners (name, key) VALUES (?, ?)",
                    (args.owner, key))
        cur.commit()
    print(key)


def addzone(args):
    with app.app_context():
        cur = get_db()
        r = cur.execute("SELECT id FROM zones WHERE name=?", (args.zone,))
        if r.fetchone():
            print("Error: zone %s already exists" % args.zone)
            sys.exit(1)

        zone = args.zone if args.zone.endswith('.') else args.zone + '.'
        cur.execute("""INSERT INTO zones
                    (id, owner, aws_access_key, aws_secret_key, name)
                    VALUES (?, ?, ?, ?, ?)""",
                    (args.zone_id, args.owner, args.access_key,
                     args.secret_key, zone))
        cur.commit()
    adddomain(args)
    print("OK")


def adddomain(args, addr=None, typ=None):
    with app.app_context():
        domain = None
        if addr is None:
            domain = ''
            addr = args.address
        else:
            domain = args.domain
        cur = get_db()
        if args.zone_id:
            zoneid = args.zone_id
        else:
            r = cur.execute("SELECT id FROM zones where name=?", (args.zone,))
            zoneid = r.fetchone()['id']

        r = cur.execute("SELECT zone_id FROM domains WHERE name=? AND zone_id=?",
                        (domain, zoneid))

        if r.fetchone():
            print("Error: domain %s in zone %s already exists" %
                  (domain, zoneid))
            sys.exit(1)

        cur.execute("""INSERT INTO domains
                    (zone_id, name, type, value)
                    VALUES (?, ?, ?, ?)""",
                    (zoneid, domain, 'A', addr))
        cur.commit()
    print("OK")


def init_db(args):
    with app.app_context():
        db = get_db()
        cur = db.execute("SELECT * FROM sqlite_master")
        if cur.fetchone():
            print("Error: db is already initialized")
            sys.exit(1)
        db.cursor().executescript(schema)
        db.commit()
    print("OK")


def show(args):
    with app.app_context():
        db = get_db()
        cur = db.execute("""
SELECT
    o.name as owner, o.key as token, z.id as zone_id,
    z.name as zone_name, d.name as domain_name,
    d.type as record_type, d.value as address
FROM owners o
INNER JOIN zones z ON z.owner = o.name
INNER JOIN domains d ON d.zone_id = z.id""")
        current_owner = None
        current_zone = None
        for row in cur.fetchall():
            rowdict = dict(zip(row.keys(), row))
            if rowdict['owner'] != current_owner:
                current_owner = rowdict['owner']
                if args.keys:
                    print("\n\n{owner:<15}:  {token}".format(**rowdict))
                else:
                    print("\n\n{owner:<15}:".format(**rowdict))
            if rowdict['zone_id'] != current_zone:
                current_zone = rowdict['zone_id']
                print("\n  {d:<28}{t:>10}{a:>18}".format(d="DOMAIN", t="TYPE", a="ADDRESS"))
            fqdn = "{}.{}".format(rowdict['domain_name'], rowdict['zone_name'])
            print("  {fqdn:<28}{record_type:>10}{address:>18}".format(fqdn=fqdn, **rowdict))


def usage(parser, args):
    parser.print_help()
    sys.exit(1)


def main():
    parser = ArgumentParser()
    parser.set_defaults(func=partial(usage, parser))
    sp = parser.add_subparsers()

    p = sp.add_parser('initdb', help='initialize database file')
    p.set_defaults(func=init_db)

    p = sp.add_parser('addowner', help='add a zone owner')
    p.add_argument('owner')
    p.set_defaults(func=addowner)

    p = sp.add_parser('addzone', help='add a zone')
    p.add_argument('-o', '--owner', help='zone owner name', required=True)
    p.add_argument('-a', '--access_key', help='aws access key', required=True)
    p.add_argument('-s', '--secret_key', help='aws secret key', required=True)
    p.add_argument('-z', '--zone_id', help='route53 zone id', required=True)
    p.add_argument('-A', '--address', help='apex domain ip address',
                   required=True)
    p.add_argument('zone')
    p.set_defaults(func=addzone)

    p = sp.add_parser('adddomain', help='add a domain')
    p.add_argument('-o', '--owner', help='zone owner name')
    mx = p.add_mutually_exclusive_group(required=True)
    mx.add_argument('-z', '--zone', help='zone name')
    mx.add_argument('-i', '--zone_id', help='zone id')
    p.add_argument('-A', '--address', help='ip address')
    p.add_argument('domain', help='subdomain')
    p.set_defaults(func=adddomain)

    p = sp.add_parser('show', help='show entries')
    p.add_argument('-k', '--keys', help='include keys',
                   action='store_true', default=False)
    p.set_defaults(func=show)

    args = parser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == '__main__':
    main()
