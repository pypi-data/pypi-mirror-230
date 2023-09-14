# -*- coding: utf-8 -*-
import yaml
import argparse
from computeNestSupplier.service_supplier.processor.service_processor import ServiceProcessor


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--service_name', type=str, help='Description of service name parameter', required=False)
    parser.add_argument('--file_path', type=str, help='Description of file path parameter')
    parser.add_argument('--access_key_id', type=str, help='Description of key_id parameter')
    parser.add_argument('--access_key_secret', type=str, help='Description of secret parameter')
    args = parser.parse_args()
    if args.file_path is None:
        parser.error('请提供--file_path')
    if args.access_key_id is None:
        parser.error('请提供--access_key_id')
    if args.access_key_secret is None:
        parser.error('请提供--access_key_secret')
    file_path = args.file_path
    access_key_id = args.access_key_id
    access_key_secret = args.access_key_secret
    with open(file_path, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.FullLoader)
    region_id = data['Service']['RegionId']
    service = ServiceProcessor(region_id, access_key_id, access_key_secret)
    if hasattr(args, 'service_name'):
        service_name = args.service_name
        service.process(data, file_path, service_name)
    else:
        service.process(data, file_path)

if __name__ == '__main__':
    main()
