"""
Table1                                                          ####
Author: Tomas Karpati M.D.                                      ####
Creation date: 2019-01-02                                       ####
Last Modified: 2020-02-27                                       ####
"""

__author__ = "Tomas Karpati <karpati@it4biotech.com>"
__version__ = "0.1.3"

"""
Usage:
x: character vector with the name of the variables
y: the name of the strata variable (optional)
rn: character vector with the text we want to replace the variable names
data: the dataset to be used
miss: include missing statistics: [0=none, 1=only for categorical variables, 2=for all variables]
excel: export the table to excel [0=no, 1=yes]
excel_file: the name of the excel file we want to save the table (optional)

"""
import time
import sys
import os
import numpy as np
from scipy import stats
#from statsmodels.stats import multitest
from statsmodels.formula.api import ols
#import statsmodels.stats.api as sms
from statsmodels.stats.anova import anova_lm
import pandas as pd
from sklearn.preprocessing import normalize
#import matplotlib
### preventing matplotlib to open a graph window when saving...
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
### preventing matplotlib to open a graph window when saving...
plt.ioff()
import seaborn as sns
## dissable the "SettingWithCopyWarning" warning
pd.options.mode.chained_assignment = None  # default='warn'
#import warnings

if(pd.__version__ < '0.21.0'):
    pd.set_option('use_inf_as_null',True)
else:
    pd.set_option('use_inf_as_na',True)


