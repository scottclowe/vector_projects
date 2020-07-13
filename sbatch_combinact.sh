#!/bin/bash
#SBATCH -p p100                # partition - should be gpu on MaRS (q), and either p100 or t4 on Vaughan (vremote1)
#SBATCH --exclude=gpu053
#SBATCH --gres=gpu:1           # request GPU(s)
#SBATCH -c 4                   # number of CPU cores
#SBATCH --mem=8G               # memory per node
#SBATCH --time=20:00:00        # max walltime, hh:mm:ss
#SBATCH --array=0-200%10        # array value
#SBATCH --output=logs/cmbnct_rs_cnn_mnist1/%a-%N-%j    # %N for node name, %j for jobID
#SBATCH --job-name=cmbnct_rs_cnn_mnist1

source ~/.bashrc
source activate ~/venvs/combinact

SAVE_PATH="$1"
SEED="$SLURM_ARRAY_TASK_ID"

# Debugging outputs
pwd
which conda
python --version
pip freeze

echo ""
python -c "import torch; print('torch version = {}'.format(torch.__version__))"
python -c "import torch.cuda; print('cuda = {}'.format(torch.cuda.is_available()))"
echo ""

echo "SAVE_PATH=$SAVE_PATH"
echo "SEED=$SEED"

'relu, multi_relu, cf_relu, combinact, l1, l2, l2_lae, abs, max'
python train.py --seed $SEED --save_path $SAVE_PATH --actfun combinact --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun relu --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun multi_relu --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun l2 --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun l2_lae --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun abs --dataset mnist --randsearch
python train.py --seed $SEED --save_path $SAVE_PATH --actfun max --dataset mnist --randsearch