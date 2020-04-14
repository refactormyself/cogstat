# -*- coding: utf-8 -*-

"""
This module contains functions for hypothesis tests.

Arguments are the pandas data frame (pdf), and parameters (among others they
are usually variable names).
Output is text (html and some custom notations).

Mostly scipy.stats and statsmodels are used to generate the results.
"""

import gettext
import os
from scipy import stats
import numpy as np

from . import cogstat_config as csc
from . import cogstat_stat_num as cs_stat_num
from . import cogstat_stat as cs_stat
from . import cogstat_util as cs_util

from statsmodels.sandbox.stats.runs import mcnemar
from statsmodels.sandbox.stats.runs import cochrans_q
from statsmodels.stats.anova import AnovaRM
import pandas as pd
import scikit_posthocs


run_power_analysis = False  # should this analysis included?

t = gettext.translation('cogstat', os.path.dirname(os.path.abspath(__file__))+'/locale/', [csc.language], fallback=True)
_ = t.gettext

### Compare variables ###

def paired_t_test(pdf, var_names):
    """Paired sample t-test

    arguments:
    pdf (pandas dataframe)
    var_names (list of str): two variable names to compare

    return:
    text_result (string)
    """
    # Not available in statsmodels
    if len(var_names) != 2:
        return _('Paired t-test requires two variables.')

    variables = pdf[var_names].dropna()
    text_result = ''

    # Sensitivity power analysis
    if run_power_analysis:
        from statsmodels.stats.power import TTestPower
        power_analysis = TTestPower()
        text_result += _(
            'Sensitivity power analysis. Minimal effect size to reach 95%% power (effect size is in %s):') % _(
            'd') + ' %0.2f\n' % power_analysis.solve_power(effect_size=None, nobs=len(variables), alpha=0.05,
                                                           power=0.95,
                                                           alternative='two-sided')

    df = len(variables) - 1
    t, p = stats.ttest_rel(variables.iloc[:, 0], variables.iloc[:, 1])
    text_result += _('Result of paired samples t-test') + ': <i>t</i>(%d) = %0.3g, %s\n' % (df, t, cs_util.print_p(p))

    return text_result


def paired_wilcox_test(pdf, var_names):
    """Paired Wilcoxon Signed Rank test
    http://en.wikipedia.org/wiki/Wilcoxon_signed-rank_test

    arguments:
    pdf
    var_names (list of str): two variable names to compare

    return:
    """
    # Not available in statsmodels
    text_result = ''
    if len(var_names) != 2:
        return _('Paired Wilcoxon test requires two variables.')

    variables = pdf[var_names].dropna()
    T, p = stats.wilcoxon(variables.iloc[:, 0], variables.iloc[:, 1])
    text_result += _('Result of Wilcoxon signed-rank test') + ': <i>T</i> = %0.3g, %s\n' % (T, cs_util.print_p(p))
    # The test does not use df, despite some of the descriptions on the net.
    # So there's no need to display df.

    return text_result


def mcnemar_test(pdf, var_names):
    chi2, p = mcnemar(pdf[var_names[0]], pdf[var_names[1]], exact=False)
    return _('Result of the McNemar test') + ': &chi;<sup>2</sup>(1, <i>N</i> = %d) = %0.3g, %s\n' % \
                                              (len(pdf[var_names[0]]), chi2, cs_util.print_p(p))


def cochran_q_test(pdf, var_names):
    q, p = cochrans_q(pdf[var_names])
    return _("Result of Cochran's Q test") + ': <i>Q</i>(%d, <i>N</i> = %d) = %0.3g, %s\n' % \
                                              (len(var_names)-1, len(pdf[var_names[0]]), q, cs_util.print_p(p))


