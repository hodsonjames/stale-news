% Example run with test.csv for FamaMacBeth
[y, X, PART_VAR] = FM_csv_args('test.csv', 12);
BETA = zeros(11, 1);
LAG = double(uint64(0.75 * length(unique(PART_VAR)) ^ (1/3)));
RET = FamaMacBeth_NW(y, X, PART_VAR, BETA, 'NW', LAG);
