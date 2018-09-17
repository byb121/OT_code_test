import argparse
import re
import sys
import requests
from http import HTTPStatus
from statistics import pstdev, mean


API_URL = 'https://api.opentargets.io/v3/platform/public/association/filter'

TESTS = [
    ('target', 'ENSG00000157764', {'min': 1.0, 'max': 1.0, 'mean': 1.0, 'std_dev': 0.0}),
    ('disease', 'EFO_0002422', {'min': 1.0, 'max': 1.0, 'mean': 1.0, 'std_dev': 0.0}),
    ('disease', 'EFO_0000616', {'min': 1.0, 'max': 1.0, 'mean': 1.0, 'std_dev': 0.0})
]


def setup_args():
    parser = argparse.ArgumentParser(description='solutions for OT code test.')
    parser.add_argument(
        '-t', '--target',
        dest='target_id',
        metavar='STRING',
        type=str,
        help='target ID. eg: ENSG00000157764')

    parser.add_argument(
        '-d', '--disease',
        dest='disease_id',
        metavar='STRING',
        type=str,
        help='disease ID. eg: EFO_0002422')

    parser.add_argument(
        '--test',
        action='store_true',
        help='run a suite of tests')

    args = parser.parse_args()
    return args


def query_and_return_stats(disease_id: str = None, target_id: str = None):
    if target_id and disease_id:
        raise RuntimeError('can not take both target_id and disease_id.')
    if not target_id and not disease_id:
        raise RuntimeError('require either a target_id or a disease_id.')

    # if target_id:
    #     validate_id_format(target_id, 'target')
    # if disease_id:
    #     validate_id_format(disease_id, 'disease')

    res = requests.get(API_URL, params={'disease': disease_id, 'target': target_id})
    if res.status_code != HTTPStatus.OK:
        raise RuntimeError('query failed.')
    try:
        data = res.json()['data']
        # assuming return body will always have a float for the value
        overall_association_scores = [d['association_score']['overall'] for d in data]
        # print(overall_association_scores)
    except Exception as e:
        raise RuntimeError('failed to parse query returned body: %s' % str(e))

    # can be an empty list
    if not overall_association_scores:
        raise RuntimeError('API did not return overall scores')

    try:
        return {
                'min': min(overall_association_scores),
                'max': max(overall_association_scores),
                'mean': mean(overall_association_scores),
                'std_dev': pstdev(overall_association_scores)
            }
    except Exception as e:
        sys.exit('failed to parse scores: %s' % str(e))


def test_q_an_r_stats():
    for test in TESTS:
        if test[0] == 'disease':
            assert query_and_return_stats(disease_id=test[1]) == test[2]
        else:
            assert query_and_return_stats(target_id=test[1]) == test[2]


# NOTE seems format can be much more variable than this
# def validate_id_format(id: str, format: str) -> None:
#     if format == 'target':
#         if not re.search(r'^ENSG', id):
#             raise ValueError('unrecognised target id format')
#
#     if format == 'disease':
#         if not re.search(r'^EFO\_', id):
#             raise ValueError('unrecognised disease id format')


if __name__ == "__main__":
    # setup arguments
    args = setup_args()
    # print(args)
    if args.test:
        # run test functions
        test_q_an_r_stats()
    else:
        stats = query_and_return_stats(args.disease_id, args.target_id)
        print(stats)
