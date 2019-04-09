function ret = NeweyWestPanelStata(y, X, L, FIRM_VAR, TIME_VAR, stat)
% Function that runs OLS and returns standard errors based
% Newey-West autocorrelation consistent covariance estimator.
% This routine can be used for a single time-series or panel data. The
% routine produces identical results to Stata's newey.ado file and 
%
% SYNTAX: ret = NeweyWestPanelStata(y, X, L, FIRM_VAR, TIME_VAR, stat)
%
% The value returned depends on stat:
%  0: [beta, standard errors, t-statistics]
%  1: residuals
  
  % Sort the data by FIRM_VAR and then TIME_VAR
  FIRMS = unique(FIRM_VAR);
  j = 0;
  for i=1:length(FIRMS);
    rows = find(FIRM_VAR==FIRMS(i));
    [temp, ix] = sort(TIME_VAR(rows,:));
    rows = rows(ix,:);
    if i==1
      y2 = y(rows,:);
      X2 = X(rows,:);
      F2 = FIRM_VAR(rows,:);
      T2 = TIME_VAR(rows,:);
    else
      y2 = [y2; y(rows,:)];
      X2 = [X2; X(rows,:)];
      F2 = [F2; FIRM_VAR(rows,:)];
      T2 = [T2; TIME_VAR(rows,:)];
    end
  end
  
  % Reassign the variables after sorting.
  y = y2;
  X = X2;
  FIRM_VAR = F2;
  TIME_VAR = T2;
  
  % calculate Bhat
  b = pinv(X)*y;
 
  % Determine the size of the matrix of regressors
  [N, k] =size(X);
 
  % Generate residuals
  e = y - X * b;
 
  % Calculate the Newey-West autocorrelation consistent covariance
  % estimator. See p.464 of Greene (2000) for more information
  % Note that there was a typo in the 2000 edition that was corrected
  % in the 2003 edition.
  Q = 0;
  for l = 0:L
    w_l = 1-l/(L+1);
    for t = l+1:N
      if (l==0)   % This calculates the S_0 portion
        Q = Q  + e(t) ^2 * X(t, :)' * X(t,:);
      else        % This calculates the off-diagonal terms
        if FIRM_VAR(t,1) == FIRM_VAR(t-l,1)
        Q = Q + w_l * e(t) * e(t-l)* ...
          (X(t, :)' * X(t-l,:) + X(t-l, :)' * X(t,:));
        end
      end
    end
  end
  Q = 1/(N-k) * Q;
  
  % Calculate Newey-White standard errors
  varBhat = N * inv(X' * X) * Q * inv(X' * X);

  % calculate standard errors and t-stats
  se = sqrt(diag(varBhat));
  t = b ./ se;
    
  if (stat==1) % return residuals
    ret = e;
  elseif (stat==0) % return SSR
    ret = [b se t];
  end
end
