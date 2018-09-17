import argparse
import gzip
import json
from typing import List, Tuple, Dict
from heapq import nlargest
from statistics import median
from datetime import datetime
# import concurrent.futures


def setup_args():
    parser = argparse.ArgumentParser(description='solutions for OT code test.')
    parser.add_argument(
        '-i', '--input',
        dest='input',
        metavar='FILE',
        type=str,
        required=True,
        help='gzipped file contain dumped JSON objects')

    parser.add_argument(
        '-o', '--output',
        dest='csv_output',
        metavar='FILE',
        type=str,
        required=True,
        help='output csv file')

    parser.add_argument(
        '-c', '--count',
        action='store_true',
        help='count target pairs sharing a connection to at least to diseases')

    args = parser.parse_args()
    return args


def get_dict_from_file(in_file: str):
    # print(f'{datetime.now()}: start to process file')
    tar_dis = {}
    with gzip.open(in_file, 'rb') as f:
        for line in f:
            evi = json.loads(line)
            try:
                key = (evi['target']['id'], evi['disease']['id'])
                if key in tar_dis:
                    tar_dis[key].append(evi['scores']['association_score'])
                else:
                    tar_dis[key] = [evi['scores']['association_score']]
            except Exception as e:
                print('warning: failed to parse a record: %s' % str(e))
                continue
    return tar_dis


def read_and_output_associations(in_file: str, out_file: str, count: bool) -> None:

    # make sure output is writable
    with open(out_file, 'w') as f:
        f.write(
            'target_id,disease_id,median,highest_score,2nd_highest_score,3rd_highest_score' + '\n'
        )

    evi_dict = get_dict_from_file(in_file)
    evi_dict = {
        evi: (median(evi_dict[evi]), evi_dict[evi])
        for evi in evi_dict
    }
    # start to write output
    with open(out_file, 'a') as f:
        for a_pair, median_scores in sorted(evi_dict.items(), key=lambda x: x[1][0]):
            # print(a_pair, scores)
            f.write(
                ','.join(
                    list(a_pair) +
                    [str(median_scores[0])] +
                    # NOTE some scores look like int eg: 1 instead of 1.0
                    [
                        str(ele) for ele in
                        # when fewer values, use NA to fill the columns
                        (nlargest(3, median_scores[1]) + ['NA', 'NA', 'NA'])[:3]
                    ]
                ) + '\n'
            )
    if count:
        # print(f'{datetime.now()}: start to count')
        evi_dict_keys = list(evi_dict.keys())
        evi_dict.clear()
        print(
            'number of target pairs sharing connection to at least two diseases: ',
            count_pairs_sharing_connection(evi_dict_keys)
        )


def count_pairs_sharing_connection(evi_keys: List[Tuple[str,str]]) -> int:
    tar_dis = {}
    for a_pair in evi_keys:
        target, disease = a_pair
        if target in tar_dis:
            tar_dis[target].append(disease)
        else:
            tar_dis[target] = [disease]
    # print(f'{datetime.now()}: tar_dis is completed')

    # loop through dict once, remove single disease targets, and convert list to set
    all_targets = list(tar_dis.keys())
    for a_tar in all_targets:
        temp = set(tar_dis[a_tar])
        if len(temp) > 1:
            tar_dis[a_tar] = temp
        else:
            del(tar_dis[a_tar])

    # loop through dict second time
    all_targets = list(tar_dis.keys())
    eligible_pairs_count = 0

    for i in range(len(all_targets)):
        for j in range(i+1, len(all_targets)):
            # if one target has more than 1 common diseases with another target
            if len(
                tar_dis[all_targets[i]] & tar_dis[all_targets[j]]
            ) > 1:
                eligible_pairs_count += 1
    return eligible_pairs_count

# NOTE tried to use more CPU, did not gain any better performance
# def count_pairs_sharing_connection_2(evi_keys: List[Tuple[str,str]]) -> None:
#     tar_dis = {}
#     for a_pair in evi_keys:
#         target, disease = a_pair
#         if target in tar_dis:
#             tar_dis[target].append(disease)
#         else:
#             tar_dis[target] = [disease]
#     print(f'{datetime.now()}: tar_dis is completed')
#
#     # loop through dict once, remove single disease targets, and convert list to set
#     all_targets = list(tar_dis.keys())
#     for a_tar in all_targets:
#         temp = set(tar_dis[a_tar])
#         if len(temp) > 1:
#             tar_dis[a_tar] = temp
#         else:
#             del(tar_dis[a_tar])
#
#     # loop through dict second time
#     all_targets = list(tar_dis.keys())
#     eligible_pairs_count = 0
#     results = []
#
#     with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
#         for result in executor.map(
#             compare_target_to_others,
#             [(index, all_targets, tar_dis) for index in range(len(all_targets))]
#         ):
#             results.append(result)
#     return sum(results)
#
#
# def compare_target_to_others(index_targets_dict: Tuple[int, List[str], Dict[str, list]]) -> int:
#     index, all_targets, tar_dis = index_targets_dict
#     count = 0
#     for j in range(index+1, len(all_targets)):
#         if len(
#             tar_dis[all_targets[index]] & tar_dis[all_targets[j]]
#         ) > 1:
#             count += 1
#     return count


if __name__ == "__main__":
    # setup arguments
    args = setup_args()
    # print(args)
    read_and_output_associations(args.input, args.csv_output, args.count)
