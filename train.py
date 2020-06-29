import torch
import torch.utils.data
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.optim.lr_scheduler import CyclicLR

import models
import util

import argparse
import os
import numpy as np
import datetime
import csv
import time

# -------------------- Optimized Hyper Parameter Settings

_HYPERPARAMS = {
    "relu": {"adam_beta_1": np.exp(-2.375018573261741),
             "adam_beta_2": np.exp(-6.565065478550015),
             "adam_eps": np.exp(-19.607731090387627),
             "adam_wd": np.exp(-11.86635747404571),
             "max_lr": np.exp(-5.7662952418075175),
             "cycle_peak": 0.2935155263985412
             },
    "cf_relu": {"adam_beta_1": np.exp(-4.44857338551192),
                "adam_beta_2": np.exp(-4.669825410890087),
                "adam_eps": np.exp(-17.69933166220988),
                "adam_wd": np.exp(-12.283288733512373),
                "max_lr": np.exp(-8.563504990329884),
                "cycle_peak": 0.10393251332079881
                },
    "multi_relu": {"adam_beta_1": np.exp(-2.859441513546877),
                   "adam_beta_2": np.exp(-5.617992566623951),
                   "adam_eps": np.exp(-20.559015044774018),
                   "adam_wd": np.exp(-12.693844976989661),
                   "max_lr": np.exp(-5.802816398828524),
                   "cycle_peak": 0.28499869111025217
                   },
    "combinact": {"adam_beta_1": np.exp(-2.6436039683427253),
                  "adam_beta_2": np.exp(-7.371516988658699),
                  "adam_eps": np.exp(-16.989022147994522),
                  "adam_wd": np.exp(-12.113778466374383),
                  "max_lr": np.exp(-5.211973674318645),
                  "cycle_peak": 0.4661308739740898
                  },
    "l2": {"adam_beta_1": np.exp(-2.244614412525641),
           "adam_beta_2": np.exp(-5.502197648895974),
           "adam_eps": np.exp(-16.919215725249092),
           "adam_wd": np.exp(-13.99956243808541),
           "max_lr": np.exp(-5.383090612225605),
           "cycle_peak": 0.35037784343793205
           },
    "abs": {"adam_beta_1": np.exp(-3.1576858739457845),
            "adam_beta_2": np.exp(-4.165206705873042),
            "adam_eps": np.exp(-20.430988799955056),
            "adam_wd": np.exp(-13.049933891070697),
            "max_lr": np.exp(-5.809683797646132),
            "cycle_peak": 0.34244342851740034
            },
    "cf_abs": {"adam_beta_1": np.exp(-5.453380890632929),
               "adam_beta_2": np.exp(-5.879222236954101),
               "adam_eps": np.exp(-18.303333640483068),
               "adam_wd": np.exp(-15.152599023560422),
               "max_lr": np.exp(-6.604045812173043),
               "cycle_peak": 0.11189158130301018
               },
    "l2_lae": {"adam_beta_1": np.exp(-2.4561852034212),
               "adam_beta_2": np.exp(-5.176943480470942),
               "adam_eps": np.exp(-16.032458209235187),
               "adam_wd": np.exp(-12.860274699438266),
               "max_lr": np.exp(-5.540947578537945),
               "cycle_peak": 0.40750994546983904
               },
    "max": {"adam_beta_1": np.exp(-2.2169207045481505),
            "adam_beta_2": np.exp(-7.793567052557596),
            "adam_eps": np.exp(-18.23187258333265),
            "adam_wd": np.exp(-12.867866026516422),
            "max_lr": np.exp(-5.416840501318637),
            "cycle_peak": 0.28254869607601146
            }

}


# -------------------- Setting Up & Running Training Function

