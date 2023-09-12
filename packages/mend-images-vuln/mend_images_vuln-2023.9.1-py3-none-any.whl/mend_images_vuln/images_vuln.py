import argparse
import csv
import logging
import os
from datetime import datetime

from mend_images_vuln._version import __tool_name__, __description__
from mend_images_vuln.mend_api import MendAPI
from mend_images_vuln.mend_const import aliases, varenvs

logger = logging.getLogger(__tool_name__)
logger.setLevel(logging.DEBUG)
try:
    is_debug = logging.DEBUG if os.environ.get("DEBUG").lower() == 'true' else logging.INFO
except:
    is_debug = logging.INFO

formatter = logging.Formatter('[%(asctime)s] %(levelname)5s %(message)s', "%Y-%m-%d %H:%M:%S")
s_handler = logging.StreamHandler()
s_handler.setFormatter(formatter)
s_handler.setLevel(is_debug)
logger.addHandler(s_handler)
logger.propagate = False


def try_or_error(supplier, msg):
    try:
        return supplier()
    except:
        return msg


def parse_args():
    parser = argparse.ArgumentParser(description=__description__)
    got_args = parser.parse_known_args()
    if len(got_args[1]) == 1 and got_args[1][0] in ["--version", "-v"]:
        parser.add_argument(*aliases.get_aliases_str("version"), help="Current version", action='store_true')
    else:
        parser.add_argument(*aliases.get_aliases_str("userkey"), help="Mend user key", dest='ws_user_key',
                            default=varenvs.get_env("wsuserkey"), required=not varenvs.get_env("wsuserkey"))
        parser.add_argument(*aliases.get_aliases_str("email"), help="Mend user email", dest='ws_email',
                            default=varenvs.get_env("wsemail"), required=not varenvs.get_env("wsemail"))
        parser.add_argument(*aliases.get_aliases_str("apikey"), help="Mend API key", dest='ws_token',
                            default=varenvs.get_env("wsapikey"), required=not varenvs.get_env("wsapikey"))
        parser.add_argument(*aliases.get_aliases_str("projectkey"), help="Mend product/project scope",
                            dest='scope_token',
                            default=varenvs.get_env("wsscope"))
        parser.add_argument(*aliases.get_aliases_str("url"), help="Mend server URL", dest='ws_url',
                            default=varenvs.get_env("wsurl"), required=not varenvs.get_env("wsurl"))
        parser.add_argument(*aliases.get_aliases_str("output"), help="Output directory", dest='out_dir',
                            default=os.getcwd())
        parser.add_argument(*aliases.get_aliases_str("separate"), help="Separated CSV files or one CSV file", dest='separated',
                            default='true')
        parser.add_argument('--proxy', help="Proxy URL", dest='proxy',
                            default=os.environ.get("HTTP_PROXY", ''))
        parser.add_argument('--proxyUsername', help="Proxy Username", dest='proxyuser',
                            default=os.environ.get("HTTP_PROXY_USERNAME", ''))
        parser.add_argument('--proxyPassword', help="Proxy Password", dest='proxypsw',
                            default=os.environ.get("HTTP_PROXY_PASSWORD", ''))

    return parser.parse_known_args()[0]


def get_image_vulnerabilities(image_id, image_name):
    try:
        vulns = conn.call_mend_api(api_type="GET", token=conn.orguuid, entity="orguuid",
                                   sub_entity=f"images/{image_id}/vulnerabilities?page=0&size=5000",
                                   cloud_native=True)['data']
        # ToDo  Maybe need to use different structure of separated files and union file in future
        '''
        if args.separated.lower() == "true":
            data = [{"VULNERABILITY ID": x['vulnerabilityId'], "PACKAGE": x['packageName'],
                     "PACKAGE VERSION": x['packageVersion'], "PACKAGE TYPE": x['packageType'],
                     "SEVERITY": x['severity'],
                     "FIX VERSION": x['fixVersion'], "DETAILS": x['description'], "RISK": x['risk']} for x in vulns]
        else:
            data = [{"IMAGE NAME": image_name, "VULNERABILITY ID": x['vulnerabilityId'], "PACKAGE": x['packageName'],
                     "PACKAGE VERSION": x['packageVersion'], "PACKAGE TYPE": x['packageType'], "SEVERITY": x['severity'],
                     "FIX VERSION": x['fixVersion'], "DETAILS": x['description'], "RISK": x['risk']} for x in vulns]
        '''
        data = [{"IMAGE NAME": image_name, "VULNERABILITY ID": x['vulnerabilityId'], "PACKAGE": x['packageName'],
                 "PACKAGE VERSION": x['packageVersion'], "PACKAGE TYPE": x['packageType'], "SEVERITY": x['severity'],
                 "FIX VERSION": x['fixVersion'], "DETAILS": x['description'], "RISK": x['risk']} for x in vulns]
        if not data:
            logger.info(f"Not found vulnerabilities in the image {image_name}")
        return data
    except Exception as err:
        logger.error(f"Error while getting vulnerability data from the image {image_name}. Details {err}")
        return []


def create_csv(image_data: list):
    for image_data_ in image_data:
        for image_name_, image_dat_ in image_data_.items():
            csv_file = os.path.join(args.out_dir, f"{image_name_.replace('/','_')}.csv")
            header = image_dat_[0].keys()
            with open(csv_file, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=header)
                writer.writeheader()  # Write the header row
                writer.writerows(image_dat_)  # Write the JSON objects as rows
            logger.info(f"CSV file {image_name_.replace('/','_')} created in the folder {args.out_dir}")


def main():
    global args
    global conn
    args = parse_args()
    try:
        conn = MendAPI(user_key=args.ws_user_key, user_login=args.ws_email, url=args.ws_url, token=args.ws_token,
                       proxy_url=args.proxy, proxyuser=args.proxyuser, proxypsw=args.proxypsw)
        if not conn.jwt_token:
            logger.error(f"Authentication with email {conn.user_login} was failed. The instance {args.ws_url}")
            exit(-1)

        images = try_or_error(lambda: conn.call_mend_api(api_type="GET", token=conn.orguuid, entity="orguuid", sub_entity="images", cloud_native=True)["data"], [])
        image_data_aggr = []
        image_data_sep = []
        for image in images:
            image_el_data = get_image_vulnerabilities(image_id=image['uuid'], image_name=image['name'] if image['name'] else image['repo'])
            if image_el_data:
                logger.info(f"Proceeded image {image['name'] if image['name'] else image['repo']}")
                if args.separated.lower() == "true":
                    image_data_sep.append(
                        {image['name'] if image['name'] else image['repo']: image_el_data}
                    )
                else:
                    image_data_aggr.extend(image_el_data)

        if image_data_aggr:
            logger.info("Creating CSV file...")
            create_csv([{f"images_vuln_{datetime.now().strftime('%Y-%m-%d')}": image_data_aggr}])
        elif not image_data_aggr and not image_data_sep:
            logger.info(f"Not found vulnerabilities.")
        else:
            logger.info("Creating CSV files...")
            create_csv(image_data_sep)
    except Exception as err:
        logger.error(f"Error was raised {err}")


if __name__ == "__main__":
    main()
