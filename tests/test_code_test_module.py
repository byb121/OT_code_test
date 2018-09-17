import pytest
import os
from ..process_json import get_dict_from_file

TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def test_read_dict_from_file():
    result = get_dict_from_file(os.path.join(TEST_DIR, 'test_2.json.gz'))
    expected_dict = {
        ('ENSG00000140859', 'EFO_0000519'): [1.0],
        ('ENSG00000197170', 'EFO_0000708'): [1.0],
        ('ENSG00000198650', 'Orphanet_28378'): [1],
        ('ENSG00000102468', 'EFO_0003761'): [1.0],
        ('ENSG00000043591', 'EFO_0000612'): [1.0],
        ('ENSG00000073282', 'EFO_0000292'): [1.0],
        ('ENSG00000204264', 'EFO_0000519'): [1.0],
        ('ENSG00000115129', 'EFO_0002916'): [1.0],
        ('ENSG00000274286', 'EFO_0003761'): [1.0],
        ('ENSG00000112164', 'EFO_0001360'): [1.0]
    }
    assert result == expected_dict