def repeated_measures_anova(pdf, var_names, factors=[]):
    """
    TODO
    :param pdf:
    :param var_names:
    :param factors:
    :return:
    """

    if not factors:  # one-way comparison
        # TODO use statsmodels functions
        [dfn, dfd, f, pf, w, pw], corr_table = cs_stat_num.repeated_measures_anova(pdf[var_names].dropna(), var_names)
        # Choose df correction depending on sphericity violation
        text_result = _("Result of Mauchly's test to check sphericity") + \
                       ': <i>W</i> = %0.3g, %s. ' % (w, cs_util.print_p(pw))
        if pw < 0.05:  # sphericity is violated
            p = corr_table[0, 1]
            text_result += '\n<decision>'+_('Sphericity is violated.') + ' >> ' \
                           +_('Using Greenhouse-Geisser correction.') + '\n<default>' + \
                           _('Result of repeated measures ANOVA') + ': <i>F</i>(%0.3g, %0.3g) = %0.3g, %s\n' \
                            % (dfn * corr_table[0, 0], dfd * corr_table[0, 0], f, cs_util.print_p(p))
        else:  # sphericity is not violated
            p = pf
            text_result += '\n<decision>'+_('Sphericity is not violated. ') + '\n<default>' + \
                           _('Result of repeated measures ANOVA') + ': <i>F</i>(%d, %d) = %0.3g, %s\n' \
                                                                    % (dfn, dfd, f, cs_util.print_p(p))

        # Post-hoc tests
        if p < 0.05:
            pht = cs_stat_num.pairwise_ttest(pdf[var_names].dropna(), var_names).sort_index()
            text_result += '\n' + _('Comparing variables pairwise with the Holm-Bonferroni correction:')
            #print pht
            pht['text'] = pht.apply(lambda x: '<i>t</i> = %0.3g, %s' % (x['t'], cs_util.print_p(x['p (Holm)'])), axis=1)

            pht_text = pht[['text']]
            text_result += cs_stat._format_html_table(pht_text.to_html(bold_rows=True, classes="table_cs_pd", escape=False,
                                                               header=False))

            # Or we can print them in a matrix
            #pht_text = pht[['text']].unstack()
            #np.fill_diagonal(pht_text.values, '')
            #text_result += pht_text.to_html(bold_rows=True, escape=False))
    else:  # multi-way comparison

        # Prepare the dataset for the ANOVA
        # new temporary names are needed to set the independent factors in the long format
        # (alternatively, one might set it later in the long format directly)
        temp_var_names = ['']
        for factor in factors:
            # TODO this will not work if the factor name includes the current separator (_)
            temp_var_names = [previous_var_name+'_'+factor[0]+str(i)
                              for previous_var_name in temp_var_names for i in range(factor[1])]
        temp_var_names = [temp_var_name[1:] for temp_var_name in temp_var_names]
        #print(temp_var_names)

        pdf_temp = pdf[var_names].dropna()
        pdf_temp.columns = temp_var_names
        pdf_temp = pdf_temp.assign(ID=pdf_temp.index)
        pdf_long = pd.melt(pdf_temp, id_vars='ID', value_vars=temp_var_names)
        pdf_long = pd.concat([pdf_long, pdf_long['variable'].str.split('_', expand=True).
                             rename(columns={i: factors[i][0] for i in range(len(factors))})], axis=1)

        # Run ANOVA
        anovarm = AnovaRM(pdf_long, 'value', 'ID', [factor[0] for factor in factors])
        anova_res = anovarm.fit()

        # Create the text output
        #text_result = str(anova_res)
        text_result = ''
        for index, row in anova_res.anova_table.iterrows():
            factor_names = index.split(':')
            if len(factor_names) == 1:
                text_result += _('Main effect of %s') % factor_names[0]
            else:
                text_result += _('Interaction of factors %s') % ', '.join(factor_names)
            text_result += (': <i>F</i>(%d, %d) = %0.3g, %s\n' %
                            (row['Num DF'], row['Den DF'], row['F Value'], cs_util.print_p(row['Pr > F'])))

        # TODO post hoc - procedure for any number of factors (i.e., not only for two factors)
    #print(text_result)

    return text_result


