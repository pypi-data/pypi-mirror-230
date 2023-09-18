
# -*- coding: utf-8 -*-

import math
import numpy as np
import pandas as pd
import scipy.stats as st
import matplotlib.pyplot as plt
import warnings as warnings
import collections
import plotnine as pn
# sklearn
from sklearn import metrics
from sklearn.preprocessing import LabelBinarizer
# Statsmodels
import statsmodels as smt
from statsmodels.tools import eval_measures
from statsmodels.stats.outliers_influence import OLSInfluence, GLMInfluence
import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.stats.api as sms
import statsmodels.stats.stattools as stattools
import statsmodels.stats.diagnostic as diagnostic

# Lag function
def lag(x,n=1):
    """
    Lag a Time Series

    Compute a lagged version of a time series, shifting the time base back by a given number of observations.

    Parameters:
    -----------
    x : A vector or matrix or univariate time series
    n : int, default=1
        the number of lags (in units of observations)
    
    Return:
    --------
    Returns suitably shifted 
    """
    if n==0:
        return x
    elif isinstance(x,pd.Series):
        return x.shift(periods=n)
    elif isinstance(x,np.array):
        x = pd.Series(x)
        return x.shift(periods=n)
    else:
        x = x.copy()
        x[n:] = x[0:-n]
        x[:n] = np.nan
        return x

# Diff Function
def diff(x,lags=1):
    """
    Lagged Differences

    Parameters
    ----------
    x : Series or 1D-array

    Return
    ------
    Returns suitably lagged 
    """
    if isinstance(x,pd.Series):
        x = x
    else:
        x = pd.Series(x)
    
    return x.diff(periods=lags)

# Extract AIC
def extractAIC(self):
    """
    Akaike information criterion.

    Parameters
    ----------
    self : an instance of statsmodels model class.

    Returns
    -------
    aic : float
    """
    return self.aic

def extractBIC(self):
    """
    Bayesian information criterion.

    Parameters
    ----------
    self : an instance of statsmodels model class.

    Returns
    -------
    bic : float
    """
    return self.bic

def extractAICC(self):
    """
    Akaike information criterion with correction.

    Parameters
    ----------
    self : an instance of statsmodels model class.

    Returns
    -------
    aicc : float
    """
    # Number of observations
    nobs = self.nobs
    # Log - likelihood
    llf = self.llf
    # Number of parameters
    k = len(self.params)
    return eval_measures.aicc(llf=llf,nobs=nobs,df_modelwc=k)

# Extract coefficients
def coefficients(self):
    """
    Coefficients of model.

    Parameters:
    -----------
    self : an object for which the extraction of coefficients is meaningful.

    Return:
    -------
    table : table of float
    """
    return self.summary().tables[1]

# Log-likelihood of model
def logLik(self):
    """
    Log-likelihood of model

    Parameters:
    -----------
    self : an object for which the extraction of log-likelihood is meaningful.

    Return
    ------
    llf :float
        Log-likelihood of model
    """
    return self.llf

def LikelihoodRatioTest(full_model,reduced_model=None):
    """
    Likelihood Ratio Test

     A likelihood ratio test compares the goodness of fit of two nested regression models.

    Parameters:
    -----------
    full_model : The complex model
    reduced_model : A reduced model is simply one that contains a subset of the predictor variables in the overall regression model, default = None.

    Return:
    -------
    statistic : float
                Likelihood ratio chi-squared statistic
    dof : int
            Degree of freedom
    pvalue : float
            The chi-squared probability of getting a log-likelihood ratio statistic greater than statistic.
    
    Notes:
    ------
    Likelihood Ratio Test in R, The likelihood-ratio test in statistics compares the goodness of fit of two 
    nested regression models based on the ratio of their likelihoods, specifically one obtained by maximization 
    over the entire parameter space and another obtained after imposing some constraint.

    A nested model is simply a subset of the predictor variables in the overall regression model.
    For instance, consider the following regression model with four predictor variables.
    y = b0 + b1*x1 + b2*x2 + b3*x3 + b4*x4 + e

    The following model, with only two of the original predictor variables, is an example of a nested model.
    y = b0 + b1*x1 + b2*x2 + e

    To see if these two models differ significantly, we can use a likelihood ratio test with the following null and alternative hypotheses.
    Hypothesis :
    H0: Both the full and nested models fit the data equally well. As a result, you should employ the nested model.
    H1: The full model significantly outperforms the nested model in terms of data fit. As a result, you should use the entire model.

    The test statistic for the LRT follows a chi-squared distribution with degrees of freedom equal to the difference in dimensionality of your models. 
    The equation for the test statistic is provided below:
    -2 * [loglikelihood(nested)-loglikelihood(complex)]

    If the p-value of the test is less than a certain threshold of significance (e.g., 0.05), we can reject the null hypothesis and 
    conclude that the full model provides a significantly better fit.

    """
    if reduced_model is None:
        if full_model.model.__class__ == smt.regression.linear_model.OLS:
            # Null Model
            dataset = pd.DataFrame({full_model.model.endog_names : full_model.model.endog})
            null_model = smf.ols(f"{full_model.model.endog_names}~1",data=dataset).fit()
            # Deviance statistic
            lr_statistic = -2*(null_model.llf - full_model.llf)
            # degree of freedom
            df_denom = null_model.df_resid - full_model.df_resid
            # Critical Probability
            pvalue = st.chi2.sf(lr_statistic,df_denom)
            # Store all informations
            Result = collections.namedtuple("LikelihoodRatioTestResult",["statistic","df_denom","pvalue"],rename=False)
            return Result(statistic=lr_statistic,df_denom=df_denom,pvalue=pvalue) 
        else:
            Result = collections.namedtuple("LikelihoodRatioTestResult",["statistic","pvalue"],rename=False)
            return  Result(statistic=full_model.llr,pvalue=full_model.llr_pvalue)
    else:
        # Deviance statistic
        lr_statistic = -2*(reduced_model.llf - full_model.llf)
        # degree of freedom
        df_denom = reduced_model.df_resid - full_model.df_resid
        # Critical Probability
        pvalue = st.chi2.sf(lr_statistic,df_denom)
        # Store all informations
        Result = collections.namedtuple("LikelihoodRatioTestResult",["statistic","df_denom","pvalue"],rename=False)
        return Result(statistic=lr_statistic,df_denom=df_denom,pvalue=pvalue) 

