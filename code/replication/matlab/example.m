% Example run with test.csv for FamaMacBeth
[y X PART_VAR] = FM_csv_args('test.csv', 12)
BETA = zeros(10, 1);
FamaMacBeth_NW(y, X, PART_VAR, BETA, 'NW', 1)