class Table1: #(object):

    def __init__(self, data=None, x='', y='', rn='', miss=True, catmiss=True, formatted=True, categorize=True, factorVars='', maxcat=6, decimals=1, messages=True, dir="report", excel=False, excel_file=''):
        self.data = data
        self.x = x
        self.y = y
        self.rn = rn
        self.miss = miss
        self.catmiss = catmiss
        self.formatted = formatted
        self.categorize = categorize
        self.factorVars = factorVars
        self.maxcat = maxcat
        self.decimals = decimals
        self.messages = messages
        self.dir = dir
        self.excel = excel
        self.excel_file = excel_file
        ### define sub-functions
        #self.table1 = self._getTable1(x, data, y, rn, miss, catmiss, formatted, categorize, factorVars, maxcat, decimals, messages, excel, excel_file)
        #self.explorer = self.exploreData(data, y=None, miss=True, catmiss=True, categorize=True, maxcat=6, decimals=1, dir="report")
    #def getTable1(self):
    #    #self.table1 = self._getTable1(x, data, y, rn, miss, catmiss, formatted, categorize, factorVars, maxcat, decimals, messages, excel, excel_file)
    #    return(self.table1)

    def _g1(self,var):
        res = {'mean':np.nanmean(var), 'sd':np.nanstd(var)}
        return(res)

    def _g2(self,var):
        res = {'median':np.nanmedian(var), 'irq_25':np.nanpercentile(var,25), 'irq_75':np.nanpercentile(var,75)}
        return(res)

    def _getUniqueCount(self, data):
        import pandas as pd
        bb = data.columns.tolist()
        cc = {}
        for v in bb:
            cc[v] = len(data.groupby(v).count())
        return(pd.Series(cc))


    def _to_categorical(self, x):
        x = x.astype('category')
        return(x)

    def _setFactors(self, data, factorVars, unq, catmiss, maxcat):
        aa =data.dtypes
        if(len(factorVars) > 0):
            for v in factorVars:
                #print("Variable %s is a %s" % (v,aa[v].name))
                if(aa[v].name!='category'):
                    data.loc[:,v] = self._to_categorical(data[v])
                if(catmiss==True):
                    if(data[v].isnull().sum()>0):
                        #print("Adding missing category to %s" % v)
                        data[v] = data[v].cat.add_categories(['Missing'])
                        data.loc[data[v].isnull(),v] = "Missing"

        elif(len(factorVars)==0):
            #factorVars = self._getUniqueCount(data)
            factorVars = unq
            factorVars = factorVars[factorVars <= maxcat]
            for v in factorVars.index:
                if(aa[v].name!="category"):
                    data.loc[:,v] = self._to_categorical(data[v])
                if(catmiss==True):
                    if(data[v].isnull().sum()>0):
                        data[v].cat.add_categories(['Missing'])
                        data.loc[data[v].isnull(),v] = "Missing"
        return(data)


    def _getSimpleTable(self,x, data, rn, miss, catmiss, formatted, categorize, factorVars, unq, maxcat, decimals, messages):
        msg=[]
        if (len(rn)==0):
            rn = x
        ln = len(x)
        ### init the progress bar
        sys.stdout.write("[%s]" % ("" * ln))
        sys.stdout.flush()
        sys.stdout.write("\b" * (ln+1)) # return to start of line, after '['
        toolbar_width = 80
        ### define the column names
        tableaaaa = [[0,"Individuals","n",1, len(data)]]
        tablebbbb = [[0,"Individuals","n",1, len(data),'','']]
        q = 0
        n = 0
        ii = 0
        tm = 0
        for v in x:
          time.sleep(0.1) # do real work here
          # update the progress bar
          sys.stdout.write("*")
          sys.stdout.flush()
          ### check if the variable name exists in the dataset
          if({v}.issubset(data.columns)):
            ### check  if there are no values on the variable
            #if(data[v].nunique()==0):
            if(unq[v]==0):
                msg.append("The variable %s has no data... avoided" % v)
            ### define if the actual variable has to be treated as numeric or factor
            aa = data.dtypes
            #if(categorize==True and data[v].nunique() <= maxcat):
            if(categorize==True and (unq[v] <= maxcat)):
                data.loc[:,v] = self._to_categorical(data[v])
            ### If date/time, don't show
            if(aa[v].name == 'datetime64[ns]'):
                msg.append("The variable %s is a date. Dates are not allowed in Table1... avoided" % v)
            ### if it is defined as object (not assigned numerical or categorical), ignore
            elif(aa[v].name == 'object'):
                msg.append("The variable %s is not well defined. This data type is not allowed in Table1... avoided" % v)
            ### if it is numeric, show
            elif(aa[v].name == 'float64' or aa[v].name == 'int64'):
                ## report mean and standard deviation
                t_n = self._g1(data[v])
                tp = "%s (%s)" % ('{:8,.2f}'.format(round(t_n['mean'],decimals)), '{:8,.2f}'.format(round(t_n['sd'],decimals)))
                tbl1 = [0, rn[q],"Mean (SD)",1, tp]
                tbl2 = [0, rn[q],"Mean (SD)",1, round(t_n['mean'],5),round(t_n['sd'],5),'']
                tableaaaa.append(tbl1)
                tablebbbb.append(tbl2)
                ## report median and Interquartile ranges (25%,75%)
                t_n = self._g2(data[[v]])
                tp = "%s (%s-%s)" % ('{:8,.2f}'.format(round(t_n['median'],decimals)), '{:8,.2f}'.format(round(t_n['irq_25'],decimals)), '{:8,.2f}'.format(round(t_n['irq_75'],decimals)))
                tbl1 = [0, rn[q],"Median (IQR)",2, tp]
                tbl2 = [0, rn[q],"Median (IQR)",2, round(t_n['median'],5),round(t_n['irq_25'],5),round(t_n['irq_75'],5)]
                tableaaaa.append(tbl1)
                tablebbbb.append(tbl2)
                ## report number and percent of missing
                if (miss >= 1):
                    if (data[v].isnull().sum()>0):
                        t_n  = len(data)
                        t_m = data[v].isnull().sum()
                        tp = "%s (%s%%)" % ('{:8,.2f}'.format(t_m),'{:8,.2f}'.format(round((t_m/t_n)*100,decimals)))
                        tbl1 = [0,rn[q],"Missing (%)",3, tp]
                        tbl2 = [0,rn[q],"Missing (%)",3, t_m, (t_m/t_n)*100, ]
                    else:
                        tbl1 = [1,rn[q],"Missing (%)",3, " -- "]
                        tbl2 = [1,rn[q],"Missing (%)",3,'' ,'' ,'' ]
                    tableaaaa.append(tbl1)
                    tablebbbb.append(tbl2)
            elif(aa[v].name == "category"):
                #if(data[v].nunique()>8):
                if(len(data.groupby(v).count())>8):
                    tmpcat = pd.Series.value_counts(data[v],dropna=(not catmiss))
                    n = len(tmpcat)
                    if(n > 8):
                        v1 = tmpcat[0:6].values
                        v2 = np.append(v1,tmpcat[7:n].sum())
                        a1 = tmpcat.index[0:6].values.tolist()
                        a2 = a1.extend(['Other'])
                        t_n = pd.Series(v2,a1)
                else:
                    t_n = pd.Series.value_counts(data[v],dropna=(not catmiss))
                ttotal = len(data)
                #nm = data[v].unique()
                nm = t_n.index.values
                for f in range(0,len(nm)):
                    del1 = 0
                    if(len(nm)==2 and (nm[f]=="No" or nm[f]=="no" or nm[f]==0 or nm[f]=="0" or nm[f]=="None" or nm[f]=="none")):
                        del1 = 1
                    tp = t_n.iloc[f] / ttotal * 100
                    pct = "%s (%s%%)" % ('{:8,.2f}'.format(round(t_n.iloc[f],decimals)), '{:8,.2f}'.format(round(tp,decimals)))
                    tbl1 = [del1,rn[q],nm[f],f, pct]             ########### delete rows 0/1 !!!!!!!!!
                    tbl2 = [del1,rn[q],nm[f],f, t_n.iloc[f], tp, ]    ########### delete rows 0/1 !!!!!!!!!
                    tableaaaa.append(tbl1)
                    tablebbbb.append(tbl2)
                if (miss >= 2 and catmiss==False ):
                    if (data[v].isnull().sum()>0):
                      t_n = len(data)
                      t_m = data[v].isnull().sum()
                      tp = "%s (%s%%)" % ('{:8,.2f}'.format(t_m), '{:8,.2f}'.format(round((t_m/t_n)*100,decimals)))
                      tbl1 = [0, rn[q], "Missing (%)", f, tp]
                      tbl2 = [0, rn[q], "Missing (%)", f, t_m, (t_m/t_n)*100, ]
                    else:
                      tbl1 = [1,rn[q],"Missing (%)",f, " -- "]
                      tbl2 = [1,rn[q],"Missing (%)",f,'' ,'' , '']
                    tableaaaa.append(tbl1)
                    tablebbbb.append(tbl2)
            else:
                msg.append("The variable %s doesn't exists in the dataset... avoiding" % v)

            q = q + 1
            ii = ii + 1
            tm = tm + 1
        if(formatted==True):
          ### terminate the progress bar
          sys.stdout.write("\n")
          if(messages==True):
              print(msg)
          return(tableaaaa)
        else:
          ### terminate the progress bar
          sys.stdout.write("\n")
          if(messages==True):
              print(msg)
          return(tablebbbb)


    def _pvals(self, x, y, rn, data, unq, messages):
        msg = []
        ptab = [] #[["Variables","pval", "n"]]
        if (y!=''):
          if ({y}.issubset(data.columns)):
            if (len(rn)==0 or len(rn)<2):
                rn = x
            q = 0
            for v in x:
              #print(v)
              if ({v}.issubset(data.columns) and v != y):
                #factorY = data[y].nunique()
                factorY = unq[y]
                aa = data.dtypes
                if((aa[y].name == 'float64' or aa[y].name == 'int64' or aa[y].name == 'object') and factorY <= maxcat):
                    data.loc[:,y] = to_categorical(data[y])
                elif (aa[y].name == 'float64' or aa[y].name == 'int64'):
                  msg.append("The variable %s is not a factor. Please convert to factor or change the 'categorize' flag to TRUE." % y)
                  pval = []

                #if ((aa[v].name == 'float64' or aa[v].name == 'int64') and (data[y].nunique() > 1)):
                if ((aa[v].name == 'float64' or aa[v].name == 'int64' or aa[v].name == 'float32' or aa[v].name == 'int32') and (unq[y] > 1)):
                  ### first check for homoscedasticity
                    bb = pd.Series({x : y.tolist() for x,y in data[v].groupby(data[y])})
                    if (stats.bartlett(*bb)[1] >= 0.05):
                        formula = "%s ~ %s" % (v,y)
                        model = ols(formula,data=data,missing='drop').fit()
                        aov_table = anova_lm(model, typ=2)
                        pval =round(aov_table['PR(>F)'][0],3)
                    else:
                        prevar = data.loc[-data[v].isnull()]
                        bb = pd.Series({x : y.tolist() for x,y in prevar[v].groupby(prevar[y])})
                        pval = stats.f_oneway(*bb)[1]
                #elif (data[y].nunique()==1):
                elif (unq[y]==1):
                  pval = np.nan
                elif (aa[v].name=="datetime64[ns]"):
                    pval = np.nan
                else:
                    if(pd.crosstab(data[v],data[y]).min().min()>5):
                        pval = stats.chi2_contingency(pd.crosstab(data[v],data[y]))[1]
                    else:
                        ct = pd.crosstab(data[v],data[y])
                        if(ct.min().min()==0):
                        # in cases where there are cells with zero, we use Fisher's exact test
                            if(ct.shape == (2,2)):
                                pval = stats.fisher_exact(ct)[1]
                            else:
                                pval = stats.chi2_contingency(pd.crosstab(data[v],data[y]))[1]
                                msg.append("Unable to calcualte the Fisher exact test for variables %s and %s... The p-value may be incorrect" % (v,y))
                        else:
                            pval = stats.mstats.kruskalwallis(pd.crosstab(data[v],data[y]))[1]
                ptab.append([rn[q],round(pval,3),1])
              q = q + 1
        if(messages==True):
            print(msg)
        return(ptab)

    ###############################################################################################
    ####################### Begin analysis
    ###############################################################################################
    def _getTable1(self, data, x, y, rn, miss, catmiss, formatted, categorize, factorVars, maxcat, decimals, messages, excel, excel_file):
    #def _getTable1(self):
        import time
        init = time.time()

        print("Factorizing... please wait")
        if (len(x)==0):
            x = data.columns.tolist()
        if(y!='' and {y}.issubset(x)):
            x.remove(y)
            #if ({'Unnamed: 0'}.issubset(x)):
            #    x.drop('Unnamed: 0')
        unq = self._getUniqueCount(data)
        if ({'Unnamed: 0'}.issubset(unq)):
            unq.drop('Unnamed: 0')
        if (len(factorVars)==0):
            factorVars = unq[unq <= maxcat].index
        #print(data.dtypes)
        data = self._setFactors(data=data, factorVars=factorVars, unq=unq, catmiss=catmiss, maxcat=maxcat)
        #print(data.dtypes)
        ##### if y is null then make a simple table
        #print("_getSimpleTable pass 1...")
        tabaaa1 = self._getSimpleTable(x=x, rn=rn, data=data, miss=miss, catmiss=catmiss, unq=unq, formatted=formatted, categorize=categorize, factorVars=factorVars, maxcat=maxcat, decimals=decimals, messages=messages)
        if(formatted==True):
            tabaaa1 = pd.DataFrame(tabaaa1,columns=["Del","Variables","Categories","n","Population"])
        else:
            tabaaa1 = pd.DataFrame(tabaaa1,columns=["Del","Variables","Categories","n","val1","val2","val3"])
        #print(tabaaa1)
        ##### if y has two levels, then make a compound comparison
        if (y!=''): #1
            if ({y}.issubset(data.columns)):  #2
                if (data[y].dtype == "category"): #3
                    if (unq[y] > 8): #4
                        if (messages==True): #5
                            print("The dependent variable has more than 8 levels, table too large!")
                    elif(min(pd.Series.value_counts(data[y]))==0): #4
                        print("The dependent variable has one or more levels with no items assigned!")
                    else: # 4
                        data.loc[:,y] = self._to_categorical(data[y])
                #if (data[y].nunique() >= 2): #3
                if (unq[y] > 6): #3
                    print("You have selected a Y that has more than six different values...")
                elif (unq[y] >= 2 and unq[y]<=6): #3
                    for lv in data[y].unique(): #4
                        #print("Category %s" % lv)
                        dtsub = data.loc[data[y]==lv]
                        #print("_getSimpleTable Y pass ...")
                        tab = self._getSimpleTable(x=dtsub.columns,data=dtsub, rn=rn, miss=miss, unq=unq, catmiss=catmiss, formatted=formatted, categorize=categorize, factorVars=factorVars, maxcat=maxcat, decimals=decimals, messages=False)
                        if(formatted==True): # 5
                            tab1 = pd.DataFrame(tab,columns=["Del","Variables","Categories","n",'Category_%s' % lv])
                        else: #5
                            tab1 = pd.DataFrame(tab,columns=["Del","Variables","Categories","n","Cat_%s_val1" % lv,"Cat_%s_val2" % lv,"Cat_%s_val3" % lv])
                        tab1 = tab1.drop(['n'], axis=1) #5
                        #print(tab)
                        tabaaa1 = pd.merge(tabaaa1, tab1, on=['Del','Variables','Categories'],how='left')
                    #print(tabaaa1)

                    #print("_pvals pass ...")
                    ptab = self._pvals(x=x,y=y, rn=rn, data=data, unq=unq, messages=messages)
                    ptab = pd.DataFrame(ptab,columns=["Variables","p_value", "n"])
                    #print(ptab)
                    tabaaa1 = pd.merge(tabaaa1, ptab, on=['Variables','n'],how='left')
                    tabaaa1 = tabaaa1.loc[tabaaa1['Population']!=" -- "]
                    tabaaa1 = tabaaa1.drop('n',1)
                    tabaaa1 = tabaaa1.drop('Del',1)
        #### Save as excel file
        if(excel==True):
            if(excel_file == ''):
                print("Please fill in the <excel_file> parameter with the file name including the path.")
            else:
                writer = pd.ExcelWriter(excel_file)
                tabaaa1.to_excel(writer,'Table1',index=False)
                writer.save()
                print("Excel file written to %s" % excel_file)
        print("------ Finished in % seconds -----" % (time.time() - init))
        return(tabaaa1) #1
