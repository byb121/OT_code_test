import argparse
import gzip
import json
from typing import List, Tuple, Dict, Any
from heapq import nlargest
from statistics import median
from datetime import datetime
from multiprocessing import Pool, cpu_count


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

    parser.add_argument(
        '-p', '--multi_threads',
        action='store_true',
        help='use all cpus')


    args = parser.parse_args()
    return args


def get_dict_from_file(in_file: str):
    print(f'{datetime.now()}: start to process file')
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


def read_and_output_associations(in_file: str, out_file: str, count: bool, multi_threads: bool) -> None:

    # make sure output is writable
    with open(out_file, 'w') as f:
        f.write(
            'target_id,disease_id,median,highest_score,2nd_highest_score,3rd_highest_score' + '\n'
        )

    evi_dict = get_dict_from_file(in_file)
    print(f'{datetime.now()}: parsing data')
    evi_dict = {
        evi: (median(evi_dict[evi]), evi_dict[evi])
        for evi in evi_dict
    }
    # start to write output
    print(f'{datetime.now()}: write to the output')
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
        print(f'{datetime.now()}: start to count')
        evi_dict_keys = list(evi_dict.keys())
        evi_dict.clear()
        result = count_pairs_sharing_connection(evi_dict_keys, multi_threads)
        print(
            f'{datetime.now()}: number of target pairs sharing connection to at least two diseases: {result}')


def count_pairs_sharing_connection(evi_keys: List[Tuple[str,str]], multi_threads: bool) -> int:
    tar_dis = {}
    for a_pair in evi_keys:
        target, disease = a_pair
        if target in tar_dis:
            tar_dis[target].append(disease)
        else:
            tar_dis[target] = [disease]
    print(f'{datetime.now()}: tar_dis is completed')

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
    if(len(all_targets) == 1):
        # if only one target is left
        return 0
    if multi_threads:
        # range step is trying to slice all_targets into cpu*2 chunks.
        # Earlier chunks takes much longer time, 
        # and later chunks runs much faster as fewer comparisons to go through,
        # so having much chunks to ensure faster process onces finishes can pick up a later/faster job.
        slice_index = [i for i in range(0, len(all_targets)-1, int((len(all_targets)-1)/(cpu_count()*2)+1))]
        index_ranges = []
        for i in range(len(slice_index)):
            if(i == 0):
                index_ranges.append((0, slice_index[1]))
                continue
            if(i == len(slice_index) - 1):
                index_ranges.append((slice_index[i]+1, len(all_targets)-1))
                continue
            index_ranges.append((slice_index[i]+1, slice_index[i+1]))

        count_lits = Pool().map(
            count_it_in_a_slice_of_list, [(start, stop, all_targets, tar_dis) for (start, stop) in index_ranges]
        )
        return sum(count_lits)
    else:
        return count_it_in_a_slice_of_list((0, len(all_targets)-1, all_targets, tar_dis))


def count_it_in_a_slice_of_list(args: Tuple[Any]) -> int:
    (start, stop, all_targets, tar_dis) = args
    eligible_pairs_count = 0
    for i in range(start, stop+1):
        for j in range(i+1, len(all_targets)):
            # if one target has more than 1 common diseases with another target
            if len(
                tar_dis[all_targets[i]] & tar_dis[all_targets[j]]
            ) > 1:
                eligible_pairs_count += 1
    return eligible_pairs_count


if __name__ == "__main__":
    # setup arguments
    args = setup_args()
    read_and_output_associations(args.input, args.csv_output, args.count, args.multi_threads)
