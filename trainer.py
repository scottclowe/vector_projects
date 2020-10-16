import torch
import torch.utils.data
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ExponentialLR
from torch.optim.lr_scheduler import CyclicLR
from torch.optim.lr_scheduler import OneCycleLR
import torch.nn.functional as F

import math
from models import mlp
from models import cnn
from models import preact_resnet
import util
import hyper_params as hp

import numpy as np
import csv
import time


# -------------------- Loading Model
def load_model(model, dataset, actfun, k, p, g, num_params, perm_method, device, resnet_ver, resnet_width, verbose):

    model_params = []

    if dataset == 'mnist' or dataset == 'fashion_mnist':
        input_channels, input_dim, output_dim = 1, 28, 10
    elif dataset == 'cifar10' or dataset == 'svhn':
        input_channels, input_dim, output_dim = 3, 32, 10
    elif dataset == 'cifar100':
        input_channels, input_dim, output_dim = 3, 32, 100

    if model == 'nn' or model == 'mlp':
        if dataset == 'mnist' or dataset == 'fashion_mnist':
            input_dim = 784
        elif dataset == 'cifar10' or dataset == 'svhn':
            input_dim = 3072
        elif dataset == 'cifar100':
            input_dim = 3072
        model = mlp.MLP(actfun=actfun,
                        input_dim=input_dim,
                        output_dim=output_dim,
                        k=k,
                        p=p,
                        g=g,
                        num_params=num_params,
                        permute_type=perm_method).to(device)
        model_params.append({'params': model.batch_norms.parameters(), 'weight_decay': 0})
        model_params.append({'params': model.linear_layers.parameters()})
        if actfun == 'combinact':
            model_params.append({'params': model.all_alpha_primes.parameters(), 'weight_decay': 0})

    elif model == 'cnn':
        model = cnn.CNN(actfun=actfun,
                        num_input_channels=input_channels,
                        input_dim=input_dim,
                        num_outputs=output_dim,
                        k=k,
                        p=p,
                        g=g,
                        num_params=num_params,
                        permute_type=perm_method).to(device)

        model_params.append({'params': model.conv_layers.parameters()})
        model_params.append({'params': model.pooling.parameters()})
        model_params.append({'params': model.batch_norms.parameters(), 'weight_decay': 0})
        model_params.append({'params': model.linear_layers.parameters()})
        if actfun == 'combinact':
            model_params.append({'params': model.all_alpha_primes.parameters(), 'weight_decay': 0})

    elif model == 'resnet':
        model = preact_resnet.PreActResNet(resnet_ver=resnet_ver,
                                           actfun=actfun,
                                           in_channels=input_channels,
                                           out_channels=output_dim,
                                           k=k,
                                           p=p,
                                           g=g,
                                           permute_type=perm_method,
                                           width=resnet_width,
                                           verbose=verbose).to(device)

        model_params = model.parameters()

    return model, model_params