def friedman_test(pdf, var_names):
    """Friedman t-test

    arguments:
    var_names (list of str):
    """
    # Not available in statsmodels
    text_result = ''
    if len(var_names) < 2:
        return _('Friedman test requires at least two variables.')

    variables = pdf[var_names].dropna()
    chi2, p = stats.friedmanchisquare(*[np.array(var) for var in variables.T.values])
    df = len(var_names) - 1
    n = len(variables)
    text_result += _('Result of the Friedman test: ') + '&chi;<sup>2</sup>(%d, <i>N</i> = %d) = %0.3g, %s\n' % \
                   (df, n, chi2, cs_util.print_p(p))  # χ2(1, N=90)=0.89, p=.35

    return text_result


### Compare groups ###


def levene_test(pdf, var_name, group_name):
    """

    arguments:
    var_name (str):
    group_name (str):

    return
    p: p
    text_result: APA format
    """
    # Not available in statsmodels
    text_result = ''

    dummy_groups, var_s = cs_stat._split_into_groups(pdf, var_name, group_name)
    for i, var in enumerate(var_s):
        var_s[i] = var_s[i].dropna()
    w, p = stats.levene(*var_s)
    text_result += _('Levene test') + ': <i>W</i> = %0.3g, %s\n' % (w, cs_util.print_p(p))

    return p, text_result


def independent_t_test(pdf, var_name, grouping_name):
    """Independent samples t-test

    arguments:
    var_name (str):
    grouping_name (str):
    """
    from statsmodels.stats.weightstats import ttest_ind
    text_result = ''

    dummy_groups, [var1, var2] = cs_stat._split_into_groups(pdf, var_name, grouping_name)
    var1 = var1.dropna()
    var2 = var2.dropna()
    t, p, df = ttest_ind(var1, var2)
    # CI http://onlinestatbook.com/2/estimation/difference_means.html
    # However, there are other computtional methods:
    # http://dept.stat.lsa.umich.edu/~kshedden/Python-Workshop/stats_calculations.html
    # http://www.statisticslectures.com/topics/ciindependentsamplest/
    mean_diff = np.mean(var1) - np.mean(var2)
    sse = np.sum((np.mean(var1) - var1) ** 2) + np.sum((np.mean(var2) - var2) ** 2)
    mse = sse / (df)
    nh = 2.0 / (1.0 / len(var1) + 1.0 / len(var2))
    s_m1m2 = np.sqrt(2 * mse / (nh))
    t_cl = stats.t.ppf(1 - (0.05 / 2), df)  # two-tailed
    lci = mean_diff - t_cl * s_m1m2
    hci = mean_diff + t_cl * s_m1m2
    prec = cs_util.precision(var1.append(var2)) + 1

    # Sensitivity power analysis
    if run_power_analysis:
        from statsmodels.stats.power import TTestIndPower
        power_analysis = TTestIndPower()
        text_result += _(
            'Sensitivity power analysis. Minimal effect size to reach 95%% power (effect size is in %s):') % _(
            'd') + ' %0.2f\n' % power_analysis.solve_power(effect_size=None, nobs1=len(var1), alpha=0.05, power=0.95,
                                                           ratio=len(var2) / len(var1), alternative='two-sided')

    text_result += _('Difference between the two groups:') + ' %0.*f, ' % (prec, mean_diff) + \
                   _('95%% confidence interval [%0.*f, %0.*f]') % (prec, lci, prec, hci) + '\n'
    text_result += _('Result of independent samples t-test:') + ' <i>t</i>(%0.3g) = %0.3g, %s\n' % \
                   (df, t, cs_util.print_p(p))
    return text_result


