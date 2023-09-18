# -*- coding: utf-8 -*-

import scipy.stats as st
import numpy as np
import pandas as pd
from itertools import combinations
import plotnine as pn
from ggcorrplot import (
    get_melt, 
    no_panel,
    remove_diag,
    match_arg,
    get_lower_tri,
    get_upper_tri)

def scientistmetrics(X,method="cramer",correction=False,lambda_ = None):
    """Compute the degree of association between two nominales variables and return a DataFrame

    Parameters
    ----------
    X : DataFrame.
        Observed values
    
    method : {"chi2","phi","gtest","cramer","tschuprow","pearson"} (default = "cramer")
        The association test statistic.
    
    correction : bool, optional
        Inherited from https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
    
    lambda_ : float or str, optional
        Inherited from https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html

    Returns:
    --------
    statistic : DataFrame
        value of the test statistic   
    """
    # Check if X is an instance of class
    if not isinstance(X,pd.DataFrame):
        raise TypeError(f"{type(X)} is not supported. Please convert to a DataFrame with "
                        "pd.DataFrame. For more information see: "
                        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    
    if method not in ["chi2","phi","gtest","cramer","tschuprow","pearson"]:
        raise ValueError("Error : Valid method are 'chi2','phi','gtest','cramer','tschuprow' or pearson.")
    
    # Extract catehorical columns
    cat_columns = X.select_dtypes(include=["category","object"]).columns

    if len(cat_columns)==0:
        raise KeyError("No categorical variables found")

    # get all possible pair-wise combinations in the columns list
    # this assumes that A-->B equals B-->A so we don't need to
    # calculate the same thing twice
    # we also never get "A --> A"
    all_combinations = combinations(cat_columns, r=2)

    # fill matrix with zeros, except for the main diag (which will
    # be always equal to one)
    matrix = pd.DataFrame(np.eye(len(cat_columns)),columns=cat_columns,index=cat_columns)

    # log - likelihood
    if method == "gtest":
        lambda_ = "log-likelihood"

    # note that because we ignore redundant combinations,
    # we perform half the calculations, so we get the results
    # twice as fast
    for comb in all_combinations:
        i = comb[0]
        j = comb[1]

        # make contingency table
        input_tab = pd.crosstab(X[i],X[j])

        # Chi2 contingency
        if method in ["chi2","gtest"]:
            res_association = st.chi2_contingency(input_tab,correction=correction,lambda_=lambda_)[0]
        elif method == "phi":
            res_association = st.chi2_contingency(input_tab,correction=correction,lambda_=lambda_)[0]/input_tab.sum().sum()
        else:
            res_association = st.contingency.association(input_tab, method=method,correction=correction,lambda_=lambda_)

        matrix[i][j], matrix[j][i] = res_association, res_association

    return matrix

def ggheatmap(X,
              method = "square",
              type = "full",
              show_diag = None,
              limit = None,
              title = None,
              show_legend = True,
              legend_title = "association",
              colors = ["red","blue"],
              outline_color = "gray",
              lab = False,
              lab_col = "black",
              lab_size = 11,
              tl_cex = 12,
              tl_col = "black",
              tl_srt = 45,
              digits = 2,
              ggtheme = pn.theme_minimal()):
    """
    
    
    """
    
    if not isinstance(X,pd.DataFrame):
        raise TypeError(f"{type(X)} is not supported. Please convert to a DataFrame with "
                        "pd.DataFrame. For more information see: "
                        "https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html")
    #

    # set argument
    type = match_arg(type, ["full","lower","upper"])
    method = match_arg(method,["square",'circle'])

    #
    if show_diag is None:
        if type == "full":
            show_diag = True
        else:
            show_diag = False

    # Round elements
    X = X.round(decimals=digits)

    #
    if not show_diag:
        X = remove_diag(X)

    # Get lower or upper triangle
    if type == "lower":
        X = get_lower_tri(X,show_diag)
    elif type == "upper":
        X = get_upper_tri(X,show_diag)

    # Melt corr and p_mat
    X.columns = pd.Categorical(X.columns,categories=X.columns)
    X.index = pd.Categorical(X.columns,categories=X.columns)
    X = get_melt(X)

    # Initialize
    p = pn.ggplot(X,pn.aes(x="Var1",y="Var2",fill="value"))

    # Modification based on method
    if method == "square":
        p = p + pn.geom_tile(color=outline_color)
    elif method == "circle":
        p = p+pn.geom_point(pn.aes(size="abs_corr"),
                            color=outline_color,
                            shape="o")+pn.scale_size_continuous(range=(4,10))+pn.guides(size=None)
    
    # Set limit
    if limit is None:
        limit = [np.min(X["value"]),np.max(X["value"])]
    
    # Adding colors
    p = p + pn.scale_fill_gradient(
        low = colors[0],
        high = colors[1],
        name = legend_title
    )

    # depending on the class of the object, add the specified theme
    p = p + ggtheme

    p =p+pn.theme(
        axis_text_x=pn.element_text(angle=tl_srt,
                                    va="center",
                                    size=tl_cex,
                                    ha="center",
                                    color=tl_col),
        axis_text_y=pn.element_text(size=tl_cex)
    ) + pn.coord_fixed()

    label = X["value"].round(digits)

    # matrix cell labels
    if lab:
        p = p + pn.geom_text(mapping=pn.aes(x="Var1",y="Var2"),
                             label = label,
                             color=lab_col,
                             size=lab_size)
    
    if title is not None:
        p = p + pn.ggtitle(title=title)
    
    # Removing legend
    if not show_legend:
        p =p+pn.theme(legend_position=None)
    
    # Removing panel
    p = p + no_panel()

    return p

    

        