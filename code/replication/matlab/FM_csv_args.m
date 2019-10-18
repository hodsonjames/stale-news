function [y, X, PART_VAR] = FM_csv_args(file, num_cols)
% Routine for creating y, X, PART_VAR from a file (csv)
% these values are arguments for FamaMacBeth_NW
%
% SYNTAX: ret = FM_csv_args(file, num_cols)
%
%   file: file name
%   num_cols: number of columns
%
  D = importdata(file);
  y = D.data(:,2);
  X = D.data(:,3:num_cols);
  PART_VAR = D.data(:,1);
end