def single_case_task_extremity(pdf, var_name, grouping_name, se_name = None, n_trials=None):
    """Modified t-test for comparing a single case with a group.
    Used typically in case studies.

    arguments:
    pdf (pandas dataframe) including the data
    var_name (str): name of the dependent variable
    grouping_name (str): name of the grouping variable
    se_name (str): optional, name of the slope SE variable - use only for slope based calculation
    n_trials (int): optional, number of trials the slopes were calculated of - use only for slope based calculation
    """
    text_result = ''
    group_levels, [var1, var2] = cs_stat._split_into_groups(pdf, var_name, grouping_name)
    if not se_name:  # Simple performance score
        try:
            if len(var1) == 1:
                ind_data = var1
                group_data = var2.dropna()
            else:
                ind_data = var2
                group_data = var1.dropna()
            t, p, df = cs_stat_num.modified_t_test(ind_data, group_data)
            text_result += _('Result of the modified independent samples t-test:') + \
                           ' <i>t</i>(%0.3g) = %0.3g, %s\n' % (df, t, cs_util.print_p(p))
        except ValueError:
            text_result += _('One of the groups should include only a single data.')
    else:  # slope performance
        group_levels, [se1, se2] = cs_stat._split_into_groups(pdf, se_name, grouping_name)
        if len(var1)==1:
            case_var = var1[0]
            control_var = var2
            case_se = se1[0]
            control_se = se2
        else:
            case_var = var2[0]
            control_var = var1
            case_se = se2[0]
            control_se = se1
        t, df, p, test = cs_stat_num.slope_extremity_test(n_trials, case_var, case_se, control_var, control_se)
        text_result += _('Result of slope test with %s:')%(test) + \
                       ' <i>t</i>(%0.3g) = %0.3g, %s\n' % (df, t, cs_util.print_p(p))
    return text_result


def welch_t_test(pdf, var_name, grouping_name):
    """ Welch's t-test

    :param pdf: pandas data frame
    :param var_name: name of the dependent variable
    :param grouping_name: name of the grouping variable
    :return: html text with APA format result
    """
    dummy_groups, [var1, var2] = cs_stat._split_into_groups(pdf, var_name, grouping_name)
    t, p = stats.ttest_ind(var1.dropna(), var2.dropna(), equal_var=False)
    # http://msemac.redwoods.edu/~darnold/math15/spring2013/R/Activities/WelchTTest.html
    n1 = len(var1)
    n2 = len(var2)
    A = np.std(var1)/n1
    B = np.std(var2)/n2
    df = (A+B)**2/(A**2/(n1-1)+B**2/(n2-1))
    return _("Result of Welch's unequal variances t-test:") + \
           ' <i>t</i>(%0.3g) = %0.3g, %s\n' % (df, t, cs_util.print_p(p))


def mann_whitney_test(pdf, var_name, grouping_name):
    """Mann-Whitney test

    arguments:
    var_name (str):
    grouping_name (str):
    """
    # Not available in statsmodels
    text_result = ''

    dummy_groups, [var1, var2] = cs_stat._split_into_groups(pdf, var_name, grouping_name)
    try:
        u, p = stats.mannwhitneyu(var1.dropna(), var2.dropna(), alternative='two-sided')
        text_result += _('Result of independent samples Mann-Whitney rank test: ') + '<i>U</i> = %0.3g, %s\n' % \
                       (u, cs_util.print_p(p))
    except:
        try:  # older versions of mannwhitneyu do not include the alternative parameter
            u, p = stats.mannwhitneyu(var1.dropna(), var2.dropna())
            text_result += _('Result of independent samples Mann-Whitney rank test: ') + '<i>U</i> = %0.3g, %s\n' % \
                           (u, cs_util.print_p(p * 2))
        except Exception as e:
            text_result += _('Result of independent samples Mann-Whitney rank test: ') + str(e)

    return text_result


