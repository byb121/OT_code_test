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

Runtime on the example evidence file is about 17mins.

### Output

The output CSV file of the example evidence file is `evidence_stats.txt.gz` in folder `output`.

My code prints count of target pairs on screen:
```
$ time python process_json.py -i ~/Downloads/17.12%2F17.12_evidence_data.json.gz -o output/evidence_stats.txt --count
number of target pairs sharing connection to at least two diseases:  121114622

real	16m22.277s
user	15m56.546s
sys	0m10.792s
```

## Testing

Due to the time constrain, only one function of `process_json` is tested (not thoroughly though).