# -------------------- Setting Up & Running Training Function
def train(args, checkpoint, mid_checkpoint_location, final_checkpoint_location, best_checkpoint_location,
          actfun, curr_seed, outfile_path, fieldnames, train_loader, validation_loader, sample_size,
          batch_size, device, num_params, curr_k=2, curr_p=1, curr_g=1, perm_method='shuffle'):
    """
    Runs training session for a given randomized model
    :param args: arguments for this job
    :param checkpoint: current checkpoint
    :param checkpoint_location: output directory for checkpoints
    :param actfun: activation function currently being used
    :param curr_seed: seed being used by current job
    :param outfile_path: path to save outputs from training session
    :param fieldnames: column names for output file
    :param train_loader: training data loader
    :param validation_loader: validation data loader
    :param sample_size: number of training samples used in this experiment
    :param batch_size: number of samples per batch
    :param device: reference to CUDA device for GPU support
    :param num_params: number of parameters in the network
    :param curr_k: k value for this iteration
    :param curr_p: p value for this iteration
    :param curr_g: g value for this iteration
    :param perm_method: permutation strategy for our network
    :return:
    """

    if actfun == 'relu':
        curr_k = 1
        resnet_ver = args.resnet_ver
        resnet_width = args.resnet_width
    else:
        resnet_ver = args.resnet_ver
        resnet_width = args.resnet_width + math.ceil(curr_k/2)
    if args.model != 'resnet':
        resnet_ver = 0
        resnet_width = 0

    actfuns_1d = ['relu', 'abs', 'swish', 'leaky_relu']
    if actfun in actfuns_1d:
        curr_k = 1

    model, model_params = load_model(args.model, args.dataset, actfun, curr_k, curr_p, curr_g, num_params=num_params,
                                     perm_method=perm_method, device=device, resnet_ver=resnet_ver,
                                     resnet_width=resnet_width, verbose=args.verbose)

    util.seed_all(curr_seed)
    rng = np.random.RandomState(curr_seed)
    model.apply(util.weights_init)

    print("=============================== Hyper params:")
    i = 0
    for name, param in model.named_parameters():
        # print(name, param.shape)
        if len(param.shape) == 4:
            print(param[:2, :2, :4, :4])
            break
        elif len(param.shape) == 3:
            print(param[:2, :2, :2])
        elif len(param.shape) == 2:
            print(param[:4, :4])
            break
        elif len(param.shape) == 1:
            print(param[:3])
        print()
        i += 1
        if i == 4:
            break
    print("===================================================================")

    criterion = nn.CrossEntropyLoss()
    hyper_params = hp.get_hyper_params(args, args.model, args.dataset, actfun, rng=rng, exp=args.hyper_params, p=curr_p)

    num_epochs = args.num_epochs
    if args.overfit:
        num_epochs = 50

    optimizer = optim.RMSprop(model_params)
    scheduler = ExponentialLR(optimizer, gamma=args.lr_gamma)
    epoch = 1

    if checkpoint is not None:
        model.load_state_dict(checkpoint['state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        scheduler.load_state_dict(checkpoint['scheduler'])
        epoch = checkpoint['epoch']
        model.to(device)
        print("*** LOADED CHECKPOINT ***"
              "\n{}"
              "\nSeed: {}"
              "\nEpoch: {}"
              "\nActfun: {}"
              "\nNum Params: {}"
              "\nSample Size: {}"
              "\np: {}"
              "\nk: {}"
              "\ng: {}"
              "\nperm_method: {}".format(mid_checkpoint_location, checkpoint['curr_seed'],
                                         checkpoint['epoch'], checkpoint['actfun'],
                                         checkpoint['num_params'], checkpoint['sample_size'],
                                         checkpoint['p'], checkpoint['k'], checkpoint['g'],
                                         checkpoint['perm_method']))

    util.print_exp_settings(curr_seed, args.dataset, outfile_path, args.model, actfun, hyper_params,
                            util.get_model_params(model), sample_size, model.k, model.p, model.g,
                            perm_method, resnet_ver, resnet_width, args.validation)

    best_val_acc = 0

    # ---- Start Training
    while epoch <= num_epochs:

        if args.check_path != '':
            torch.save({'state_dict': model.state_dict(),
                        'optimizer': optimizer.state_dict(),
                        'scheduler': scheduler.state_dict(),
                        'curr_seed': curr_seed,
                        'epoch': epoch,
                        'actfun': actfun,
                        'num_params': num_params,
                        'sample_size': sample_size,
                        'p': curr_p, 'k': curr_k, 'g': curr_g,
                        'perm_method': perm_method
                        }, mid_checkpoint_location)

        util.seed_all((curr_seed * args.num_epochs) + epoch)
        start_time = time.time()
        scaler = torch.cuda.amp.GradScaler()

        # ---- Training
        model.train()
        for batch_idx, (x, targetx) in enumerate(train_loader):
            # print(batch_idx)
            x, targetx = x.to(device), targetx.to(device)
            optimizer.zero_grad()
            with torch.cuda.amp.autocast():
                output = model(x)
                train_loss = criterion(output, targetx)
            scaler.scale(train_loss).backward()
            scaler.step(optimizer)
            scaler.update()

        alpha_primes = []
        alphas = []
        if model.actfun == 'combinact':
            for i, layer_alpha_primes in enumerate(model.all_alpha_primes):
                curr_alpha_primes = torch.mean(layer_alpha_primes, dim=0)
                curr_alphas = F.softmax(curr_alpha_primes, dim=0).data.tolist()
                curr_alpha_primes = curr_alpha_primes.tolist()
                alpha_primes.append(curr_alpha_primes)
                alphas.append(curr_alphas)

        model.eval()
        with torch.no_grad():
            total_train_loss, n, num_correct, num_total = 0, 0, 0, 0
            for batch_idx, (x, targetx) in enumerate(train_loader):
                x, targetx = x.to(device), targetx.to(device)
                output = model(x)
                train_loss = criterion(output, targetx)
                total_train_loss += train_loss
                n += 1
                _, prediction = torch.max(output.data, 1)
                num_correct += torch.sum(prediction == targetx.data)
                num_total += len(prediction)
            eval_train_loss = total_train_loss / n
            eval_train_acc = num_correct * 1.0 / num_total

            total_val_loss, n, num_correct, num_total = 0, 0, 0, 0
            for batch_idx2, (y, targety) in enumerate(validation_loader):
                y, targety = y.to(device), targety.to(device)
                output = model(y)
                val_loss = criterion(output, targety)
                total_val_loss += val_loss
                n += 1
                _, prediction = torch.max(output.data, 1)
                num_correct += torch.sum(prediction == targety.data)
                num_total += len(prediction)
            eval_val_loss = total_val_loss / n
            eval_val_acc = num_correct * 1.0 / num_total

        lr = 0
        for param_group in optimizer.param_groups:
            lr = param_group['lr']
        print(
            "    Epoch {}: LR {:1.5f}  |  train_acc {:1.5f}  |  val_acc {:1.5f}  |  train_loss {:1.5f}  |  val_loss {:1.5f}  |  time = {:1.5f}"
                .format(epoch, lr, eval_train_acc, eval_val_acc, eval_train_loss, eval_val_loss, (time.time() - start_time)), flush=True
        )

        if args.hp_idx is None:
            hp_idx = -1
        else:
            hp_idx = args.hp_idx

        # Outputting data to CSV at end of epoch
        with open(outfile_path, mode='a') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames, lineterminator='\n')
            writer.writerow({'dataset': args.dataset,
                             'seed': curr_seed,
                             'epoch': epoch,
                             'time': (time.time() - start_time),
                             'actfun': model.actfun,
                             'sample_size': sample_size,
                             'hyper_params': hyper_params,
                             'model': args.model,
                             'batch_size': batch_size,
                             'alpha_primes': alpha_primes,
                             'alphas': alphas,
                             'num_params': util.get_model_params(model),
                             'var_nparams': args.var_n_params,
                             'var_nsamples': args.var_n_samples,
                             'k': curr_k,
                             'p': curr_p,
                             'g': curr_g,
                             'perm_method': perm_method,
                             'gen_gap': float(eval_val_loss - eval_train_loss),
                             'resnet_ver': resnet_ver,
                             'resnet_width': resnet_width,
                             'train_loss': float(eval_train_loss),
                             'val_loss': float(eval_val_loss),
                             'train_acc': float(eval_train_acc),
                             'val_acc': float(eval_val_acc),
                             'hp_idx': hp_idx,
                             'lr_gamma': args.lr_gamma,
                             'curr_lr': lr
                             })

        epoch += 1
        scheduler.step()

        if eval_val_acc > best_val_acc:
            best_val_acc = eval_val_acc
            torch.save({'state_dict': model.state_dict(),
                        'optimizer': optimizer.state_dict(),
                        'scheduler': scheduler.state_dict(),
                        'curr_seed': curr_seed,
                        'epoch': epoch,
                        'actfun': actfun,
                        'num_params': num_params,
                        'sample_size': sample_size,
                        'p': curr_p, 'k': curr_k, 'g': curr_g,
                        'perm_method': perm_method
                        }, best_checkpoint_location)

        torch.save({'state_dict': model.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'scheduler': scheduler.state_dict(),
                    'curr_seed': curr_seed,
                    'epoch': epoch,
                    'actfun': actfun,
                    'num_params': num_params,
                    'sample_size': sample_size,
                    'p': curr_p, 'k': curr_k, 'g': curr_g,
                    'perm_method': perm_method
                    }, final_checkpoint_location)