def two_way_anova(pdf, var_name, grouping_names):
    """Two-way ANOVA

    Arguments:
    pdf (pd dataframe)
    var_name (str):
    grouping_names (list of str):
    """
    # TODO extend it to multi-way ANOVA
    text_result = ''

    # http://statsmodels.sourceforge.net/stable/examples/generated/example_interactions.html#one-way-anova
    from statsmodels.formula.api import ols
    from statsmodels.stats.anova import anova_lm
    data = pdf.dropna(subset=[var_name] + grouping_names)
    # from IPython import embed; embed()
    # FIXME If there is a variable called 'C', then patsy is confused whether C is the variable or the categorical variable
    # http://gotoanswer.stanford.edu/?q=Statsmodels+Categorical+Data+from+Formula+%28using+pandas%
    # http://stackoverflow.com/questions/22545242/statsmodels-categorical-data-from-formula-using-pandas
    # http://stackoverflow.com/questions/26214409/ipython-notebook-and-patsy-categorical-variable-formula
    anova_model = ols(str('%s ~ C(%s) + C(%s) + C(%s):C(%s)' % (var_name, grouping_names[0], grouping_names[1], grouping_names[0], grouping_names[1])), data=data).fit()
    anova_result = anova_lm(anova_model, typ=3)
    text_result += _('Result of two-way ANOVA:' + '\n')
    # Main effects
    for group_i, group in enumerate(grouping_names):
        text_result += _('Main effect of %s: ' % group) + '<i>F</i>(%d, %d) = %0.3g, %s\n' % \
                       (anova_result['df'][group_i+1], anova_result['df'][4], anova_result['F'][group_i+1],
                        cs_util.print_p(anova_result['PR(>F)'][group_i+1]))
    # Interaction effects
    text_result += _('Interaction of %s and %s: ') % (grouping_names[0], grouping_names[1]) + '<i>F</i>(%d, %d) = %0.3g, %s\n' % \
                   (anova_result['df'][3], anova_result['df'][4], anova_result['F'][3], cs_util.print_p(anova_result['PR(>F)'][3]))

    """ # TODO
    # http://en.wikipedia.org/wiki/Effect_size#Omega-squared.2C_.CF.892
    omega2 = (anova_result['sum_sq'][0] - (anova_result['df'][0] * anova_result['mean_sq'][1])) / (
                (anova_result['sum_sq'][0] + anova_result['sum_sq'][1]) + anova_result['mean_sq'][1])
    text_result += _('Effect size: ') + '&omega;<sup>2</sup> = %0.3g\n' % omega2
    """

    """ # TODO
    # http://statsmodels.sourceforge.net/stable/stats.html#multiple-tests-and-multiple-comparison-procedures
    if anova_result['PR(>F)'][0] < 0.05:  # post-hoc
        post_hoc_res = sm.stats.multicomp.pairwise_tukeyhsd(np.array(data[var_name]), np.array(data[grouping_name]),
                                                            alpha=0.05)
        text_result += '\n' + _(u'Groups differ. Post-hoc test of the means.') + '\n'
        text_result += ('<fix_width_font>%s\n<default>' % post_hoc_res).replace(' ', u'\u00a0')
        ''' # TODO create our own output
        http://statsmodels.sourceforge.net/devel/generated/statsmodels.sandbox.stats.multicomp.TukeyHSDResults.html#statsmodels.sandbox.stats.multicomp.TukeyHSDResults
        These are the original data:
        post_hoc_res.data
        post_hoc_res.groups

        These are used for the current output:
        post_hoc_res.groupsunique
        post_hoc_res.meandiffs
        post_hoc_res.confint
        post_hoc_res.reject
        '''
    """
    return text_result


def kruskal_wallis_test(pdf, var_name, grouping_name):
    """Kruskal-Wallis test

    Arguments:
    var_name (str):
    grouping_name (str):
    """
    # Not available in statsmodels
    text_result = ''

    dummy_groups, variables = cs_stat._split_into_groups(pdf, var_name, grouping_name)
    variables = [variable.dropna() for variable in variables]
    try:
        H, p = stats.kruskal(*variables)
        df = len(dummy_groups)-1
        n = len(pdf[var_name].dropna())  # TODO Is this OK here?
        text_result += _('Result of the Kruskal-Wallis test: ')+'&chi;<sup>2</sup>(%d, <i>N</i> = %d) = %0.3g, %s\n' % \
                                                                (df, n, H, cs_util.print_p(p))  # χ2(1, N=90)=0.89, p=.35
        if p < 0.05:
            # Run the post hoc tests
            text_result += '\n' + _('Groups differ. Post-hoc test of the means.') + '\n'
            text_result += _("Results of Dunn's test (p values).") + '\n'
            posthoc_result = scikit_posthocs.posthoc_dunn(pdf.dropna(subset=[grouping_name]),
                                                          val_col=var_name, group_col=grouping_name)
            text_result += cs_stat._format_html_table(posthoc_result.to_html(classes="table_cs_pd",
                                                                     float_format=lambda x : '%.3f'%x))

    except Exception as e:
        text_result += _('Result of the Kruskal-Wallis test: ')+str(e)

    return text_result