# https://github.com/TristanFauvel/Hosmer-Lemeshow/blob/master/HosmerLemeshow.py
# https://www.bookdown.org/rwnahhas/RMPH/blr-gof.html
def HosmerLemeshowTest(self=None,Q=10,y_true=None,y_prob=None,**kwargs):
    """
    Hosmer-Lemeshow goodness of fit test

    See https://en.wikipedia.org/wiki/Hosmer%E2%80%93Lemeshow_test

    Parameters
    ----------
    self : an instance of class Logit, default=None
    Q : int, optional, default=10
        The number of groups

    Returns
    -------
    result : the result of the test, including Chi2-HL statistics and p-value 

    References:
    -----------
    Hosmer, D. W., Jr., S. A. Lemeshow, and R. X. Sturdivant. 2013. Applied Logistic Regression. 3rd ed. Hoboken, NJ: Wiley.
    Hosmer, David W., and Stanley Lemeshow. 2000. Applied Logistic Regression. Second edtion. New York: John Wiley & Sons.
    """
    if self is None:
        if (y_true is not None) and (y_prob is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                ytrue = y_true
                yprob = y_prob
            else:
                raise ValueError("Error : 'hosmerlemeshowtest' is only for binary classification.")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ytrue = self.model.endog
            yprob = self.predict()
        else:
             raise ValueError("Error: 'hosmerlemeshowtest' only applied to an object of class Logit.")
    
    df = pd.DataFrame({'y' : ytrue,'score' : yprob})
    df["classe"] = pd.qcut(df.score,q=Q,**kwargs)
    # Effectifs par groupe
    n_tot = df.pivot_table(index='classe',values='y',aggfunc='count').values[:,0]
    # Somme des scores par groupe
    s_scores = df.pivot_table(index='classe',values="score",aggfunc="sum").values[:,0]
    # Nombre de positifs par groupes
    n_pos = df.pivot_table(index='classe',values='y',aggfunc='sum').values[:,0]
    # Nombre de négatifs par groupe
    n_neg = n_tot - n_pos
    # Statistic de Hosmer - Lemeshow
    hl_statistic = np.sum((n_pos - s_scores)**2/s_scores) + np.sum((n_neg - (n_tot - s_scores))**2/((n_tot - s_scores)))
    # Degrée de liberté
    df_denom = Q- 2
    # Probabilité critique
    pvalue = st.chi2.sf(hl_statistic,df_denom)
    # Store all informations
    Result = collections.namedtuple("HosmerLemeshowResult",["statistic","df_denom","pvalue"],rename=False)
    return Result(statistic=hl_statistic,df_denom=df_denom,pvalue=pvalue) 

# Mann Whitney Test
def MannWhitneyTest(self=None, y_true=None, y_prob=None):
    """
    Mann - Whitney Test

    Parameters:
    -----------
    self : an instance of class Logit, default=None.
    ytrue : array of int, default = None.
            The outcome label (e.g. 1 or 0)
    yprob : array of float, default = None.
            The predicted outcome probability

    Return:
    -------
    statistic : float
                Mann Whitney statistic
    pvalue : float
            The normal critical probability
    """
    if self is None:
        if (y_true is not None) and (y_prob is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                ytrue = y_true
                yprob = y_prob
            else:
                raise ValueError("Error : 'mannwhitneytest' is only for binary classification.")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ytrue = self.model.endog
            yprob = self.predict()
        else:
             raise ValueError("Error: 'mannwhitneytest' only applied to an object of class Logit.")

    df = pd.DataFrame({'y' : ytrue,'score' : yprob})
    n_moins, n_plus = df.y.value_counts()
    df = df.sort_values(by="score",ascending=True)
    df["rang"] = np.arange(1,len(ytrue)+1)
    # Somme des rangs de chaque groupe
    srang_moins, srang_plus = df.pivot_table(index='y',values="rang",aggfunc="sum").values[:,0]
    # Statistiques
    u_moins = srang_moins - (n_moins*(n_moins+1)/2)
    u_plus = srang_plus - (n_plus*(n_plus+1)/2)
    U = min(u_moins,u_plus)
    # Statistique de Mann - Whitney
    mn_statistic = (U - (n_plus*n_moins)/2)/(np.sqrt((1/12)*(n_moins*n_plus+1)*(n_moins*n_plus)))
    # Pvalue
    pvalue = st.norm.sf(mn_statistic)
    # Store all informations
    Result = collections.namedtuple("MannWhitneyResult",["statistic","pvalue"],rename=False)
    return Result(statistic=mn_statistic,pvalue=pvalue) 

######################################################################## Residuals for models ##############################################################

# Model Residualss
def residuals(self,choice=None):
    """
    Model Residuals

    Parameters
    ----------
    self : an object for which the extraction of model residuals is meaningful.
    choice : {"response","pearson","deviance"}, default = None. 
            if choice = None, then choice is set to "response".
                - "response" : The response residuals
                - "pearson" : Pearson residuals
                - "deviance" : Deviance residuals. (Only used for logistic regression model.)
    
    Returns
    -------
    resid : pd.Series of float.

    References:
    -----------
    https://en.wikipedia.org/wiki/Errors_and_residuals
    """

    if choice is None:
        choice = "response"

    if self.model.__class__ == smt.regression.linear_model.OLS:
        if choice == "response": # The residuals of the model.
            return self.resid 
        elif choice == "pearson": # Pearson residuals
            return self.resid_pearson 
        else:
            raise ValueError("Error : ")
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        if choice == "response": # TThe response residuals : y - p 
            return self.resid_response
        elif choice == "pearson": # Pearson residuals
            return self.resid_pearson 
        elif choice == "deviance": # Deviance residuals
            return self.resid_dev
    elif self.model.__class__ == smt.tsa.arima.model.ARIMA:
        return self.resid
    elif self.model.__class__ == smt.discrete.discrete_model.MNLogit:
        if choice == "response":
            dummies = LabelBinarizer().fit_transform(self.model.endog)
            return pd.DataFrame(dummies - self.predict())
        else:
            raise ValueError(f"Error : 'choice' should be 'response'.")

# Standardized Model residuals
def rstandard(self,choice=None):
    """
    Standardized Model residuals.

    Parameters
    ----------
    self : an object for which the extraction of model residuals is meaningful.
    choice : {""sd_1","predictive"} for linear regression or {"pearson","deviance"} for logistic regression model.
                - "pearson" : Standardized Pearson residuals
                - "deviance" : Standardized deviance residuals
    Returns
    -------
    resid : pd.series of floats
    """

    # Set default choice
    if choice is None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            choice = "sd_1"
        elif self.model.__class__ == smt.discrete.discrete_model.Logit:
            choice = "deviance"
    
    # Extract resid
    if self.model.__class__ == smt.regression.linear_model.OLS:
        influ = OLSInfluence(self)
        if choice == "sd_1":
            return influ.resid_studentized
        elif choice == "predictive":
            return influ.resid_press
        else:
            raise ValueError("Error : 'choice' should be one of 'sd_1', 'predictive'.")
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        influ = GLMInfluence(self)
        hii = influ.hat_matrix_exog_diag
        if choice == "pearson":
            return residuals(self,choice="pearson")/np.sqrt(1 - hii)
        elif choice == "deviance":
            return residuals(self,choice="deviance")/np.sqrt(1 - hii)
        else:
            raise ValueError("Error : 'choice' should be one of 'pearson', 'deviance'.")
    else:
        raise ValueError(f"Error : no applicable method for 'rstandard' applied to an object of class {self.model.__class__}.")

# Studentized residuals    
def rstudent(self):
    """
    Studentized residuals

    Parameters
    ----------
    self : an object of class OLS, Logit

    Returns
    -------
    resid : pd.series of float.

    References:
    -----------
    https://en.wikipedia.org/wiki/Studentized_residual
    """
    if self.model.__class__ == smt.discrete.discrete_model.MNLogit:
        raise ValueError("Error : no applicable method for 'rstudent' applied to an object of class MNLogit.")
    elif self.model.__class__ == smt.miscmodels.ordinal_model.OrderedModel:
        raise ValueError("Error : no applicable method for 'rstudent' applied to an object of class OrderedModel.")
    
    # Studentized residuals for Ordinary Least Squares
    if self.model.__class__ == smt.regression.linear_model.OLS:
        influ = OLSInfluence(self)
        return influ.resid_studentized_external
    # Studentized residuals for logistic model
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        influ = GLMInfluence(self)
        hii = influ.hat_matrix_exog_diag
        dev_res = residuals(self,choice="deviance")
        pear_res = residuals(self,choice="pearson")
        stud_res = np.sign(dev_res)*np.sqrt(dev_res**2 + (hii*pear_res**2)/(1 - hii))
        return stud_res

######################################################################## Metrics for ordinary least squared regression ######################################

# Explained Variance Score
def explained_variance_score(self=None,y_true=None,y_pred=None):
    """
    Explained Variance Ratio regression score function.

    Best possible score is 1.0, lower values are worse.

    Parameters
    ----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,)
            Estimated target values.
    
    Return:
    ------
    score : float
    """

    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            ytrue = self.model.endog
            ypred = self.predict()
        else:
            raise ValueError("Error : 'explained_variance_ratio' only applied to an object of class OLS.")

    return metrics.explained_variance_score(y_true=ytrue,y_pred=ypred)

# R^2 and adjusted R^2.
def r2_score(self=None,y_true=None,y_pred=None,adjust=False):
    """
    $R^2$ (coefficient of determination) regression score function.

    Parameters:
    -----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,)
            Estimated target values.
    adjust : bool, default = False.
            if False, returns r2 score, if True returns adjusted r2 score.
    
    Returns:
    ------
    z : float
        The r2 score or adjusted r2 score.      
    """
    if adjust is False:
        if self is None:
            if (y_true is not None) and (y_pred is not None):
                return metrics.r2_score(y_true=y_true,y_pred=y_pred)
        elif self is not None:
            if self.model.__class__ == smt.regression.linear_model.OLS:
                return self.rsquared
            else:
                raise ValueError("Error : 'r2_score' only applied to an object of class OLS.")
    else:
        if self is None:
            raise ValueError("Error : `adjust` is only for training model.")
        
        if self.model.__class__ != smt.regression.linear_model.OLS:
            raise ValueError("Error : 'r2_score' only applied to an object of class OLS.")
        return self.rsquared_adj

# Mean Squared Error/ Root Mean Squared Error
def mean_squared_error(self=None, y_true=None, y_pred=None,squared=True):
    """
    (Root)Mean Squared Error ((R)MSE) regression loss.

    Read more in the [User Guide](https://scikit-learn.org/stable/modules/model_evaluation.html#mean-squared-error).

    Parameters:
    -----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,)
            Estimated target values.
    squared : bool, default = True
              if True returns MSE value, if False returns RMSE value
             
    Returns:
    ------
    loss : float
            A non-negative floating point value (the best value is 0.0)
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            ytrue = self.model.endog
            ypred = self.predict()
        else:
            raise ValueError(f"Error : 'mean_squared_error' only applied to an object of class OLS.")

    return metrics.mean_squared_error(y_true=ytrue,y_pred=ypred,squared=squared)

# Max Error
def max_error(self=None,y_true=None,y_pred=True):
    """
    Max Error regression loss

    The max_error metric calculates the maximum residual error.

    Read more in the [User Guide](https://scikit-learn.org/stable/modules/model_evaluation.html#max-error).

    Parameters:
    -----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,)
            Estimated target values.
    
    Returns:
    ------
    max_error : float
                A positive floating point value (the best value is 0.0).
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            ytrue = self.model.endog
            ypred = self.predict()
        else:
            raise ValueError("Error : 'max_error' only applied to an object of class OLS.")
    
    return metrics.max_error(y_true=ytrue,y_pred=ypred)

# Mean Absolute Error
def mean_absolute_error(self=None, y_true=None, y_pred=None, percentage=False):
    """
    Mean Absolute (Percentage) Error regression loss.

    Read more in the [User Guide](https://scikit-learn.org/stable/modules/model_evaluation.html#mean-absolute-error).

    Parameters:
    -----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,) or (n_samples, n_outputs)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,) or (n_samples, n_outputs)
            Estimated target values.
    percentage : bool, default = False;
                if True returns MAPE, il False returns MAE
    
    Returns:
    ------
    loss : float
           MA(P)E output is non-negative floating point. The best value is 0.0.
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            ytrue = self.model.endog
            ypred = self.predict()
        else:
            raise ValueError(f"Error : 'mean_absolute_error' only applied to an object of class OLS.")
    
    if percentage:
        return metrics.mean_absolute_percentage_error(y_true=ytrue,y_pred=ypred)
    else:
        return metrics.mean_absolute_error(y_true=ytrue,y_pred=ypred)
    
# Median Absolute Error
def median_absolute_error(self=None,y_true=None,y_pred=None):
    """
    Median Absolute Error regression loss

    Median absolute error output is non-negative floating point. The best value is 0.0. Read more in the [User Guide](https://scikit-learn.org/stable/modules/model_evaluation.html#median-absolute-error).

    Parameters:
    -----------
    self : an instance of class OLS.
    y_true : array-like of shape (n_samples,) or (n_samples, n_outputs)
            Ground truth (correct) target values.
    y_pred : array-like of shape (n_samples,) or (n_samples, n_outputs)
            Estimated target values.
    
    Returns:
    ------
    loss : float
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            ytrue = self.model.endog
            ypred = self.predict()
        else:
            raise ValueError("Error : 'median_absolute_error' only applied to an object of class OLS.")
    
    return metrics.median_absolute_error(y_true=ytrue,y_pred=ypred)
    
##################################################### Pseudo rsquared for logistic regression ####################################################
# See : https://datascience.oneoffcoder.com/psuedo-r-squared-logistic-regression.html

def efron_rsquare(ytrue, yprob):
    """
    Efron's R^2

    Parameters
    ----------
    ytrue : array of int
            The outcome label (e.g. 1 or 0)
    yprob : array of float
            The predicted outcome probability
    
    Return:
    -------
    value : float
    """
    n = float(len(ytrue))
    t1 = np.sum(np.power(ytrue - yprob, 2.0))
    t2 = np.sum(np.power((ytrue - (np.sum(ytrue) / n)), 2.0))
    return 1.0 - (t1 / t2)

def r2_efron(self=None,y_true=None, y_prob=None):
    """
    Efron's R^2

    Parameters:
    -----------
    self : An instance of class Logit
    y_true : array of int. default = None.
            the outcome label (e.g. 1 or 0)
    y_prob : array of float. default = None.
            The predicted outcome probability
    
    Returns:
    -------
    value : float
    """
    if self == None:
        if (y_true is not None) and (y_prob is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                return efron_rsquare(ytrue=y_true,yprob=y_prob)
            else:
                raise ValueError("Error : 'r2_efron' only applied for binary classification.")
        else:
            raise ValueError("Error : ")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            y_true, y_prob = self.model.endog, self.predict()
            return efron_rsquare(ytrue=y_true,yprob=y_prob)
        else:
            ValueError(f"Error : 'r2_efron' only applied to an object of class Logit.")

# McFadden's Pseudo-R2 : Logit, MNLogit and OrderedModel
# https://www.statease.com/docs/v12/contents/advanced-topics/glm/pseudo-r-squared/
def r2_mcfadden(self,adjust=False):
    """
    McFadden's R^2

    Parameters
    ----------
    self : An instance of class Logit, MNLogit and OrderedModel.
    adjust : boolean, default = False
            if True returns adjusted McFadden r2 score, if False returns McFadden r2 score.

    Return:
    -------
    value : float

    References:
    ----------
    J. S. Long. Regression Models for categorical and limited dependent variables. Sage Publications, Thousand Oaks, CA, 1997.
    D. McFadden. Conditional logit analysis of qualitative choice behavior. In P. Zarembka, editor, Frontiers in Econometrics, 
    chapter Four, pages 104-142. Academic Press, New York, 1974.
    """
    if self.model.__class__ not in [smt.discrete.discrete_model.Logit,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
        raise ValueError(f"Error : 'r2_macfadden' only applied to an object of class Logit, MNLogit or OrderedModel.")
    
    if adjust:
        # Number of parameters (e.g. number of covariates associated with non-zero coefficients)
        k = self.df_model - 1
        # Estimated likelihood of the full model
        llf = self.llf
        # Estimated likelihood of the null model (model with only intercept)
        llnull = self.llnull
        return 1.0 - ((llf - k)/llnull)
    else:
        return self.prsquared
    
# MCKelvey & Zavoina R^2
def r2_mckelvey(self=None,y_prob=None):
    """
    McKelvey & Zavoina R^2

    Parameters:
    -----------
    y_prob : array of float
            The predicted probabilities for binary outcome
    
    Return
    ------
    value : float
    """
    if self is None:
        if y_prob is not None:
            yprob = y_prob
    else:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            yprob = self.predict()
        else:
            raise ValueError(f"Error : 'r2_mckelvey' only applied to an object of class Logit.")
    return np.var(yprob) / (np.var(yprob) + (np.power(np.pi, 2.0) / 3.0) )

# Get number of correct outcome
def get_num_correct(ytrue, yprob, threshold=0.5):
    ypred = np.where(yprob > threshold,1.0,0.0)
    return sum([1.0 for p, pred in zip(ytrue,ypred) if p == pred])

# Count R^2
def r2_count(self=None,y_true=None,y_prob=None,threshold=0.5):
    """
    Count R^2

    Parameters
    ----------
    self : an instance of class Logit, default = None.
    y_true : array of int. default = None.
            the outcome label (e.g. 1 or 0)
    y_prob : array of float. default = None.
            The predicted outcome probability
    threshold : classification threshold, default = 0.5.

    Return:
    -------
    value : float
    """
    if self is None:
        if (y_true is not None) and (y_prob is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                n = float(len(y_true))
                num_correct = get_num_correct(ytrue=y_true,yprob=y_prob, threshold=threshold)
                return num_correct / n
            else:
                raise ValueError("Error : 'r2_count' only applied for binary classification.")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            y_true, y_prob = self.model.endog, self.predict()
            n = float(len(y_true))
            num_correct = get_num_correct(ytrue=y_true,yprob=y_prob, threshold=threshold)
            return num_correct / n
        else:
            ValueError(f"Error : 'r2_count' only applied to an object of class Logit.")
    
# Get the most frequence outcome
def get_count_most_freq_outcome(ytrue):
    num_0 = 0
    num_1 = 0
    for p in ytrue:
        if p == 1.0:
            num_1 += 1
        else:
            num_0 += 1
    return float(max(num_0, num_1))

# Adjust count R^2
def r2_count_adj(self=None,y_true=None,y_prob=None,threshold=0.5):
    """
    Adjusted R^2 count

    Parameters
    ----------
    self : an instance of class Logit, default = None.
    y_true : array of int. default = None.
            the outcome label (e.g. 1 or 0)
    y_prob : array of float. default = None.
            The predicted outcome probability.
    threshold : classification threshold, default = 0.5.

    Return
    ------
    score : float
    """

    if self is None:
        if (y_true is not None) and (y_prob is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                correct = get_num_correct(ytrue=y_true,yprob=y_prob,threshold=threshold)
                total = float(len(y_true))
                n = get_count_most_freq_outcome(ytrue=y_true)
                return (correct - n) / (total - n)
            else:
                raise ValueError("Error : 'r2_count_adj' only applied for binary classification.")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            y_true, y_prob = self.model.endog, self.predict()
            correct = get_num_correct(ytrue=y_true,yprob=y_prob,threshold=threshold)
            total = float(len(y_true))
            n = get_count_most_freq_outcome(ytrue=y_true)
            return (correct - n) / (total - n)
        else:
            ValueError("Error : 'r2_count_adj' only applied to an object of class Logit.")

# Cox and Snell R^2
def r2_coxsnell(self):
    """
    Cox and Snell R^2

    Parameters
    ----------
    self : an instance of class Logit, MNLogit or OrderedModel

    Return:
    -------
    value : float
    """
    if self.model.__class__ not in [smt.discrete.discrete_model.Logit,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
        raise ValueError("Error : 'r2_coxsnell' only applied to an object of class Logit, MNLogit or OrderedModel.")
    
    Ln = np.exp(self.llf)
    L0 = np.exp(self.llnull)
    n = self.nobs
    return 1 - (L0/Ln)**(2/n)

# Nagelkerke/Cragg & Uhler's R^2
def r2_nagelkerke(self):
    """
    Nagelkerke/Cragg & Uhler's R^2

    Parameters
    ----------
    self : an instance of class Logit, MNLogit or OrderedModel

    Return:
    -------
    value : float
    """
    if self.model.__class__ not in [smt.discrete.discrete_model.Logit,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
        raise ValueError("Error : 'r2_nagelkerke' only applied to an object of class Logit, MNLogit or OrderedModel.")
    
    L0 = np.exp(self.llnull)
    n = self.nobs
    max_r2coxsnell = 1 - L0**(2/n)
    return r2_coxsnell(self)/max_r2coxsnell

# https://www.statease.com/docs/v12/contents/advanced-topics/glm/tjur-pseudo-r-squared/
def r2_tjur(self):
    """
    Tjur R-squared

    Applied only to logistic regression.

    Parameters:
    ----------
    self : an instance of class Logit

    Returns:
    -------
    value :float

    References:
    -----------
    Tue Tjur. Coefficients of determination in logistic regression models-a new proposal: the coefficient of 
    discrimination. The American Statistician, 63(4):366-372, November 2009.
    """
    if self.model.__class__ != smt.discrete.discrete_model.Logit:
        raise ValueError("Error : 'r2_tjur' only applied to an object of class Logit.")
    
    df = pd.DataFrame({self.model.endog_names : self.model.endog,"prob" : self.predict()})
    # Mean by group
    gmean = df.groupby(self.model.endog_names).mean().values
    return float(gmean[1]) - float(gmean[0])

def r2_kullback(self,adjust=True):
    """

    Calculates the Kullback-Leibler-divergence-based R2 for generalized linear models.

    Parameters:
    -----------
    self : A generalized linear model (Logit, MNLogit, OrderedModel, Poisson)
    adjust : bool, default = True
            if True returns the adjusted R2 value
    
    Returns:
    --------
    value : float

    References:
    -----------
    Cameron, A. C. and Windmeijer, A. G. (1997) An R-squared measure of goodness of fit for some common nonlinear regression models. Journal of Econometrics, 77: 329-342.
    """

    if self.model.__class__ == smt.regression.linear_model.OLS:
        raise ValueError("Error : 'r2_kullback' only applied to a generalized linear model")

    if adjust:
        adj = (self.df_model+self.df_resid)/self.df_resid
    else:
        adj = 1
    
    # Model deviance
    model_deviance = -2*self.llf
    # Null deviance
    null_deviance = -2*self.llnull
    klr2 = 1 -  (model_deviance/null_deviance)*adj
    return klr2

def r2_loo(self):
    raise NotImplementedError("Error : 'r2_loo' is not yet implemented.")

def r2_loo_posterior(self):
    raise NotImplementedError("Error : 'r2_loo_posterior' is not yet implemented.")

def r2_nakagawa(self):
    raise NotImplementedError("Error : 'r2_nakagawa' is not yet implemented.")

def r2_posterior(self):
    raise NotImplementedError("Error : 'r2_posterior' is not yet implemented.")

def r2_somers(self,threshold=0.5):
    """
    Somers' Dxy rank correlation for binary outcomes

    Parameters
    ----------
    self : an instance of class Logit.
    threshold : classification threshold, default = 0.5.

    Returns:
    -------
    Dxy : namedtuple
    """

    if self.model.__class__ != smt.discrete.discrete_model.Logit:
        raise ValueError("Error : 'r2_somers' only applied to an object of class Logit.")
    
    y_true = self.model.endog
    y_pred = np.where(self.predict() < threshold,0.0,1.0)
    return st.somersd(x=y_true,y=y_pred,alternative="two-sided")

def r2_xu(self):
    """
    Xu' R2 (Omega-squared)

    Parameters
    ----------
    self : an instance of class OLS

    Returns:
    --------
    score : float

    References:
    -----------
    Xu, R. (2003). Measuring explained variation in linear mixed effects models.
    Statistics in Medicine, 22(22), 3527–3541. \doi{10.1002/sim.1572}
    """
    if self.model.__class__ != smt.regression.linear_model.OLS:
        raise ValueError("Error : 'r2_xu' only applied to an object of class OLS.")
    
    return 1 - np.var(self.resid,ddof=0)/np.var(self.model.endog,ddof=0)

def r2_zeroinflated(self):
    raise NotImplementedError("Error : 'r2_zeroinflated' is not yet implemented.")

def r2_bayes(self):
    raise NotImplementedError("Error : 'r2_bayes' is not yet implemented.")

#
def r2(self):
    """
    Compute the model's R^2

    Calculate the R2, also known as the coefficient of determination, 
    value for different model objects. Depending on the model, R2, pseudo-R2, 
    or marginal / adjusted R2 values are returned.

    Parameters:
    ----------
    self : an instance of class Ols, Logit, MNLogit or OrderedModel

    Returns:
    ------
    score :float
    """
    if self.model.__class__ == smt.regression.linear_model.OLS:
        return {"R2" : r2_score(self),"adj. R2" : r2_score(self,adjust=True)}
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        return {"Tjur's " : r2_tjur(self)}
    elif self.model.__class__ == smt.discrete.discrete_model.MNLogit:
        return {"MacFadden's" : r2_mcfadden(self)}
    elif self.model.__class__ == smt.miscmodels.ordinal_model.OrderedModel:
        return {"Nagelkerke's" :r2_nagelkerke(self)}
    elif self.model.__class__ == smt.discrete.discrete_model.Poisson:
        return {"MacFadden's" : r2_mcfadden(self)}
    else:
        raise ValueError("Error : 'self' must be an instance of class OLS, Logit, MNLogit, OrderedModel or Poisson")

################################################### Metrics for classification model #########################################################

def accuracy_score(self=None,y_true=None,y_pred=None,threshold=0.5):
    """
    Accuracy classification score

    Read more in the [User Guide](https://scikit-learn.org/stable/modules/model_evaluation.html#accuracy-score).

    Parameters:
    -----------
    self : an instance of class Logit, MNLogit and OrderedModel
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default =None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Returns:
    ------
    score : float
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ == smt.regression.linear_model.OLS:
            raise ValueError("Error : 'accuracy_score' only applied to generalized linear models.")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
        elif self.model.__class__ in [smt.discrete.discrete_model.MNLogit,smt.miscmodels.ordinal_model.OrderedModel]:
            ypred = np.asarray(self.predict()).argmax(1)
    
    return metrics.accuracy_score(y_true=ytrue,y_pred=ypred)

# Error rate
def error_rate(self=None,y_true=None,y_pred=None,threshold=0.5):
    """
    Error rate classification

    Parameters:
    -----------
    self : an instance of class Logit, MNLogit and OrderedModel
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default =None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Returns:
    ------
    error_rate : float
    """
    return 1.0 - accuracy_score(self=self,y_true=y_true,y_pred=y_pred,threshold=threshold)

# Balance accuracy score
def balanced_accuracy_score(self=None,y_true=None,y_pred=None, threshold=0.5):
    """
    Compute the balanced accuracy.

    Parameters:
    -----------
    self : an instance of class Logit.
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default =None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Returns:
    --------
    balanced_accuracy : float
                        Balanced accuracy score.
    """
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'balance_accuracy_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
    
    return metrics.balanced_accuracy_score(y_true=ytrue,y_pred=ypred)

# Average precision score
def average_precision_score(self=None,y_true=None, y_prob = None):
    """
    Compute average precision (AP) from prediction scores.

    Parameters
    ----------
    self : an instance of class Logit.
    y_true : array-like of shape (n_samples,) , default = None.
            True binary labels or binary label indicators.
    y_prob : array-like of shape (n_samples,) , default =None.
            Probabilities of the positive class..

    Returns:
    -------
    average_precision : float.
                        Average precision score.
    """
    if self is None:
        if (y_true is not None) and (yprob is not None):
            ytrue = y_true
            yprob = y_prob
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'average_precision_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            yprob = self.predict()
    
    return metrics.average_precision_score(y_true=ytrue,y_prob=yprob)

# Brier score loss
def brier_score_loss(self=None,y_true=None,y_prob=None):
    """
    Compute the Brier score loss.

    Parameters
    ----------
    self : an instance of class Logit.
    y_true : array-like of shape (n_samples,) , default = None.
            True binary labels or binary label indicators.
    y_prob : array-like of shape (n_samples,) , default =None.
            Probabilities of the positive class.

    Returns:
    -------
    score : float.
            Brier score loss.
    """
    if self is None:
        if (y_true is not None) and (yprob is not None):
            ytrue = y_true
            yprob = y_prob
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'brier_score_loss' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            yprob = self.predict()

    return metrics.brier_score_loss(y_true=ytrue,y_prob=yprob)

# F1 - score
def f1_score(self=None,y_true=None, y_pred=None,threshold=0.5):
    """
    Compute the F1 score

    Parameters:
    -----------
    self : an instance of class Logit.
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default = None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Return:
    ------
    f1_score : float
            F1 score of the positive class in binary classification.
    """

    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'f1_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
    
    return metrics.f1_score(y_true=ytrue,y_pred=ypred)

# Log loss 
def log_loss(self=None,y_true=None, y_pred=None, threshold=0.5):
    """
    Log loss, aka logistic loss or cross-entropy loss.

    Parameters:
    -----------
    self : an instance of class Logit.
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default = None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Return:
    -------
    loss : float
            Log loss, aka logistic loss or cross-entropy loss.
    """

    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'f1_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
    
    return metrics.log_loss(y_true=ytrue,y_pred=ypred)

# Precision score
def precision_score(self=None,y_true=None, y_pred = None,threshold=0.5):
    """
    Compute the precision.

    Parameters:
    -----------
    self : an instance of class Logit.
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default = None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Return:
    -------
    precision : float
            Precision of the positive class in binary classification .
    """
    
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'f1_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
    
    return metrics.precision_score(y_true=ytrue,y_pred=ypred)

# Recall score
def recall_score(self=None, y_true=None, y_pred=None, threshold=0.5):
    """
    Compute the recall.

    Parameters:
    -----------
    self : an instance of class Logit.
    y_true : 1d array-like, or label indicator array, default = None
            Ground thuth (correct) labels
    y_pred : 1d array-like, or label indicator array, default = None.
            Predicted labels, as returned by a classifier.
    threshold : float,  default = 0.5.
            The threshold value is used to make a binary classification decision based on the probability of the positive class.
           
    Return:
    -------
    recall : float.
            Recall of the positive class in binary classification.
    """
    
    if self is None:
        if (y_true is not None) and (y_pred is not None):
            ytrue = y_true
            ypred = y_pred
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'f1_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ypred = np.where(self.predict() < threshold,0,1)
    
    return metrics.recall_score(y_true=ytrue, y_pred=ypred)

def roc_auc_score(self=None, y_true=None, y_prob = None):
    """
    Compute Area Under the Receiver Operating Characteristic Curve (ROC AUC) from prediction scores.

    Parameters
    ----------
    self : an instance of class Logit.
    y_true : array-like of shape (n_samples,) , default = None.
            True binary labels or binary label indicators.
    y_prob : array-like of shape (n_samples,) , default =None.
            Probabilities of the positive class.

    Return:
    -------
    auc : float.
        Area Under the Curve score.
    """

    if self is None:
        if (y_true is not None) and (yprob is not None):
            ytrue = y_true
            yprob = y_prob
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,
                                    smt.discrete.discrete_model.MNLogit,
                                    smt.miscmodels.ordinal_model.OrderedModel]:
            raise ValueError("Error : 'roc_auc_score' function is only applied to an object of class Logit (binary classification).")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            yprob = self.predict()
    
    return metrics.roc_auc_score(y_true=ytrue,y_prob=yprob)

def multiclass_roc(self=None,y_true=None, y_prob=None,multi_class="ovr"):
    """
    Compute Area Under the Receiver Operating Characteristic Curve (ROC AUC) for multiclass targets

    Parameters
    ----------
    self : an instance of class MNLogit.
    y_true : array-like of shape (n_samples,) , default = None.
            True multiclass labels 
    y_prob : array-like of shape (n_samples,) , default =None.
            Probabilities of each class.

    Return:
    -------
    auc : float.
        Area Under the Curve score.
    """

    if self is None:
        if (y_true is not None) and (yprob is not None):
            ytrue = y_true
            yprob = y_prob
    elif self is not None:
        if self.model.__class__ in [smt.regression.linear_model.OLS,smt.discrete.discrete_model.Logit]:
            raise ValueError("Error : 'multiclass_roc' function is only applied to an object of class MNLogit or OrderdModel.")
        ytrue = self.model.endog
        if self.model.__class__ == smt.discrete.discrete_model.MNLogit:
            yprob = self.predict()
    
    if multi_class not in ["ovo","ovr"]:
        raise ValueError("Error : Allowed values for 'multi_class' are `ovo`, `ovr`.")
    
    return metrics.roc_auc_score(y_true=ytrue,y_prob=yprob,multi_class=multi_class)

########################################################################### check

def check_autocorrelation(self,test="dw",nlags=None,maxiter=100):
    """
    Autocorrelated (Serially Correlated) Errors

    Parameters:
    -----------
    self : an instance of class OLS, Logit, MNLogit or OrderedModel.
    test : {'dw','dg','nw','corc','lb'}, default = 'dw'.
            - 'dw' for Durbin-Watson Test
            - 'bg' for 
            - 'nw' for Newey-West HAC Covariance Matrix Estimation
            - 'corc' for Feasible GLS - Cochrane-Orcutt Procedure
            - 'lb-bp' for Ljung-Box test and Box-Pierce test
    nlags : int, default=None
    maxiter : int, default = 100
    
    Return:
    -------
    test : float, dict

    Notes : See  http://web.vu.lt/mif/a.buteikis/wp-content/uploads/PE_Book/4-8-Multiple-autocorrelation.html
    """

    if test == "dw":
        if self.model.__class__ in [smt.regression.linear_model.OLS,smt.discrete.discrete_model.Logit]:
            res = stattools.durbin_watson(resids=residuals(self=self))
        else:
            raise ValueError("Error : 'dw' is only for OLS or Logit class.")
    elif test == "bg":
        if self.model.__class__ == smt.regression.linear_model.OLS:
            names = ['lm', 'lm-pvalue', 'fvalue', 'f-pvalue']
            bgtest = diagnostic.acorr_breusch_godfrey(self,nlags=nlags)
            res = dict(zip(names,bgtest))
        else:
            raise ValueError("Error : 'bg' is only for OLS class.")
    elif test == "nw":
        if self.model.__class__ == smt.regression.linear_model.OLS:
            V_HAC = smt.stats.sandwich_covariance.cov_hac_simple(self, nlags = nlags)
            V_HAC = pd.DataFrame(V_HAC,columns=self.model.exog_names, index=self.model.exog_names)
            model_HAC = self.get_robustcov_results(cov_type = 'HAC', maxlags = nlags)
            coef_model_HAC = model_HAC.summary2().tables[1]
            res = {"cov. " : V_HAC, "coef. model HAC" : coef_model_HAC}
        else:
            raise ValueError("Error : 'nw' is only for OLS class.")
    elif test == "corc":
        model = sm.GLSAR(self.model.endog, self.model.exog)
        model_fit = model.iterative_fit(maxiter = maxiter)
        coef_model_fit = model_fit.summary2().tables[1]
        res = {"coef. " : coef_model_fit,"rho" : float(model.rho)}
    elif test == "lb-bp":
        if self.model.__class__ == smt.regression.linear_model.OLS:
            res = sm.stats.acorr_ljungbox(residuals(self), lags=[nlags],boxpierce=True, return_df=True)
        else:
            raise ValueError("Error : 'lb-bp' is only for OLS class.")
        
    return res

def check_clusterstructure(X):
    raise NotImplementedError("Error : 'check_clusterstructure' is not yet implemented.")

def check_collinearity(self, metrics = "klein"):

    """
    
    metrics : {"klein","farrar-glauber","vif"}
    
    """
    raise NotImplementedError("Error : 'check_collinearity' is not yet implemented.")

def check_concurvity(X):
    raise NotImplementedError("Error : 'check_concurvity' is not yet implemented.")
    
def check_convergence(self):
    raise NotImplementedError("Error : 'check_convergence' is not yet implemented.")

def check_distribution(self, choice = "response"):
    """
    
    Distribution of model family
    
    """
    raise NotImplementedError("Error : 'check_distribution' is not yet implemented.")

def check_factorstructure(self):
    """
    """
    raise NotImplementedError("Error : 'check_factorstructure' is not yet implemented.")

def check_heterogeneity_bias(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_heterogeneity_bias' is not yet implemented.")

def check_heteroscedasticity(self, test = "bp",alpha=0.05,drop=None):
    """
    Test for heteroscedasticity

    Parameters
    ----------
    self : an instance of class OLS.
    test : {"bp","white","gq"}, default = "bp".
            - "bp" for Breusch-Pagan Lagrange Multiplier test for heteroscedasticity.
            - "white" for White’s Lagrange Multiplier Test for Heteroscedasticity.
            - "gq" for Goldfeld-Quandt homoskedasticity test.
    alpha : float, default = 0.05
    drop : {int,float} default = None.
            If this is not None, then observation are dropped from the middle part of the sorted 
            series. If 0<split<1 then split is interpreted as fraction of the number of observations 
            to be dropped. Note: Currently, observations are dropped between split and split+drop, 
            where split and drop are the indices (given by rounding if specified as fraction). 
            The first sample is [0:split], the second sample is [split+drop:]
    
    Return:
    -------
    results : dict
    """

    if self.model.__class__ != smt.regression.linear_model.OLS:
        raise ValueError("Error : 'check_heteroscedasticity' currently only works Gaussian models.")
    
    if test not in ['bp','white','gq']:
        raise ValueError("Error : Allowed values for 'test' are 'bp', 'white' or 'gq'.")
    
    if test in ["bp","white"]:
        names = ['lm', 'lm-pvalue', 'fvalue', 'f-pvalue']
    elif test == 'gq':
        names = ['fvalue','f-pvalue','alternative']
    
    def test_names(test_lb):
        match test_lb:
            case "bp":
                return "Breusch-Pagan"
            case 'white':
                return 'White'
            case 'gq':
                return 'Goldfeld-Quandt'

    if test == "bp": # Breusch-Pagan Lagrange Multiplier test for heteroscedasticity
        test_result = sms.het_breuschpagan(self.resid, self.model.exog)
    elif test == "white": # White’s Lagrange Multiplier Test for Heteroscedasticity.
        test_result = sms.het_white(self.resid, self.model.exog)
    elif test == "gq": # Goldfeld-Quandt homoskedasticity test.
        test_result = sms.het_goldfeldquandt(self.model.endog, self.model.exog,drop=drop)
    
    res = dict(zip(names, test_result))
    if test_result[1] < alpha:
        res["warning"]= f"According to {test_names(test)} Test, Heteroscedasticity (non-constant variance) detected (p < {alpha})."
    return res

def check_homogeneity(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_homogeneity' is not yet implemented.")

def check_itemscale(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_itemscale' is not yet implemented.")

# https://github.com/Sarmentor/KMO-Bartlett-Tests-Python/blob/master/correlation.py
# Computes KMO
def check_kmo(X):
    """
    Computes Kaiser, Meyer, Olkin (KMO) measure

    Parameters
    ----------
    X : DataFrame

    Return
    ------
    KMO : dict
    """

    if not isinstance(X,pd.DataFrame):
            raise TypeError(
            f"{type(X)} is not supported. Please convert to a DataFrame with "
            "pd.DataFrame. For more information see: "
            "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    
    # Correlation matrix
    corr = X.corr(method="pearson")
    # Inverse of the correlation matrix
    inv_corr = np.linalg.inv(corr)
    # Dimesion
    n_row, n_col = corr.shape

    # Partial correlation matrix
    A = np.ones((n_row,n_col))
    for i in np.arange(1,n_row,1):
        for j in np.arange(i,n_col,1):
            # Above the diagonal
            A[i,j] = - (inv_corr[i,j])/math.sqrt(inv_corr[i,i]*inv_corr[j,j])
            # Below the diagonal
            A[j,i] = A[i,j]
    
    # Transform to an aray of array ('matrix' with python)
    corr = np.asarray(corr)

    # KMO value
    kmo_num = np.sum(np.square(corr)) - np.sum(np.square(np.diagonal(corr)))
    kmo_denom = kmo_num + np.sum(np.square(A)) - np.sum(np.square(np.diagonal(A)))
    kmo_value = kmo_num / kmo_denom

    kmo_j = [None]*corr.shape[1]
    #KMO per variable (diagonal of the spss anti-image matrix)
    for j in range(0, corr.shape[1]):
        kmo_j_num = np.sum(corr[:,[j]] ** 2) - corr[j,j] ** 2
        kmo_j_denom = kmo_j_num + np.sum(A[:,[j]] ** 2) - A[j,j] ** 2
        kmo_j[j] = kmo_j_num / kmo_j_denom
    
    Result = collections.namedtuple("KMOTestResults", ["value", "per_variable"])   
    return Result(value=kmo_value,per_variable=kmo_j)

def check_model(self, figsize=None):
    """
    
    
    """

    if figsize is None:
        figsize=(12,10)
    
    fig, axs = plt.subplots(3,2,figsize=figsize)
    
    if self.model.__class__ == smt.regression.linear_model.OLS:
        dataset = pd.DataFrame(np.c_[self.model.endog,self.predict()],columns=[self.model.endog_names,"predicted"])
        # Add Density
        dataset.plot(kind="density",ax=axs[0,0])
        axs[0, 0].set(xlabel=self.model.endog_names,ylabel="Density",title="Posterior Predictive Check")
        # Linearity
        smx,smy = sm.nonparametric.lowess(residuals(self=self),self.predict(),frac=1./5.0,it=5, return_sorted = True).T
        axs[0,1].scatter(self.predict(),residuals(self=self))
        axs[0,1].plot(smx,smy)
        axs[0,1].set(xlabel="Fitted values",ylabel="Residuals",title="Linearity")
        # Homogeneity of Variance
        infl = OLSInfluence(self)
        smx,smy = sm.nonparametric.lowess(np.sqrt(np.abs(infl.resid_studentized_external)),self.predict(),frac=1./5.0,it=5, return_sorted = True).T
        axs[1,0].scatter(self.predict(),np.sqrt(np.abs(infl.resid_studentized_external)))
        axs[1,0].plot(smx,smy)
        axs[1,0].set(xlabel="Fitted values",ylabel=r"$\sqrt{|Std. residuals|}$",title="Homogeneity of Variance")
        # Influential Observation
        hii = infl.hat_matrix_diag
        smx,smy = sm.nonparametric.lowess(infl.resid_studentized_external,hii,frac=1./5.0,it=5, return_sorted = True).T
        axs[1,1].scatter(hii,infl.resid_studentized_external)
        axs[1,1].plot(smx,smy)
        axs[1,1].set(xlabel=r"Leverage$(h_{ii})$",ylabel="Std. residuals",title="Influential Observations")
        # Colinearity
        axs[2,0].set(title="Collinearity",ylabel="Variance Inflation \n Factor (VIF,log-scaled)",ylim=(1,11))
        # Normality of Residuals
        sm.qqplot(infl.resid_studentized_external,line="45",ax=axs[2,1])
        axs[2,1].set(title="Normality of Residuals")
    else:
        raise ValueError("Error: `check_model()` not yet implemented.")
    
    plt.tight_layout()
    plt.show()

def check_multimodal(self):
    """
    Check if a distribution is unimodal or multimodal
    
    """
    # Guassian Mixture
    raise NotImplementedError("Error : 'check_multimodal' is not yet implemented.")

def check_normality(self, test="shapiro", effects = "fixed"):
    """
    Check model for (non-)normality of residuals.

    Parameters:
    ----------
    self : an instance of class OLS
    test : {'shapiro','jarque-bera','agostino'}, default = 'shapiro'
            i
            - 'shapiro' : Perform the Shapiro-Wilk test for normality.
            - 'jarque-bera' : Perform the Jarque-Bera goodness of fit test on sample data.
            - 'agostino' : It is based on D'Agostino and Pearson's, test that combines skew and kurtosis to produce an omnibus test of normality.
    effects : {'fixed','random'}
            Should normality for residuals ("fixed") or random effects ("random") be tested? Only applies to mixed-effects models. May be abbreviated.

    Returns:
    -------
    results : nametuple
                statistic : flaot
                    The test statistic
                pvalue : float
                    The p - value for the hypothseis test

    Notes:
    ------
    check_normality()  checks the standardized residuals (or studentized residuals for mixed models) for normal distribution. 

    References:
    ----------
    D'Agostino, R. B. (1971), “An omnibus test of normality for moderate and large sample size”, Biometrika, 58, 341-348
    D'Agostino, R. and Pearson, E. S. (1973), “Tests for departure from normality”, Biometrika, 60, 613-622
    Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). Biometrika, 52(3/4), 591-611.
    Jarque, C. and Bera, A. (1980) “Efficient tests for normality, homoscedasticity and serial independence of regression residuals”, 6 Econometric Letters 255-259.
    """

    if self.model.__class__ != smt.regression.linear_model.OLS:
        raise ValueError("Error : Checking normality of residuals is only appropriate for linear models.")
    
    if self.model.__class__ == smt.regression.linear_model.OLS:
        resid = rstandard(self,choice="sd_1")
    
    if test == 'shapiro':
        stat = st.shapiro(resid)
    elif test == 'jardque-bera':
        stat = st.jarque_bera(resid)
    elif test == 'agostino':
        stat = st.normaltest(resid)
    Result = collections.namedtuple("NormalityTest",["statistic","pvalue"],rename=False)
    return Result(statistic=stat.statistic,pvalue=stat.pvalue)

def check_outliers(self, method=None):
    """
    Outliers detection (check for influential observations)
    
    """
    raise NotImplementedError("Error : 'check_outliers' is not yet implemented.")

def check_overdispersion(self):
    """
    Overdispersion test

    Parameters
    ----------
    self : an instance of class Poisson.

    Returns :
    -------
    out : namedtuple
          The function outputs the dispersion ratio (dispersion_ratio), the test value (statistic), the degrees of freedom (df_denom)
          and the p-value.

    Notes:
    ------
    Overdispersion occurs when the observed variance is higher than the
    variance of a theoretical model. For Poisson models, variance increases
    with the mean and, therefore, variance usually (roughly) equals the mean
    value. If the variance is much higher, the data are "overdispersed".

    Interpretation of the Dispersion Ratio:
    If the dispersion ratio is close to one, a Poisson model fits well to the
    data. Dispersion ratios larger than one indicate overdispersion, thus a
    negative binomial model or similar might fit better to the data. 
    A p-value < 0.05 indicates overdispersion.

    References:
    -----------
    Gelman, A. and Hill, J. (2007) Data Analysis Using Regression and Multilevel/Hierarchical Models. 
    Cambridge University Press, New York. page 115_

    """
    if self.model.__class__ != smt.discrete.discrete_model.Poisson:
        raise ValueError("Error : Overdispersion checks can only be used for models from Poisson families or binomial families with trials > 1.")
    
    # True values
    y_true = self.model.endog
    # Predicted values
    y_pred = np.exp(self.fittedvalues)

    # Chis-squared statistic
    chisq_statistic = np.sum(((y_true- y_pred)**2)/y_pred)
    # Degree of freedom
    df_denom = self.df_resid
    # critical probability
    pvalue = st.chi2.sf(chisq_statistic,df_denom)
    # Dispersion ratio
    dispersion_ratio = chisq_statistic/df_denom
    
    # Store all informations in a namedtuple
    Result = collections.namedtuple("OverdispersionTestResult",["dispersion_ratio","chisq_statistic","df_denom","pvalue"],rename=False)
    result = Result(dispersion_ratio=dispersion_ratio,chisq_statistic=chisq_statistic,df_denom=df_denom,pvalue=pvalue) 

    # Output of the function
    if pvalue < 0.05 :
        warnings.warn("Overdispersion detected.")
    
    return result

def check_posterior_predictions(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_posterior_predictions' is not yet implemented.")

def check_predictions(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_predictions' is not yet implemented.")

def check_singularity(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_singularity' is not yet implemented.")

def check_sphericity(self):
    """
    Check model for violation of sphericity
    
    
    """
    raise NotImplementedError("Error : 'check_sphericity' is not yet implemented.")

def check_sphericity_bartlett(X,method="pearson"):
    """
    Test of Sphericity

    Parameters
    ----------
    X : DataFrame
    method : {'pearson','spearman'}, default = 'pearson'
            if 'pearson' used Pearson correlation matrix, if 'spearman' used Spearman rank correlation matrix

    Returns:
    --------
    out : namedtuple
        The function outputs the test value (statistic), the degrees of freedom (df_denom)
        and the p-value.
        It also delivers the n_p_ratio if the number of instances (n) divided 
        by the numbers of variables (p) is more than 5. A warning might be issued.
    
    References
    ----------
    [1] Bartlett,  M.  S.,  (1951),  The  Effect  of  Standardization  on  a  chi  square  Approximation  in  Factor
    Analysis, Biometrika, 38, 337-344.
    [2] R. Sarmento and V. Costa, (2017)
    "Comparative Approaches to Using R and Python for Statistical Data Analysis", IGI-Global.
    """

    if not isinstance(X,pd.DataFrame):
            raise TypeError(
            f"{type(X)} is not supported. Please convert to a DataFrame with "
            "pd.DataFrame. For more information see: "
            "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    
    if method not in ['pearson','spearman']:
        raise ValueError("Error : Allowed values for 'method' are 'pearson','spearamn'.")

    # Dimensions of the Dataset
    n, p = X.shape
    n_p_ratio = n / p
    
    # chi-squared statistic
    chisq_statistic = - (n - 1 - (2 * p + 5) / 6) * math.log(np.linalg.det(X.corr(method=method)))
    # Degree of freedom
    df_denom = p * (p - 1) / 2
    # Critical probability
    pvalue = st.chi2.sf(chisq_statistic , df_denom)
    
    # Store all informations in a namedtuple
    Result = collections.namedtuple("BartlettSphericityTestResult", ["statistic", "df_denom", "pvalue"], rename=False)   
    result = Result(statistic=chisq_statistic,df_denom=df_denom,pvalue=pvalue) 

    if n_p_ratio > 5 :
        print("n_p_ratio: {0:8.2f}".format(n_p_ratio))
        warnings.warn("NOTE: we advise  to  use  this  test  only  if  the number of instances (n) divided by the number of variables (p) is lower than 5. Please try the KMO test, for example.")
        
    return result

def check_symmetric(x):
    """
    Check distribution symmetry

    Parameters
    ----------
    x : 1D-array or pd.Series

    Returns:
    -------
    out: nametuple:
        The function outputs the Hotelling and Solomons test, the test value (statistic) and the p-value.

    Notes :
    ------
    Uses Hotelling and Solomons test of symmetry by testing if the standardized
    nonparametric skew (\eqn{\frac{(Mean - Median)}{SD}}) is different than 0.
    """

    if isinstance(x,pd.Series):
        x = x.dropna()
    elif isinstance(x,np.array):
        x = x[np.isfinite(x)]
    
    m = np.mean(x)
    a = np.median(x)
    n = len(x)
    s = np.std(x,ddof=1)
    D = n*(m-a)/s
    z = np.sqrt(2*n)*(m-a)/s
    pvalue = st.norm.sf(abs(z))
    # Store all informations in a namedtuple
    Result = collections.namedtuple("SymmetryTestResult", ["statistic","pvalue"], rename=False)   
    result = Result(statistic=z,pvalue=pvalue) 
    # Warning message
    if pvalue < 0.05:
        warnings.warn("Warning :  Non - symmetry detected (p = %.3f)"%(pvalue))
    return result

def check_zeroinflation(self):
    """
    
    """
    raise NotImplementedError("Error : 'check_zeroinflation' is not yet implemented.")

def posterior_predictive_check(self):
    """
    
    """
    raise NotImplementedError("Error : 'posterior_predictive_check' is not yet implemented.")

def model_performance(self, metrics = "common"):
    """
    Performance of Regression or Classification Models

    Parameters:
    -----------
    self :
    metrics : {"common","all"}, default = "common"

    Return
    ------
    metrics
    
    """

    # Common metrics
    res = {"AIC" :extractAIC(self),"AICC":extractAICC(self),"BIC" :extractBIC(self)}

    if metrics == "all":
        if self.model.__class__  == smt.regression.linear_model.OLS:
            res["r2 score"] = r2_score(self)
            res["r2 score adj."] = r2_score(self,adjust=True)
            res["expl. var. score"] = explained_variance_score(self)
            res["mean abs. error"] = mean_absolute_error(self)
            res["median abs. error"] = median_absolute_error(self)
            res["mean sq. error"] = mean_squared_error(self)
            res["root mean sq. error"] = mean_squared_error(self,squared=False)
            res["mean abs. percentage error"] = mean_absolute_error(self,percentage=True)
        elif self.model.__class__ in [smt.discrete.discrete_model.Logit,
                                      smt.discrete.discrete_model.MNLogit,
                                      smt.miscmodels.ordinal_model.OrderedModel]:
            res["accuracy"] = accuracy_score(self)
            res["r2 mcfadden"] = r2_mcfadden(self)
            res["r2 mcfadden adj."] = r2_mcfadden(self,adjust=True)
            res["r2 coxsnell"] = r2_coxsnell(self)
            res["r2 naglekerke"] = r2_nagelkerke(self)
        elif self.model.__class__ == smt.discrete.discrete_model.Poisson:
            res["pseudo r2"] = 1 - (-2*self.llf)/(-2*self.llnull)
        
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            res["r2 efron"] = r2_efron(self)
            res["r2 mckelvey"] = r2_mckelvey(self)
            res["r2 count"] = r2_count(self)
            res["r2 count adj."] = r2_count_adj(self)
            res["r2 tjur"] = r2_tjur(self)
        

    return res

################################################################## Poisson Regression

# Compare performance
def compare_performance(model=list()):
    """
    Parameters
    ----------
    model : list of training model to compare

    Returns
    -------
    DataFrame
    """

    def evaluate(i,name):
        res = pd.DataFrame({"AIC" : extractAIC(name), # Akaike information criterion.
                            "AICC":extractAICC(name), # 
                             "BIC" : extractBIC(name), # Bayesian information criterion.
                             "Log-Likelihood" : name.llf}, # Log-likelihood of model
                             index=["Model " + str(i+1)])
        if name.model.__class__  == smt.regression.linear_model.OLS:
            res["R-squared"] = name.rsquared
            res["Adj. rsquared"] = name.rsquared_adj
            ytrue, ypred= name.model.endog, name.predict()
            res["RMSE"] = metrics.mean_squared_error(y_true=ytrue,y_pred=ypred,squared=True)
            res["sigma"] = np.sqrt(name.scale)
            res.insert(0,"Name","ols")
        elif name.model.__class__ == smt.discrete.discrete_model.Logit:
            res["Pseudo R-squared"] = name.prsquared  # McFadden's pseudo-R-squared.
            ytrue, yprob = name.model.endog, name.predict()
            ypred = np.where(yprob > 0.5, 1, 0)
            res["log loss"] = metrics.log_loss(y_true=ytrue,y_pred=ypred)
            res.insert(0,"Name","logit")
        elif name.model.__class__ == smt.tsa.arima.model.ARIMA:
            res["MAE"] = name.mae
            res["RMSE"] = np.sqrt(name.mse)
            res["SSE"] = name.sse
            res.insert(0,"Name","arima")
        elif name.model.__class__ == smt.discrete.discrete_model.Poisson:
            res.insert(0,"Name","poisson")
        elif name.model.__class__ == smt.discrete.discrete_model.MNLogit:
            res.insert(0,"Name","multinomial")
        elif name.model.__class__ == smt.miscmodels.ordinal_model.OrderedModel:
            res.insert(0,"Name","ordinal")
        return res
    res1 = pd.concat(map(lambda x : evaluate(x[0],x[1]),enumerate(model)),axis=0)
    return res1
        
# https://github.com/cran/ggROC/blob/master/R/GGROC.R
# https://github.com/xrobin/pROC/blob/master/R/ggroc.R
def ggroc(self=None,
          y_true=None, 
          y_score = None,
          pos_label=None,
          color="steelblue",
          linetype="solid",
          size=0.5,
          alpha=1,
          title= "ROC Curve",
          ggtheme = pn.theme_minimal()):

    if self is None:
        if (y_true is not None) and (y_score is not None):
            n_label = len(np.unique(y_true))
            if n_label == 2:
                ytrue = y_true
                yscore = y_score
            else:
                raise ValueError("Error : 'ggroc' only applied for binary classification.")
    elif self is not None:
        if self.model.__class__ == smt.discrete.discrete_model.Logit:
            ytrue = self.model.endog 
            yscore = self.predict()
        else:
            raise ValueError("Error : 'ggroc' only applied to an object of class Logit (binary classification).")
    
    fpr, tpr, _ = metrics.roc_curve(ytrue,yscore,pos_label=pos_label)
    data = pd.DataFrame({"FPR":fpr,"TPR" : tpr})

    p = (pn.ggplot(data,pn.aes(x="FPR",y="TPR"))+
         pn.geom_line(color=color,linetype=linetype,size=size,alpha=alpha)+
         pn.geom_abline(intercept=0,slope = 1,linetype="dashed")+
         pn.labs(x="specificity",y="sensitivity",title=title))

    # Add theme
    p = p + ggtheme
    return p


# https://www.metalesaek.com/post/count_data/count-data-models/