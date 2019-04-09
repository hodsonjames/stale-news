function out = FamaMacBeth_NW(y, X, PART_VAR, beta, varargin)
% Routine for calculating Newey-West-adjusted Fama-MacBeth 
% standard errors and also Z1 and Z2 statistics.
%
% SYNTAX: ret = FamaMacBeth_NW(y, X, PART_VAR, BETA, VARARGIN)
%
%   y: vector of dependent variable
%   X: matrix of regressors
%   PART_VAR: vector containing variable by which regressions are 
%     partitioned  (e.g. MONTH, using the Fama-MacBeth approach fon 
%     a data set in which MONTH uniquely identifies a month)
%   BETA: The vector of coefficients under the null hypothesis.
%   LAG_LENGTH: The number of lags to be considered in the Newey-West 
%     approach (if the Abarbanell and Bernard (2000) correction is 
%     specified, this indicates whether the Abarbanell and Bernard (2000) 
%     adjustment should be made (LAG_LENGTH==1) or the simpler approach
%     discussed in Petersen (2007) should    be used (LAG_LENGTH==0).
%   VARARGIN: Leave empty to get unadjusted Fama-MacBeth estimates. 
%     Use either 'NW' followed by the lag length for Newey West (1987) 
%     correction or use 'AB' followed by 1 for Abarbanell and Bernard 
%     (2000) correction or 'AB; followed by 0 for correction
%     discussed in Petersent (2007)
%
%   RET = [b se t Z1 Z2], the estimated coefficients (b), the estimated 
%     standard errors (se), and t-statistics (t), and the Z1 and Z2 
%     statistics.
%   

  k = size(X,2);

  % Get details on partition variable.
  PART = unique(PART_VAR);
  T = length(PART);

  % Create a location for estimated coefficients.
  temp = zeros(k, T, 4);

  % Get Fama-MacBeth standard error
  % First estimate t coefficients, one for each year
  bb=zeros(T,k);
  
  for t=1:T
    
    % Get y and X values for regression t of T
    y2 = y(find(PART_VAR==PART(t)),:);
    X2 = X(find(PART_VAR==PART(t)),:);
    
    % Store estimated coefficient, SEs, t-statistics, and df
    regresult = regress(y2,X2,0);
    temp(:,t,1) = regresult;
    temp(:,t,2) = regresult;
    temp(:,t,3) = regresult;
    temp(:,t,4) = size(X2,1)-size(X2,2);
    
    % Store estimated coefficients for t in BB vector
    bb(t,:) = temp(:,t,1);
  end
  
  % Calculate standard errors using the time-series distribution of the
  % estimated coefficients.
  for i=1:k 
    b(i) = mean(temp(i,:,1));
    se(i) = 1/sqrt(T) * std(temp(i,:,1));
    
    % Z1 statistic
    df = temp(i,:,4);
    tstats = (temp(i,:,1) - beta(i)) ./ temp(i,:,2);
      
    Z1(i) = 1/sqrt(T)*sum(tstats)/sqrt(df/(df-2));  
    
    % Z2 statistic
    Z2(i)=mean(tstats)/(std(tstats)/sqrt(T-1));
  end
  
  % Calculate associated t-statistics.
  if nargin ~= 4
    if nargin < 4 || nargin > 6
    error('Wrong number of arguments');
  end
    if varargin{1} =='NW'
      % Calculate Newey-West standard errors.
      lag_length = varargin{2};
      for i=1:k
        oness=ones(T,1);
        ret=NeweyWestPanelStata(bb(:,i), oness, lag_length, oness, oness, 0);
        se(i)=ret(1,2);
      end
    elseif varargin{1} =='AB'
      % Abarbanell and Bernard (2000) correction
      b1=bb(2:end,:);
      blag=bb(1:end-1,:);
      n = size(bb,1);
      theta=diag(corr(b1, blag))';
      if varargin{2} == 1
        adj = 2 * theta .* (1-theta .^ n);
        adj = adj ./ (n * (1-theta) .^ 2);
      else 
        adj = 0;
      end
      se = se .* sqrt((1+theta) ./(1-theta) - adj);
    end
  end
  
  t = (b-beta') ./ se;
  
  % Return results
  out = [b' se' t' Z1' Z2'];
  
end
