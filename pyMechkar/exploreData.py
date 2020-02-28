"""
exploreData                                                     ####
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


class exploreData: #(object):

    def __init__(self, data, y=None, miss=True, catmiss=True, categorize=True, maxcat=6, decimals=1, dir="report"):
        self.data = data
        self.y = y
        self.miss = miss
        self.catmiss = catmiss
        self.categorize = categorize
        self.maxcat = maxcat
        self.decimals = decimals
        self.dir = dir
        self._explorer = self._getDataExplore(data, y, miss, catmiss, categorize, maxcat, decimals, dir)
        return(self._explorer)

    def getOutliers(self, data, var=None, type='both'):
        self.data = data
        self.var = var
        self.type = type
        self._outliers = self._Outliers(data, var, type)
        return(self._outliers)

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


    def _getDataExplore(self, data, y, categorize, maxcat, miss, catmiss, decimals, dir):
    ################## Prepare for the report ###################
        ### initialize the report file
        try:
            # Create target Directory
            os.mkdir(dir)
        except FileExistsError:
            print("Directory " , dir ,  " already exists")
        ### create the images Directory
        try:
            # Create target Directory
            os.mkdir('%s/img' % dir)
        except FileExistsError:
            print("Directory " , dir ,  " already exists")

        report = "%s/%s.html" % (dir,dir)
        myhtml = open(report,'w+')
        ### create the header
        html = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Exploratory Data Analysis (EDA)</title>
        <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
        <link rel='stylesheet' href='http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css'>
        <script src='http://code.jquery.com/jquery-1.10.2.min.js'></script>
        <script src='http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js'></script>
        <script>
        $(document).ready(function(){
           $('.onetoone').hide();
        });
        $(function() {
           $('.origimg').click(function(e) {
             $('#popup_img').attr('src',$(this).attr('src'));
             $('#myContainer').hide();
             var pos = $(document).scrollTop();
             $('#myContainer-popup').css({'clip':'auto', 'top':pos+20, 'left':250, 'width':'450px', 'height':'338px'});
             //$('#myContainer').css({'top':pos+20,'left':250, 'width':'450px', 'height':'338px' ,'position':'absolute', 'border':'1px solid black', 'padding':'0px'});
             $('#myContainer').css({'width':'450px', 'height':'338px' ,'position':'absolute', 'border':'1px solid black', 'padding':'0px'});
             $('#myContainer').show();
             $('#myContainer').css({'clip':'rect(1px, 450px, 338px, 0px)'});
             $('#popup_img').css('visibility', 'visible');
             //$('#myContainer-popup').css({'top':pos+20,'left':250, 'width':'450px', 'height':'338px' ,'position':'absolute', 'border':'1px solid black', 'padding':'0px'});
             //alert("you clicked on the image:" +  $(this).attr('src'));
            });
           $('#myContainer').click(function(e) {
             $('#myContainer').hide();
           });
           $('#myform2').submit(function(e) {
             e.preventDefault();
           });
           $('#onetoone').on('click',function() {
             console.log('onetone button - 1');
             $('#onetoone').hide();
             $('#aslist').css('visibility','visible')
             $('#aslist').show();
             // To show only individual rows:
             $('.Row').hide();
             $('.onetoone').show();
             // then we iterate
             var i = $('.Row').length;
             // Then we iterate
             var nxt = $('#idx').val();
             if (nxt < i & nxt >0) {
               $('.Row').hide();
               $('.Row').eq(0).show();
               $('.Row').eq(nxt).show();
             } else {
               $('#idx').val(1)
             }
             console.log('onetone button - 2');
          });
          $('#aslist').on('click',function() {
            console.log('aslist button - 1');
            $('#onetoone').show();
            $('#aslist').hide();
            $('.onetoone').hide();
            $('.Row').show();
            console.log('aslist button - 2');
          });
          $('#less').on('click',function(){
            //console.log('less button - 1');
            var i = $('.Row').length;
            var nxt = parseInt($('#idx').val(),10) - 1;
            if (nxt < i & nxt >0) {
              $('#idx').val(nxt)
              $('.Row').hide();
              $('.Row').eq(0).show();
              $('.Row').eq(nxt).show();
            } else {
              $('#idx').val(1)
            }
            //console.log('less button - 2');
          });
          $('#more').on('click',function(){
            //console.log('more button - 1');
            var i = $('.Row').length;
            var nxt = parseInt($('#idx').val(),10) + 1;
            if (nxt < i & nxt >0) {
              $('#idx').val(nxt)
              $('.Row').hide();
              $('.Row').eq(0).show();
              $('.Row').eq(nxt).show();
            } else {
              $('#idx').val(i)
            }
            //console.log('more button - 2');
          });
          $('#idx').on('change', function(){
            //console.log('idx changed - 1');
            var i = $('.Row').length;
            var nxt = $('#idx').val();
            if (nxt < i & nxt >0) {
              $('#idx').val(nxt)
              $('.Row').hide();
              $('.Row').eq(0).show();
              $('.Row').eq(nxt).show();
            } else {
              $('#idx').val(i)
            }
            console.log('idx changed - 2');
          });
        });
        </script>
        <style type='text/css'>
        .Table
        {
           display: table;
        }
        .Title
        {
          display: table-caption;
          text-align: center;
          font-weight: bold;
          font-size: larger;
        }
        .Row
        {
          display: table-row;
        }
        .Cell
        {
          display: table-cell;
          border: solid;
          border-width: thin;
          padding-left: 5px;
          padding-right: 5px;
          vertical-align: top;
          font-family: "Times New Roman", Times, serif;
        }
        .origimg {
          width: 200px;
          height:120px;
        }
        .ui-btn {
          width: 10%;
        }
        .ui-input-text {
          width: 90%;
        }
        </style>
        </head>
        <body>
        <div id='pageone' data-role='main' class='ui-content'>
            <p><p><h1> Exploratory Data Analysis (EDA) </h1>
            <form id="onetoone">
                <input type='button' id='onetoone' value='Show as Cards'>
            </form>
            <form id="aslist" style='visibility:hidden;'>
                <input type='button' id='aslist' value='Show as List'>
            </form>
            <p>
        """
        myhtml.write(html)
        ### table titles
        if y==None:
            alt1 = ""
        else:
            alt1 = "<div class='Cell Title'> Dependent <br> Variable <br> Distribution </div>"
        html = """<p><p>
            <div class='Table'>
            <div class='Row'>
            <div class='Cell Title'> Variable </div>
            <div class='Cell Title'> Distribution </div>
            <div class='Cell Title'> Descriptive <br> Statistics</div>
            <div class='Cell Title'> Outliers </div>
            %s
            </div>
        """ % alt1
        myhtml.write(html)
        html = ""
        #################################################
        #### multivariate outlier detection
        #################################################
        nm = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        newdf = data.select_dtypes(include=nm)
        newdf = pd.DataFrame(normalize(newdf))
        min_samples = np.floor(np.log(len(newdf)))
        eps=np.mean(np.mean(newdf))
        mvmod = self._dbscan_mvoutliers(newdf,eps=eps,min_samples=min_samples)
        mvout = np.abs(mvmod.labels_)*2
        ### get unique values for all the variables
        unq = self._getUniqueCount(data)
        #################################################
        ### iterate through variables to find their Type
        #################################################
        nm = data.columns
        ydef = 0
        for v in nm:
            #print(v)
            ############### PART I - Descriptive Statistics  ########################
            html = "<div class='Row'><div class='Cell Title'><b> %s </b></div>" % v
            myhtml.write(html)
            ### check for y definition
            if({y}.issubset(data.columns)):
                yunq = unq[y]
                if(yunq>0):
                    if(categorize==True and yunq<=maxcat and data[y].dtype.name!='category'):
                        data[y].astype('category')
                        ydef = 1
                    elif(data[y].dtype.name=='category'):
                        ydef = 1
                    elif(data[y].dtype.name=='int64' or data[y].dtype.name=='float64' or data[y].dtype.name=='int32' or data[y].dtype.name=='float32'):
                        ydef = 2
                    else:
                        print("Please define your dependent variable (y)")
            if({v}.issubset(data.columns)):
            ### check  if there are no values on the variable
                if(unq[v]==0):
                    #msg.append("The variable %s has no data... avoided" % v)
                    html = "<div class='Cell'> Number of unique values: 0 </div>"
                    myhtml.write(html)
                    ### define if the actual variable has to be treated as numeric or factor
                    #if(categorize==True and data[v].nunique() <= maxcat):
                if(categorize==True and (unq[v] <= maxcat)):
                    data.loc[:,v] = self._to_categorical(data[v])
                    #data.loc[:,v] = _to_categorical('',data[v])
                aa = data.dtypes
                ### If date/time, don't show
                if(aa[v].name == 'datetime64[ns]' or aa[v].name == 'datetime32[ns]'):
                    #msg.append("The variable %s is a date. Dates are not allowed in Table1... avoided" % v)
                    html = "<div class='Cell'> Date: <br> Min: %s <br> Max: %s <br> Unique dates: %s </div>" % (data[v].min(), data[v].max(), len(data[v].unique()))
                    myhtml.write(html)
                    ### graph... make a distribution of counts per date and show as time-series!
                    ### if it is defined as object (not assigned numerical or categorical), ignore
                    html = "<div class='Cell'></div><div class='Cell'></div>"
                elif(aa[v].name == 'object'):
                    #msg.append("The variable %s is not well defined. This data type is not allowed in Table1... avoided" % v)
                    myhtml.write(html)
                ### if it is numeric, show
                elif(aa[v].name == 'float64' or aa[v].name == 'int64' or aa[v].name == 'float32' or aa[v].name == 'int32'):
                    ## report mean and standard deviation
                    N = data[v].shape[0]
                    n = N - data[v].isnull().sum()
                    pct = '{:8,.2f}%'.format(n/N * 100)
                    nmiss = data[v].isnull().sum()
                    npct = '{:8,.2f}%'.format(nmiss/N *100)
                    t_n = self._g1(data[v])
                    ma= '{:8,.2f}'.format(round(t_n['mean'],decimals))
                    s = '{:8,.2f}'.format(round(t_n['sd'],decimals))
                    t_n = self._g2(data[[v]])
                    me = '{:8,.2f}'.format(round(t_n['median'],decimals))
                    q1 = '{:8,.2f}'.format(round(t_n['irq_25'],decimals))
                    q3 = '{:8,.2f}'.format(round(t_n['irq_75'],decimals))
                    mn = data[v].min()
                    mx = data[v].max()
                    skw = '{:8,.2f}'.format(round(stats.skew(data[v]),decimals))
                    kurt = '{:8,.2f}'.format(round(stats.kurtosis(data[v]),decimals))
                    ############### PART II - Graph  ########################
                    grp = sns.distplot(data[v])
                    fig = grp.get_figure()
                    fig.savefig("%s/img/%s_1.png" % (dir,v))
                    plt.figure()
                    ########## graph 2
                    ## outliers...
                    out = self._Outliers(data,var=v)
                    ## join with mv outliers
                    out = np.int64(out)
                    allout = np.amax([out[0], mvout], axis=0)
                    if(len(allout) > 1):
                        grp = sns.scatterplot(data.index,data[v],hue=allout)
                    else:
                        grp = sns.scatterplot(data.index,data[v])
                    fig = grp.get_figure()
                    fig.savefig("%s/img/%s_2.png" % (dir,v))
                    plt.figure()
                    ## report number and percent of missing
                    html = """<div class='Cell'> <u>Data type</u>: Continuous <p> <u>Data length</u>: %s/%s (%s%%) <br>
                    <u>Missing</u>: %s (%s%%)<p> <u>Mean</u>: %s \t <u>StdDev</u>: %s <br><u>Median</u>: %s \t
                    <u>IQR</u>: %s-%s<br><u>Min</u>: %s \t <u>Max</u>: %s \t <p><u> Kurtosis</u>: %s \t <br><u> Skweness</u>: %s </div>
                    <div class='Cell'><img class="origimg" src="img/%s_1.png"></img></div>
                    <div class='Cell'><img class="origimg" class="origimg" src="img/%s_2.png"></img> <br> Number of outliers: %s </div>
                    """ % (n, N, pct, nmiss, npct, ma, s, me, q1, q3, mn, mx, skw, kurt, v, v, sum(out[0]))
                    myhtml.write(html)
                    if(ydef==1 and v!=y and v!=y):
                        ## boxplot
                        grp = sns.boxplot(data[v],data[y])
                        fig = grp.get_figure()
                        fig.savefig("%s/img/%s_3.png" % (dir,v))
                        plt.figure()
                        html="""<div class='Cell'><img class="origimg" src="img/%s_3.png"></img></div>""" % v
                        myhtml.write(html)
                    elif(ydef==2 and v!=y):
                        ## scatterplot
                        grp = sns.scatterplot(data[v],data[y])
                        fig = grp.get_figure()
                        fig.savefig("%s/img/%s_3.png" % (dir,v))
                        plt.figure()
                        html="""<div class='Cell'><img class="origimg" src="img/%s_3.png"></img></div>""" % v #(dir,v)
                        myhtml.write(html)
                    elif(ydef>0 and v==y):
                        html="""<div class='Cell'></div>"""
                        myhtml.write(html)
                elif(aa[v].name == "category"):
                    #if(data[v].nunique()>8):
                    N = data[v].shape[0]
                    n = N - data[v].isnull().sum()
                    pct = '{:8,.2f}%'.format(n/N * 100)
                    nmiss = data[v].isnull().sum()
                    npct = '{:8,.2f}%'.format(nmiss/N *100)
                    if(len(data.groupby(v).count())>8):
                        tmpcat = pd.Series.value_counts(data[v],dropna=(not catmiss))
                        n = len(tmpcat)
                        if(n > 8):
                            v1a = tmpcat[0:6].values
                            v2a = np.append(v1a,tmpcat[7:n].sum())
                            a1 = tmpcat.index[0:6].values.tolist()
                            a2 = a1.extend(['Other'])
                            t_n = pd.Series(v2a,a1)
                    else:
                        t_n = pd.Series.value_counts(data[v],dropna=(not catmiss))
                    ttotal = len(data)
                    #nm = data[v].unique()
                    nm = t_n.index.values
                    pct = []
                    for f in range(0,len(nm)):
                        del1 = 0
                        tp = t_n.iloc[f] / ttotal * 100
                        pct.append("%s: %s (%s%%)" % (nm[f],'{:8,.2f}'.format(round(t_n.iloc[f],decimals)), '{:8,.2f}'.format(round(tp,decimals))))
                        #v1 = pct
                        v1 = '<br>'.join(map(str, pct))
                    v3 = ""
                    if (miss >= 2 and catmiss==False ):
                        if (data[v].isnull().sum()>0):
                            t_n = data.shape[0]
                            t_m = data[v].isnull().sum()
                            tp = "%s (%s%%)" % ('{:8,.2f}'.format(t_m), '{:8,.2f}'.format(round((t_m/t_n)*100,decimals)))
                            v3 = "Missing (%): " % tp
                        else:
                            v3 = "Missing (%): 0%"
                    ########## graph 1
                    grp = sns.countplot(data[v])
                    fig = grp.get_figure()
                    fig.savefig("%s/img/%s_1.png" % (dir,v))
                    plt.figure()
                    ########## graph 2
                    grp = sns.scatterplot(data.index,data[v])
                    fig = grp.get_figure()
                    fig.savefig("%s/img/%s_2.png" % (dir,v))
                    plt.figure()
                    ##########
                    html = """<div class='Cell'> <u>Data type</u>: Category <p> <u>Data length</u>: %s/%s <br>
                    <u>Missing</u>: %s (%s%%)<p> <u>Categories</u>:<br> %s <br> %s </div>
                    <div class='Cell'><img class="origimg" src="img/%s_1.png"></img></div>
                    <div class='Cell'><img class="origimg" src="img/%s_2.png"></img></div>
                    """ % (n, N, nmiss, npct,v1, v3, v, v)
                    myhtml.write(html)
                    if(ydef==1 and v!=y):
                        ## countplot
                        grp = sns.countplot(x=v, hue=y, data=data)
                        fig = grp.get_figure()
                        fig.savefig("%s/img/%s_3.png" % (dir,v))
                        plt.figure()
                        html="""<div class='Cell'><img class="origimg" src="img/%s_3.png"></img></div>""" % v
                        myhtml.write(html)
                    elif(ydef==2 and v!=y):
                        ## boxplot
                        grp = sns.boxplot(x=v,y=y,data=data)
                        fig = grp.get_figure()
                        fig.savefig("%s/img/%s_3.png" % (dir,v))
                        plt.figure()
                        html="""<div class='Cell'><img class="origimg" src="img/%s_3.png"></img></div>""" % v
                        myhtml.write(html)
                    elif(ydef>0 and v==y):
                        html="""<div class='Cell'></div>"""
                        myhtml.write(html)
                else:
                    msg.append("The variable %s doesn't exists in the dataset... avoiding" % v)
            ### close the rows
            html = "</div>"
            myhtml.write(html)

        ##### end table
        html = """
                <div data-role='popup' id='myContainer' style='display: none;'>
                    <img id='popup_img' src='' />
                </div>

                </div>
                </div>
                </div>
                <p>
                <div class='onetoone'>
                    <form id='myform2' style='display:block;'>
                      <div id='navigator' style="display: block; width='40%';">
                          <div id='less' style="float:left;"><input class='ui-btn' type='button' id='less1' value=' << ' style='width: 10%;'></div>
                          <div id='center' style="float:left;"><input id='idx' name='idx' value='1' style='text-align:center;'></input></div>
                          <div id='more' style="float:left;"><input class='ui-btn' type='button' id='more1' value=' >> ' style='width: 10%;'></div>
                      </div>
                    </form>
                </div>
                <p>
                </body></html>
        """
        myhtml.write(html)
        ###### CLOSE FILE
        myhtml.close()
        import webbrowser
        url="./%s/report.html" % dir
        #webbrowser.open(url[,new=0[,autoraise=True]])
        webbrowser.open(url)

    def _zscore_outliers(self, x, cutoff=3.0, return_thresholds=False):
        dmean = x.mean()
        dsd = x.std()
        rng = dsd * cutoff
        lower = dmean - rng
        upper = dmean + rng
        if return_thresholds:
            return lower, upper
        else:
            return [True if z < lower or z > upper else False for z in x]


    def _iqr_outliers(self, x, k=1.5, return_thresholds=False):
        # calculate interquartile range
        q25 = np.percentile(x, 25)
        q75 = np.percentile(x, 75)
        iqr = q75 - q25
        # calculate the outlier cutoff
        cut_off = iqr * k
        lower, upper = q25 - cut_off, q75 + cut_off
        if return_thresholds:
            return lower, upper
        else: # identify outliers
            return [True if z < lower or z > upper else False for z in x]

    def _dbscan_mvoutliers(self, X, eps, min_samples):
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        # scale data first
        X = StandardScaler().fit_transform(X.values)
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        labels = db.labels_
        return(db)

#    def getOutliers(self, data, var=None, type='both'):
    def _Outliers(self, data, var=None, type='both'):
        ### type=['univariate','multivariate','both']
        out = []
        ### check for normality
        skew = stats.skew(data[var])
        kurt = stats.kurtosis(data[var])
        if(skew <= 0.01 and kurt <= 3):
            stat = 1
        else:
            stat = 2
        if(stat==1 and (type=='univariate' or type=='both')):
            pnts = self._zscore_outliers(data[var])
            out.append(pnts)
        if(stat==2 and (type=='univariate' or type=='both')):
            pnts = self._iqr_outliers(data[var])
            out.append(pnts)
        #if(type=='both' or type=='multivariate'):
        #    cl = data.dtypes
        #    nm = cl[cl=='int64' or cl=='float64' or cl=='int32' or cl=='float32']
        #    pnts = self._dbscan_mvoutliers(data)
        #    out.append(pnts)
        return(out)
