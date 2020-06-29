# OT_code_test

## Requirements

* Requires Python 3.6+.
* Other dependecies are in `requirements.txt`.

## Usage

### For problem A

Codes are in `code_test.py`.

To see the usage:
```
python code_test.py -h
```

### For problem B

Codes are in `process_json.py`.

To see the usage:
```
python process_json.py -h
```

Runtime on the example evidence file is less than 9mins on a 8 core machine.

### Output

The output CSV file of the example evidence file is `evidence_stats.txt.gz` in folder `output`.

My code prints count of target pairs on screen:

```
$ time python process_json.py -i ~/Downloads/17.12_17.12_evidence_data.json.gz -o test.csv -c -p

2020-06-29 00:48:16.243150: start to process file
2020-06-29 00:55:34.812896: parsing data
2020-06-29 00:55:39.852098: write to the output
2020-06-29 00:55:48.089530: start to count
2020-06-29 00:55:49.252798: tar_dis is completed
2020-06-29 00:56:52.228129: number of target pairs sharing connection to at least two diseases: 121114622
python process_json.py -i ~/Downloads/17.12_17.12_evidence_data.json.gz -o  -  753.36s user 16.22s system 148% cpu 8:36.78 total
```

## Testing

Due to the time constrain, only one function of `process_json` is tested (not thoroughly though).
