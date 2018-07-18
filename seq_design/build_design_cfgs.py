# Getting the configs and shell scripts right for sequence design is important.
# Given a CSV table containing the info for each experiment, build the config files for each experiment,
# as well as matching shell scripts.
# The shell scripts have numbers to help keep track of each experiment.

import sys
import os
import pandas
import ConfigParser

# which promoter is this?
PROMOTERS = {'GPD':'TACGTAAATAATTAATAGTAGTGACNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNTGTCTGGGTGNNNNNNNNNNNGGCATCCANNNNNNNNNNNNNNNNNNNNNNNNNGGCATCCANNNNNNNNATCCCAGCCANNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNGTATATAAAGMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMCACCAAGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHATGTCTAAAGGTGAAGAATTATTCAC',
             'ZEV':'TTTATCATTATCAATACTCGCCATTTCAAAGAATACGTAAATAATTAATAGTAGTGACNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNGCGTGGGCGNNNNNNNGCGTGGGCGNNNNNNNNNGCGTGGGCGNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNATAAGTATATAAAGACGGMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMCACCAAGHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHATGTCTAAAGGTGAAGAATTATTCACTGGTGTTGTCCCAATTTTGGTTGAATTAGATGG'} 
OBJECTIVES = {'Strength':['strong','np.mean'],
              'Induced strength':['induced','seq_evolution.get_induced'],
              'AR + useful':['useful','seq_evolution.merge_outputs_AR_useful']} # what are we optimizing for? (controls merge_outputs)
FILTERS = {'TRUE':['gcfilter','seq_evolution.gc_filter'],'FALSE':['nofilter','lambda x: 0']} # Are we applying the GC content filter? (controls seq_scores)
FUNCTIONS = {'mean':['mean','np.mean'],'mean-sd':['1sd','seq_evolution.mean_minus_sd']} # How are we combining the outputs from each model?
STRATEGIES = {'Screening':['screen','10000','seq_screening.py'],
              'Evolution to threshold':['evolve-thresh','100','seq_evolve_to_threshold.py'],
              'Evolution: cycle-limited':['evolve-cycle','100','seq_evolution.py']} # What evolution/screening strategy are we using?

THRESHOLDS = {'GPD|Strength|Screening': '0.45',
              'GPD|Strength|Evolution to threshold': '0.7',
              'GPD|Strength|Evolution: cycle-limited': '0.7',
              'ZEV|Induced strength|Screening': '1.6',
              'ZEV|Induced strength|Evolution to threshold': '1.8',
              'ZEV|Induced strength|Evolution: cycle-limited': '1.8',
              'ZEV|AR + useful|Screening': '2.6',
              'ZEV|AR + useful|Evolution to threshold': '2.8',
              'ZEV|AR + useful|Evolution: cycle-limited': '2.8'}

if __name__ == '__main__':
  exps = pandas.read_csv(sys.argv[1])
  assert(all(exps['Promoter'] in PROMOTERS))
  assert(all(exps['Objective'] in OBJECTIVES))
  assert(all(exps['Filter'] in FILTERS))
  assert(all(exps['Function'] in FUNCTIONS))
  assert(all(exps['Strategy'] in STRATEGIES))
  
  for i, (promoter, objective, filter, function, strategy) in enumerate(zip(exps['Promoter'], exps['Objective'], exps['Filter'], exps['Function'], exps['Strategy'])):
    fn_stem = '_'.join([promoter, OBJECTIVES[objective][0], FILTERS[filter][0], FUNCTIONS[function][0], STRATEGIES[strategy][0]])
    cfg = ConfigParser.RawConfigParser()
    cfg.add_section('Dirs')
    cfg.set('Dirs','weights_dir','~/facs-seq_test/joined/final_weights')
    
    cfg.add_section('Files')
    cfg.set('Files','model_fn','~/facs-seq/models/do_model.py')
    cfg.set('Files','preds_fn','~/facs-seq_test/seq_designs/preds/' + fn_stem + '.csv')
    cfg.set('Files','rejected_fn', '~/facs-seq_test/seq_designs/rejected/' + fn_stem + '.txt')
    cfg.set('Files','selected_fn', '~/facs-seq_test/seq_designs/selected/' + fn_stem + '_selected.txt')
    cfg.set('Files','score_fn', '~/facs-seq_test/seq_designs/scores/' + fn_stem + '.csv')
    
    cfg.add_section('Functions')
    cfg.set('Functions','merge_outputs',OBJECTIVES[objective][1])
    cfg.set('Functions','merge_models',FUNCTIONS[function][1])
    cfg.set('Functions','seq_scores',FILTERS[filter][1])
    cfg.set('Functions','choose_best_seqs','seq_evolution.greedy_choose_best_seqs')
    
    cfg.add_section('Params')
    cfg.set('Params','SEQ',PROMOTERS[promoter][0])
    cfg.set('Params','N','25:25:25:25')
    cfg.set('Params','M','28:09:09:54')
    cfg.set('Params','H','33:33:0:33')
    cfg.set('Params','NUM_SEQS',STRATEGIES[strategy][1])
    cfg.set('Params','NUM_VARIANTS','20')
    cfg.set('Params','WTS_EXT','.h5')
    cfg.set('Params','OUTPUT_NAMES','A,B')
    cfg.set('Params','RANDOM_SEED','2017')
    cfg.set('Params','NUM_ITERS','100')
    cfg.set('Params','REJECT_MOTIFS','GGTCTC,GAGACC')
    cfg.set('Params','THRESH', THRESHOLDS['|'.join([promoter, objective, strategy])]
    cfg.set('Params','NUM_SEQS_FINAL','120')
    cfg.set('Params','PICK_TOP','True')
    cfg.set('Params','NUM_MUTATIONS','5:50,3:30,1:20')
    cfg.set('Params','KEEP_PARENT','True:80,False:20')
    cfg.write(open(os.path.join('designs',str(i) + '_' + fn_stem + '.cfg'), 'w'))
    script = 'nohup time python ' + STRATEGIES[strategy][2] + ' ' + fn_stem + '.cfg > ' str(i) + '_' +  fn_stem + '.log &\n'
    script_fn = os.path.join('designs',str(i) + '_' + fn_stem + '.sh')
    with open(script_fn, 'w') as sf:
      sf.write(script)
    os.system('chmod +x ' + script_fn)