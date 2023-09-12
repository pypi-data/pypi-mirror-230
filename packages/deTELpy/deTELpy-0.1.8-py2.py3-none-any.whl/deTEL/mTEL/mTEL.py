from random import choices
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import os
from gooey import Gooey, GooeyParser

from . import mtem
from . import data
from . import mcmc


def is_valid_file(p, arg):
    if not os.path.exists(arg):
        p.error("The file %s does not exist!" % arg)
    else:
        return arg


def prep_folder(arg):
    if not os.path.exists(arg):
        os.mkdir(arg)

    return arg


def run(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="all_files", required=True, help="Folder with codon_count and error files",
                        metavar="FILE", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-r", dest="trna_count", required=True, help="tRNA count file", metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-o", dest="output_folder", required=True, help="Output folder", metavar="FILE",
                        type=lambda x: prep_folder(x))
    parser.add_argument("-s", dest="samples", required=True, type=int, help="Number of samples")
    parser.add_argument("-p", dest="post_samples", required=True, type=int, help="Posterior samples")
    parser.add_argument("-c", dest="cell_vol", required=False, help="Cell Volume", type=float, default=4.2e-17)
    parser.add_argument("-t", dest="thinning", required=False, help="Thinning", type=int, default=10)
    parser.add_argument("-b", dest="burnin", required=False, help="Burn-in", type=int, default=100)
    parser.add_argument("-nb", dest="num_bootsrap", required=False, help="Number of subsamples performed", type=int,
                        default=-1)
    parser.add_argument("-os", dest="out_suffix", required=False, help="suffix added to output files (default: date)",
                        type=str, default="")
    parser.add_argument("-a", dest="aggregate", required=False, type=str, default="n",
                        help="aggregate all datasets by summation (y,n) Default: No (n)")

    args = parser.parse_args(args)

    out_suffix = args.out_suffix
    if out_suffix == "":
        out_suffix = str(date.today())

    aggregate = False if args.aggregate == 'n' else 'True'
    print("\n\n\n")
    print("--------------------------------------------------------------------")
    print(f"Folder with codon_count and error files: {args.all_files}")
    print(f"Aggregate datasets: {aggregate}")
    print(f"tRNA count file: {args.trna_count}")
    print(f"Output folder: {args.output_folder}")
    print(f"Suffix: {out_suffix}")
    print(f"Number of samples: {args.samples}")
    print(f"Posterior samples: {args.post_samples}")
    print(f"Cell Volume: {args.cell_vol}")
    print(f"Thinning: {args.thinning}")
    print(f"Burn-in: {args.burnin}")
    print(f"Number of bootstraps: {args.num_bootsrap}")
    print("--------------------------------------------------------------------")

    Path(args.output_folder).mkdir(parents=True, exist_ok=True)

    global data

    files = os.listdir(args.all_files)
    cc_files = sorted([os.path.join(args.all_files, s) for s in files if 'codon_counts' in s])
    sub_files = sorted([os.path.join(args.all_files, s) for s in files if 'errors' in s])

    if len(cc_files) != len(sub_files):
        raise AssertionError("Not the same number of substitution files and codon count files")

    data_list = len(cc_files) * [None]
    i = 0
    for cc, sub in zip(cc_files, sub_files):
        dataset = data.DataSet(substitution_file=sub, count_file=cc)
        data_list[i] = dataset
        i = i + 1
    print(f"\tFound {len(data_list)} datasets")

    if aggregate:
        data = data_list[0]
        for i in range(1, len(data_list)):
            data = data + data_list[i]
        data_list = [data]

    model = mtem.MTEM(anticodon_file=args.trna_count, cell_volume=float(args.cell_vol))

    fitting = mcmc.MCMC(model=model)
    ic_pp = np.random.normal(size=2)
    ic_wp = np.random.normal(size=16)

    if args.num_bootsrap > 0:
        pos_means_df = pd.DataFrame(0, columns=['Pos 1', 'Pos 2'], index=range(args.num_bootsrap))
        wobble_means_df = pd.DataFrame(0, columns=model.WC_NUC_PAIRS, index=range(args.num_bootsrap))
        for k in range(args.num_bootsrap):
            bootstrapped_data = choices(data_list, k=len(data_list))
            print(f"\tPerforming Bootstrap {k + 1}/{args.num_bootsrap}")
            fitting.run(int(args.samples), int(args.thinning), int(args.burnin), ic_pp, ic_wp, bootstrapped_data)

            log_lik_trace = fitting.likelihood_trace()
            plt.plot(log_lik_trace)
            plt.savefig(os.path.join(args.output_folder, f"lik_trace_{k + 1}_{out_suffix}.png"))
            plt.close()

            ppp = fitting.position_penalty_posterior(int(args.post_samples))
            pos_means_df.loc[k] = np.mean(ppp, axis=0)
            wpp = fitting.wobble_penalty_posterior(int(args.post_samples))
            wobble_means_df.loc[k] = np.mean(wpp, axis=0)

        pos_means_df.to_pickle(os.path.join(args.output_folder, f"position_bootstrap_{out_suffix}.pkl"))
        wobble_means_df.to_pickle(os.path.join(args.output_folder, f"wobble_bootstrap_{out_suffix}.pkl"))
        pos_means_df.to_csv(os.path.join(args.output_folder, f"position_bootstrap_{out_suffix}.csv"))
        wobble_means_df.to_csv(os.path.join(args.output_folder, f"wobble_bootstrap_{out_suffix}.csv"))

    else:
        fitting.run(int(args.samples), int(args.thinning), int(args.burnin), ic_pp, ic_wp, data_list)
        hist_bins = np.max([int(int(args.post_samples) / 20), 10])

        # TODO: this part is a flipping mess. Needs cleanup
        # save position information
        position_trace = fitting.position_penalty_trace()
        position_trace = pd.DataFrame(position_trace, columns=['Pos1', 'Pos2'])
        position_trace.to_csv(os.path.join(args.output_folder, f"position_trace_{out_suffix}.csv"))
        position_trace.to_pickle(os.path.join(args.output_folder, f"position_trace_{out_suffix}.pkl"))

        ppp = fitting.position_penalty_posterior(int(args.post_samples))
        ppp = pd.DataFrame(ppp, columns=['Pos1', 'Pos2'])
        ppp.to_pickle(os.path.join(args.output_folder, f"position_{out_suffix}.pkl"))
        ppp.hist(density=True, figsize=(7, 4), bins=hist_bins)
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_folder, f"position_{out_suffix}.png"))
        plt.close()
        ppp_mean = np.mean(ppp, axis=0)
        print(ppp_mean)
        ppp_mean.to_csv(os.path.join(args.output_folder, f"position_{out_suffix}.csv"))

        # save wobble information
        wobble_trace = fitting.wobble_penalty_trace()
        wobble_trace = pd.DataFrame(wobble_trace, columns=model.WC_NUC_PAIRS)
        wobble_trace.to_csv(os.path.join(args.output_folder, f"wobble_trace_{out_suffix}.csv"))
        wobble_trace.to_pickle(os.path.join(args.output_folder, f"wobble_trace_{out_suffix}.pkl"))

        wpp = fitting.wobble_penalty_posterior(int(args.post_samples))
        wpp = pd.DataFrame(wpp, columns=model.WC_NUC_PAIRS)
        wpp.to_csv(os.path.join(args.output_folder, f"wobble_{out_suffix}.csv"))
        wpp.to_pickle(os.path.join(args.output_folder, f"wobble_{out_suffix}.pkl"))
        wpp.hist(density=True, figsize=(15, 15), bins=hist_bins)
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_folder, f"wobble_{out_suffix}.png"))
        plt.close()
        wpp_mean = np.mean(wpp, axis=0)
        wpp_mean.to_csv(os.path.join(args.output_folder, f"wobble_{out_suffix}.csv"))
        print(wpp_mean)

        # save likelihood information
        log_lik_trace = fitting.likelihood_trace()
        plt.plot(log_lik_trace)
        plt.tight_layout()
        plt.savefig(os.path.join(args.output_folder, f"lik_trace_{out_suffix}.png"))
        plt.close()
        log_lik_trace = pd.DataFrame(log_lik_trace, columns=['LogLikelihood'])
        log_lik_trace.to_csv(os.path.join(args.output_folder, f"lik_trace_{out_suffix}.csv"))
        log_lik_trace.to_pickle(os.path.join(args.output_folder, f"lik_trace_{out_suffix}.pkl"))

        # calculate substitution probabilities
        wp = model.format_wobble_penalties(np.array(wpp_mean))
        sub_probs = model.calculate_all_substitution_probabilities(np.array(ppp_mean), wp)
        sub_probs.to_csv(os.path.join(args.output_folder, f'fitted_substitution_probabilities_{out_suffix}.csv'))

        # store fitted energies
        df = pd.DataFrame(index=model.CODONS, columns=model.CODONS)
        for codon in model.CODONS:
            df[codon] = model.calculate_detection_parameter(model.CODONS, codon, ppp_mean, wp)
        df.to_csv(os.path.join(args.output_folder, f"fitted_energies_{out_suffix}.csv"))

