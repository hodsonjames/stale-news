function ret = regress(y, X, stat)
% This function estimates OLS coefficients from a regression of
% y on X. Standard errors are "regular" OLS standard errors.
%
% SYNTAX: ret = regress(y, X, stat)
%
% The value returned (ret) depends on stat:
%  0: [beta, standard errors, t-statistics]
%  1: residuals
        
    % calculate Bhat
    b = pinv(X)*y; % inv(X'*X)*X'*y;

    [N, k] =size(X);

    % calculate residuals
    e = y - X * b;
    s2 = e' * e/(N - k);
    
    if (stat==1) % return residuals
      ret = e;
    elseif (stat==0) % return [beta, standard errors, t-statistics]
      % Following code borrowed from "Spatial Econometrics" library  
      if N < 10000
        [q r] = qr(X,0);
        xpxi = (r'*r)\eye(k);
      else % use Cholesky for very large problems
        xpxi = (X'*X)\eye(k);
      end;
      varBhat = s2 * xpxi;
        
      % calculate standard errors and t-stats
      se = sqrt(diag(varBhat));
      t = b ./ se;
   
      ret = [b se t];
    end
end