def train_model(actfun,
                net_struct,
                outfile_path,
                fieldnames,
                seed,
                train_loader,
                validation_loader,
                sample_size,
                device):
    """
    Runs training session for a given randomized model
    :param actfun: what activation type is being used by model
    :param net_struct: structure of our neural network
    :param outfile_path: path to save outputs from training session
    :param fieldnames: column names for output file
    :param seed: seed for randomization
    :param train_loader: training data loader
    :param validation_loader: validation data loader
    :param sample_size: number of training samples used in this experiment
    :param device: reference to CUDA device for GPU support
    :return:
    """

    # ---- Initialization
    model = models.CombinactNN(net_struct=net_struct, actfun=actfun).to(device)
    model.apply(util.weights_init)

    for param in model.linear_layers[0].parameters():
        print(param.data.shape, flush=True)
        print(param.data[:5], flush=True)
    print()

    model_params = [
        {'params': model.linear_layers.parameters()},
        {'params': model.all_batch_norms.parameters(), 'weight_decay': 0}
    ]
    if model.actfun == "combinact":
        model_params.append({'params': model.all_alpha_primes.parameters(),
                             })

    hyper_params = _HYPERPARAMS[actfun]
    optimizer = optim.Adam(model_params,
                           lr=10 ** -8,
                           betas=(hyper_params['adam_beta_1'], hyper_params['adam_beta_2']),
                           eps=hyper_params['adam_eps'],
                           weight_decay=hyper_params['adam_wd']
                           )
    criterion = nn.CrossEntropyLoss()
    scheduler = CyclicLR(optimizer,
                         base_lr=10 ** -8,
                         max_lr=hyper_params['max_lr'],
                         step_size_up=int(hyper_params['cycle_peak'] * 5000),  # 5000 = tot number of batches: 500 * 10
                         step_size_down=int((1 - hyper_params['cycle_peak']) * 5000),
                         cycle_momentum=False
                         )

    # ---- Start Training
    epoch = 1
    while epoch <= 10:

        start_time = time.time()
        final_train_loss = 0
        # ---- Training
        model.train()
        for batch_idx, (x, targetx) in enumerate(train_loader):
            x, targetx = x.to(device), targetx.to(device)
            optimizer.zero_grad()
            output = model(x)
            train_loss = criterion(output, targetx)
            train_loss.backward()
            optimizer.step()
            scheduler.step()
            final_train_loss = train_loss

        # ---- Testing
        num_correct = 0
        num_total = 0
        final_val_loss = 0
        model.eval()
        with torch.no_grad():
            for batch_idx2, (y, targety) in enumerate(validation_loader):
                y, targety = y.to(device), targety.to(device)
                output = model(y)
                val_loss = criterion(output, targety)
                final_val_loss = val_loss
                _, prediction = torch.max(output.data, 1)
                num_correct += torch.sum(prediction == targety.data)
                num_total += len(prediction)
        accuracy = num_correct * 1.0 / num_total

        # Logging test results
        print(
            "    Epoch {}: train_loss = {:1.6f}  |  val_loss = {:1.6f}  |  accuracy = {:1.6f}  |  time = {}"
                .format(epoch, final_train_loss, final_val_loss, accuracy, (time.time() - start_time)), flush=True
        )

        # Outputting data to CSV at end of epoch
        with open(outfile_path, mode='a') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames, lineterminator='\n')
            writer.writerow({'seed': seed,
                             'epoch': epoch,
                             'train_loss': float(final_train_loss),
                             'val_loss': float(final_val_loss),
                             'acc': float(accuracy),
                             'time': (time.time() - start_time),
                             'net_struct': model.net_struct,
                             'model_type': model.actfun,
                             'num_layers': net_struct['num_layers'],
                             'sample_size': sample_size,
                             'hyper_params': hyper_params
                             })

        epoch += 1


def setup_experiment(seed, outfile_path, actfun):
    """
    Retrieves training / validation data, randomizes network structure and activation functions, creates model,
    creates new output file, sets hyperparameters for optimizer and scheduler during training, initializes training
    :param seed: seed for parameter randomization
    :param outfile_path: path to save outputs from experiment
    :param actfun: model architecture
    :return:
    """

    # ---- Create new output file
    fieldnames = ['seed', 'epoch', 'train_loss', 'val_loss', 'acc', 'time', 'net_struct', 'model_type',
                  'num_layers', 'sample_size', 'hyper_params']
    with open(outfile_path, mode='w') as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}

    if actfun == 'relu' or actfun == 'abs':
        net_struct = {
            'num_layers': 2,
            'M': [250, 200],
            'k': [1, 1],
            'p': [1, 1],
            'g': [1, 1]
        }
    else:
        net_struct = {
            'num_layers': 2,
            'M': [250, 200],
            'k': [2, 2],
            'p': [1, 1],
            'g': [1, 1]
        }

    util.print_exp_settings(seed, outfile_path, net_struct, actfun)
    sample_size = 50000

    # ---- Loading MNIST
    util.seed_all(seed + sample_size)
    trans = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    mnist_train_full = datasets.MNIST(root='./data', train=True, download=True, transform=trans)
    train_set_indices = np.random.choice(50000, sample_size, replace=False)
    validation_set_indices = np.arange(50000, 60000)

    mnist_train = torch.utils.data.Subset(mnist_train_full, train_set_indices)
    mnist_validation = torch.utils.data.Subset(mnist_train_full, validation_set_indices)
    batch_size = 100
    train_loader = torch.utils.data.DataLoader(dataset=mnist_train, batch_size=batch_size,
                                               shuffle=True, **kwargs)
    validation_loader = torch.utils.data.DataLoader(dataset=mnist_validation, batch_size=batch_size,
                                                    shuffle=True, **kwargs)

    # ---- Begin training model
    print("------------ Sample Size " + str(sample_size) + "...", flush=True)
    print()
    print("Sample of randomized indices and weights:")
    print(train_set_indices)
    train_model(actfun, net_struct, outfile_path, fieldnames, seed,
                train_loader, validation_loader, sample_size, device)
    print()


# --------------------  Entry Point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--seed', type=int, default=0, help='Job seed')
    parser.add_argument('--actfun', type=str, default='max',
                        help='relu, multi_relu, cf_relu, combinact, l1, l2, l2_lae, abs, max'
                        )
    parser.add_argument('--save_path', type=str, default='', help='Where to save results')
    parser.add_argument('--dataset', type=str, default='perm_inv_mnist', help='Where to save results')
    args = parser.parse_args()

    out = os.path.join(
        args.save_path,
        '{}-{}-{}-{}.csv'.format(datetime.date.today(),
                                 args.actfun,
                                 args.seed,
                                 args.dataset))

    setup_experiment(args.seed,
                     out,
                     args.actfun
                     )
