import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    result_files = {'pos_expl':'log_file_pos_expl.txt',
                    'pos_impl':'log_file_pos_impl.txt',
                    'prec_expl':'log_file_prec_expl.txt',
                    'prec_impl':'log_file_prec_impl.txt'}

    for key in result_files.keys():
        result_files[key] = pd.read_csv(result_files[key]).query('solved==True and n>5').set_index(['seed'])
    for key in result_files.keys():
        result_files[key]['bound'] = result_files[key]['objectivevalue']*(1-result_files[key]['MIPgap'])
    best = pd.DataFrame(columns=result_files['pos_expl'].columns, index=result_files['pos_expl'].index)
    best['n'] = result_files['pos_expl']['n']
    for i in best.index:
        for key in result_files.keys():
            if np.isnan(best.loc[i,'objectivevalue']) or result_files[key].loc[i,'objectivevalue']<best.loc[i,'objectivevalue']:
                best.loc[i,'objectivevalue'] = result_files[key].loc[i,'objectivevalue']
            if np.isnan(best.loc[i,'bound']) or result_files[key].loc[i,'bound']>best.loc[i,'bound']:
                best.loc[i,'bound'] = result_files[key].loc[i,'bound']

    for key in result_files.keys():
        result_files[key]['diff_obj'] = np.nan
        result_files[key]['diff_bound'] = np.nan
        for i in result_files[key].index:
            result_files[key].loc[i,'diff_obj'] = 100*(result_files[key].loc[i,'objectivevalue']-best.loc[i,'objectivevalue'])/(best.loc[i,'objectivevalue'])
            result_files[key].loc[i,'diff_bound'] = 100*(result_files[key].loc[i,'objectivevalue']-best.loc[i,'bound'])/(best.loc[i,'bound'])
        result_files[key]['MIPgap'] = 100*result_files[key]['MIPgap']

    for key in result_files.keys():
        result_files[key]['is_best'] = np.nan
        for i in result_files[key].index:
            result_files[key].loc[i, 'is_best'] = (np.abs(
                (result_files[key].loc[i, 'objectivevalue'] - best.loc[i, 'objectivevalue'])) < 1.e-3).astype(int)

    kpi_aggregator = {'solvingtime':'mean','MIPgap':'mean','diff_bound':'mean','diff_obj':'mean','is_best':'sum'}
    for key in result_files.keys():
        result_files[key] = result_files[key].groupby('n').agg(kpi_aggregator)
        result_files[key].to_csv(f'results_{key}.txt',float_format='%.2f')

    for kpi in kpi_aggregator.keys():
        width = 1  # the width of the bars
        multiplier = 0

        plt.figure()
        ax = plt.subplot(111)

        for key in result_files.keys():
            offset = width * multiplier
            v = result_files[key][kpi]
            plt.bar(v.index+offset, v,label=key)
            multiplier+=1
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax.legend()
        plt.xlabel('n')
        plt.xticks(v.index+width*len(result_files.keys())/2-width/2,v.index)
        if kpi == 'solvingtime':
            plt.title('Solving time')
            plt.ylabel('s')
        if kpi == 'diff_obj':
            plt.title('Gap from best objective')
            plt.ylabel('%')
            plt.ylim([0,5])
        if kpi == 'diff_bound':
            plt.title('Gap from best bound')
            plt.ylabel('%')
            plt.ylim([0,5])
        if kpi == 'MIPgap':
            plt.title('MIP Gap')
            plt.ylabel('%')
        if kpi == 'is_best':
            plt.title('Number of best')
        plt.savefig(f'plot_{kpi}.png')