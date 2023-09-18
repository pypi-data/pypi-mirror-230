# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from more_itertools import powerset
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.metrics import (
    # Regression metrics
    explained_variance_score,
    max_error,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    median_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
    # Classification metrics
    confusion_matrix,
    accuracy_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

# https://jbhender.github.io/Stats506/F18/GP/Group5.html

def powersetmodel(DTrain=pd.DataFrame,
                  DTest=None,
                  split_data = True,
                  model_type ="linear",
                  target=str,
                  test_size=0.3,
                  random_state=None,
                  shuffle=True,
                  stratity=None,
                  num_from=None,
                  num_to=None):
    """
    This function return all subsets models giving a set of variables.

    Parameters
    ----------
    DTrain : DataFrame
            Training sample
    DTest : DataFrame, default = None
            Test sample
    split_data : bool, default= True. If Data should be split in train set and test set. Used if DTest is not None. 
    model_type : {"linear","logistic"}, default = "linear".
    target : target name,
    test_size : float or int, default=None
                 If float, should be between 0.0 and 1.0 and represent the proportion of the dataset to include in 
                 the test split. If int, represents the absolute number of test samples. If None, the value is set 
                 to the complement of the train size. If train_size is also None, it will be set to 0.25.
                 See : "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html"
    random_state : int, RandomState instance or None, default=None
                   Controls the shuffling applied to the data before applying the split. 
                   Pass an int for reproducible output across multiple function calls. 
                   See "https://scikit-learn.org/stable/glossary.html#term-random_state"
    shuffle : bool, default=True
               Whether or not to shuffle the data before splitting. If shuffle=False then stratify must be None.
    stratify : array-like, default=None.
               If not None, data is split in a stratified fashion, using this as the class labels. 
               Read more in the "https://scikit-learn.org/stable/modules/cross_validation.html#stratification"
    """

    # Set testing samples
    if not isinstance(DTrain,pd.DataFrame):
        raise TypeError(f"{type(DTrain)} is not supported. Please convert to a DataFrame with "
                        "pd.DataFrame. For more information see: "
                        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    
    if DTest is not None:
        if not isinstance(DTest,pd.DataFrame):
            raise TypeError(f"{type(DTest)} is not supported. Please convert to a DataFrame with "
                            "pd.DataFrame. For more information see: "
                            "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    else:
        if split_data:
            DTrain, DTest = train_test_split(DTrain,test_size=test_size,random_state=random_state,shuffle=shuffle,stratify=stratity)
        else:
            DTest = DTrain
        
    # Create formula : https://stackoverflow.com/questions/35518477/statsmodels-short-way-of-writing-formula
    def create_formula(y=str,x=list[str]):
        return y + ' ~ ' + ' + '.join(x)
    
    def predictor(x):
        return '+'.join(x)

    # List of features
    features = list(DTrain.drop(columns=target).columns)
    # Powerset features and Remove first element
    list_features = list(map(set, powerset(features)))[1:]

    # Reduce list_features using num_from and num_to
    if num_from is None:
        num_from = 1
    if num_to is None:
        num_to = len(list_features[-1])
    
    if num_from >= num_to:
        raise ValueError("Error : 'num_from' must be small than 'num_to'.")

    list_features = [num for num in list_features if len(num) in range(num_from,num_to+1,1)]

    ################################################################################
    # General metrics - AIC, BIC
    ################################################################################
    def general_metrics(x,model):
        gen_res = {"predictor" : predictor(x),
                   "count":len(x),
                   "aic":model.aic,
                   "bic":model.bic}
        return pd.DataFrame(gen_res,index=["metrics"])
    
    def likelihood_ratio_test(full_model, ho_model):
        return 2*(full_model.llf - ho_model.llf)

    #################################################################################
    #  Linear regression 
    #################################################################################
    # linear regression metrics
    def ols_metrics(model,ytrue,ypred):
        res = {"rsquared":model.rsquared,
               "adj. rsquared" : model.rsquared_adj,
               "expl. var. score" : explained_variance_score(ytrue,ypred),
               "max error" : max_error(ytrue,ypred),
               "mean abs. error" : mean_absolute_error(ytrue,ypred),
               "mean sq. error" : mean_squared_error(ytrue,ypred),
               "median abs. error" : median_absolute_error(ytrue,ypred),
               "r2 score" : r2_score(ytrue,ypred),
               "mean abs. percentage error" : mean_absolute_percentage_error(ytrue,ypred)}
        return pd.DataFrame(res,index=["metrics"])
    
    # Estimation of ols model
    def ols_estimated(y,x,df1,df2):
        # Create formula
        formula = create_formula(y=y,x=x)
        # Train the model
        model = smf.ols(formula=formula,data=df1).fit()
        # Predict under Test Dataset
        predict = model.predict(df2)
        # Metrics under test sampling
        gen_metrics = general_metrics(x,model)
        lm_metrics = ols_metrics(model,df2[y],predict)
        return gen_metrics.join(lm_metrics) 
    
    # Store ols model
    def ols_model(y,x,df):
        # Create formula
        formula = create_formula(y=y,x=x)
        # Train the model
        model = smf.ols(formula=formula,data=df).fit()
        return model
    
    ############################################################################################
    #  Logistic regression model
    ############################################################################################
    # Split confusion matrix 
    def split_confusion_matrix(cm):
        # Vrais positifs
        VN,FP,FN, VP = cm.flatten()
        # Sensibility - Precision - Specifity
        sensibility, precision, specificity = VP/(FN + VP), VP/(FP + VP), VN/(VN + FP)
        # False Positif Rate
        false_pos_rate, youden_index, likelihood_ratio = 1 - specificity, sensibility + specificity - 1, sensibility/(1 - specificity)
        res =  {"sensibility" : sensibility,
                "precision" : precision,
                "specificity" : specificity,
                "False Pos. rate" : false_pos_rate,
                "younden index" : youden_index,
                "likelihood ratio" : likelihood_ratio}
        return pd.DataFrame(res,index=["metrics"])
    
    # Hosmer-Lemeshow Test
    def hosmer_lemeshow_test(ytrue,yprob):
        y_prob = pd.DataFrame(yprob)
        y_prob1 = pd.concat([y_prob, ytrue], axis =1)
        y_prob1.columns = ["prob","test"]
        y_prob1["decile"] = pd.qcut(y_prob1.prob, 10)
        obsevents_pos = y_prob1['test'].groupby(y_prob1.decile).sum()
        obsevents_neg = y_prob1["prob"].groupby(y_prob1.decile).count() - obsevents_pos
        expevents_pos = y_prob1["prob"].groupby(y_prob1.decile).sum()
        expevents_neg = y_prob1["prob"].groupby(y_prob1.decile).count() - expevents_pos
        hl = ((obsevents_neg - expevents_neg)**2/expevents_neg).sum()+((obsevents_pos - expevents_pos)**2/expevents_pos).sum()
        return hl

    # logistic metric
    def glm_metrics(model,null_deviance,ytrue,ypred):
        # Null likelihood - Model likelihood
        L0, Ln = np.exp(model.llnull), np.exp(model.llf)
        # R2 Cox and Snell
        r2coxsnell = 1.0 - (L0/Ln)**(2/model.nobs)
        # Resid deviance
        resid_deviance = -2*model.llf
        res = {"r2 mcfadden":model.prsquared,
               "r2 cox - snell" : r2coxsnell,
               "r2 nagelkerke" : r2coxsnell/(1-L0**(2.0/model.nobs)),
               "null deviance": null_deviance,
               "resid deviance" : resid_deviance ,
               "diff deviance" : null_deviance - resid_deviance,
               "accuracy score " : accuracy_score(ytrue,ypred),
               "error rate" : 1.0 - accuracy_score(ytrue,ypred),
               "recall score" : recall_score(ytrue,ypred),
               "f1 score" : f1_score(ytrue,ypred),
               "auc" : roc_auc_score(ytrue,ypred)}
        return pd.DataFrame(res,index=["metrics"])
    
    def glm_estimated(y,x,df1,df2):
        # Create formula
        formula = create_formula(y=y,x=x)
        # Null model
        null_model = smf.logit(formula=f"{y}~1",data=df1).fit(disp=False)
        # Null deviance
        null_deviance = -2*null_model.llf
        # Train the model
        model = smf.logit(formula=formula,data=df1).fit(disp=False)
        # Probability predicted
        yprob = model.predict(df2)
        # Predict under Test dataset
        ypred = list(map(round, yprob))
        # Confusion matrix
        cm = confusion_matrix(df2[y],ypred)
        split_cm = split_confusion_matrix(cm)
        # Metrics under test sampling
        gen_metrics = general_metrics(x,model)
        logit_metrics = glm_metrics(model,null_deviance,df2[y],ypred)
        return gen_metrics.join(logit_metrics).join(split_cm)
    
    # Store ols model
    def glm_model(y,x,df1):
        # Create formula
        formula = create_formula(y=y,x=x)
        # Train the model
        model = smf.logit(formula=formula,data=df1).fit(disp=False)
        return model

    if model_type == "linear":
        list_model = list(map(lambda x : ols_model(target,x,DTrain),list_features))
        res = pd.concat(map(lambda x : ols_estimated(target,x,DTrain,DTest),list_features),axis=0,ignore_index=True)
    elif model_type == "logistic":
        list_model = list(map(lambda x : glm_model(target,x,DTrain),list_features))
        res = pd.concat(map(lambda x : glm_estimated(target,x,DTrain,DTest),list_features),axis=0,ignore_index=True)
    
    # Likelihood 
    res["likelihood test ratio"] = list(map(lambda x : likelihood_ratio_test(list_model[-1],x),list_model))

    return list_model, res
    


    

