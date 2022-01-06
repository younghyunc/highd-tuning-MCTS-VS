import torch
import botorch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import random
from benchmark import get_problem
from LamctsVS.MCTS import MCTS
from utils import save_args


parser = argparse.ArgumentParser()
parser.add_argument('--func', default='hartmann6_50', type=str)
parser.add_argument('--max_samples', default=200, type=int)
parser.add_argument('--feature_batch_size', default=2, type=int)
parser.add_argument('--sample_batch_size', default=3, type=int)
parser.add_argument('--min_num_variables', default=7, type=int)
parser.add_argument('--select_right_threshold', default=5, type=int)
parser.add_argument('--turbo_max_evals', default=50, type=int)
parser.add_argument('--Cp', default=0.1, type=float)
parser.add_argument('--ipt_solver', default='bo', type=str)
parser.add_argument('--uipt_solver', default='bestk', type=str)
parser.add_argument('--root_dir', default='theory_logs', type=str)
parser.add_argument('--postfix', default=None, type=str)
parser.add_argument('--seed', default=2021, type=int)
args = parser.parse_args()

print(args)

random.seed(args.seed)
np.random.seed(args.seed)
botorch.manual_seed(args.seed)
torch.manual_seed(args.seed)

algo_name = 'lamcts_vs_f'
if args.postfix is not None:
    algo_name += ('_' + args.postfix)
save_config = {
    'save_interval': 50,
    'root_dir': 'logs/' + args.root_dir,
    'algo': algo_name,
    'func': args.func,
    'seed': args.seed
}
f = get_problem(args.func, save_config, args.seed)

save_args(
    'config/' + args.root_dir,
    algo_name,
    args.func,
    args.seed,
    args
)

agent = MCTS(
    func=f,
    dims=f.dims,
    lb=f.lb,
    ub=f.ub,
    feature_batch_size=args.feature_batch_size,
    sample_batch_size=args.sample_batch_size,
    Cp=args.Cp,
    min_num_variables=args.min_num_variables, 
    select_right_threshold=args.select_right_threshold, 
    split_type='median',
    ipt_solver=args.ipt_solver, 
    uipt_solver=args.uipt_solver,
    turbo_max_evals=args.turbo_max_evals,
)

agent.search(max_samples=args.max_samples, verbose=False)

t, selected_variables = zip(*agent.selected_variables)

print(t)
print(selected_variables)
n_selected = [len(selected) for selected in selected_variables]

# TP
TP = []
for selected in selected_variables:
    TP.append(len(set(range(len(f.valid_idx))) & set(selected)))
print('TP:', TP)

recall = [t / len(f.valid_idx) for t in TP]
precision = [TP[idx] / len(selected_variables[idx]) for idx in range(len(TP))]

print('recall:', recall)
print('precision:', precision)

plt.figure()
plt.plot(recall)
plt.title('recall')
plt.savefig('theory_result/recall_{}.png'.format(args.seed))

plt.figure()
plt.plot(precision)
plt.title('precision')
plt.savefig('theory_result/precision_{}.png'.format(args.seed))

recall_pd = pd.DataFrame(zip(t, recall, n_selected), columns=['t', 'recall', 'n'])
precision_pd = pd.DataFrame(zip(t, precision, n_selected), columns=['t', 'precision', 'n'])
recall_pd.to_csv('theory_result/recall_{}.csv'.format(args.seed))
precision_pd.to_csv('theory_result/precision_{}.csv'.format(args.seed))

n_selected_pd = pd.DataFrame(zip(t, n_selected), columns=['t', 'n'])
n_selected_pd.to_csv('theory_result/n_selected_{}.csv'.format(args.seed))

# 
# delta = []
# for selected in selected_variables:
#     delta.append(len(set(range(len(f.valid_idx))) - set(selected)))
    
# print('delta:', delta)
# res = [np.sum(delta[: idx+1]) / (idx + 1) for idx in range(len(delta))]
# print(res)
# plt.figure()
# plt.plot(res)
# plt.savefig('theory_result/lamcts_f.png')

print('best f(x):', agent.value_trace[-1][1])
