
# Given a sequence, find whether it has an upstream TATA box, and determine the box's position and strength
# define position as the first base of the motif
# define strength as the mean loss in strength due to a mutation in the motif
# if there are multiple TATA boxes, return the strongest
import sys
import os
import numpy as np
import pandas as pd

DNA = ['A','C','G','T']
BIG_POS = 100000.

# 'seq_mat' is a score matrix; row for each position, column for each base (A,C,G,T)
# for each possible window, find if the subsequence matches the motif; if yes, get the mean score diff of all mutations
# return the index and score of the biggest motif

def mat_to_seq_and_score(mat):
  ans = []
  muts = 0.
  mat = np.abs(mat)
  for i in range(mat.shape[0]):
    if np.all(mat[i,:] == np.array([0.,0.,0.,0.])):
      ans.append('N')
    else:
      idx = np.where(mat[i,:] == np.min(mat[i,:]))[0]
      assert idx.shape == (1,)
      ans.append(DNA[idx[0]])
      muts.append(np.sum(mat[i,:])) # will be the 3 values we need plus 0.
  seq = ''.join(ans)
  num_muts = mat.shape[0]*(mat.shape[1] - 1)
  return (seq, muts/num_muts)

def find_strength_pos(seq_mat, seq):
  min_score = BIG_POS
  min_pos = -1
  for i in range(seq_mat.shape[0] - len(seq) + 1):
    window = seq_mat[i:i+len(seq),]
    (w_seq, score) = mat_to_seq_and_score(window)
    if w_seq == seq:
      min_score = min(min_score, score)
      min_pos = i

  return(min_score, min_pos)

def process_one_file(fn_in, fn_out, dir_single_muts, motif_seq, min_pos, max_pos):
  dat_in = pd.read_csv(fn_in)
  dat_in = dat_in[min_pos:max_pos,:]
  fn_stem = fn_in.split('/')[-1]
  fn_stem = '.'.join(fn_stem.split('.')[:-1])
  scores = []
  poses = []
  for i in range(dat_in.shape[0]):
    fn_muts = os.path.join(dir_single_muts, fn_stem + '_' + str(i) + '_single.csv')
    mat_muts = np.loadtxt(fn_muts, delimiter = ',')
    (score, pos) = find_strength_pos(mat_muts, motif_seq)
    scores.append(score); poses.append(pos)
  dat_in['Mut_score'] = scores
  dat_in['Pos'] = poses
  dat_in.to_csv(fn_out)

def main(fn_csv):
  with open(fn_csv, 'r') as fi:
    for l in fi:
      [fn_in, fn_out, dir_single_muts, motif_seq, min_pos, max_pos] = l.strip().split(',')
      [fn_in, fn_out, dir_single_muts] = [os.path.expanduser(q) for q in [fn_in, fn_out, dir_single_muts]]
      min_pos = int(min_pos); max_pos = int(max_pos)
      process_one_file(fn_in, fn_out, dir_single_muts, motif_seq, min_pos, max_pos)

if __name__ == '__main__':
  main(sys.argv[1])