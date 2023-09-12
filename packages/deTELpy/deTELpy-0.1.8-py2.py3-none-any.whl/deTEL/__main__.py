from gooey import Gooey, GooeyParser

from deTEL.eTEL.eTEL import is_valid_file, prep_folder

if __name__ == "__main__":
    from mTEL import mTEL
    from eTEL import eTEL
    # print('main')
else:
    from .mTEL import mTEL
    from .eTEL import eTEL
    # print('no_main')


from wx.core import wx
is_dark = wx.SystemSettings.GetAppearance().IsUsingDarkBackground()

bg_color = '#343434' if is_dark else '#eeeeee'
wbg_color = '#262626' if is_dark else '#ffffff'
fg_color = '#eeeeee' if is_dark else '#000000'

item_default = {
    'error_color': '#ea7878',
    'label_color': fg_color,
    'help_color': fg_color,
    'description_color': fg_color,
    'full_width': False,
    'external_validator': {
        'cmd': '',
    }
}

@Gooey(
    program_name="deTEL",
    program_description="detecting Translation Error Landscape",
    navigation="TABBED",
    default_size=(610, 700),
    terminal_panel_color=bg_color,
    terminal_font_color=fg_color,
    body_bg_color=bg_color,
    header_bg_color=wbg_color,
    footer_bg_color=bg_color,
    sidebar_bg_color=bg_color,
    progress_regex=r"(\d+)%"
)
def main():
    parser = GooeyParser()
    subs = parser.add_subparsers(help="commands", dest="command")

    eTEL_runner = subs.add_parser("eTEL", prog="eTEL")

    eTEL_args = eTEL_runner.add_argument_group("eTEL", description="eTEL detects the empirical translation error landscape.", gooey_options=item_default)
    eTEL_args.add_argument("-f", dest="fasta", required=True,
                           help="search database as codon fasta file", metavar="FILE",
                           type=lambda x: is_valid_file(parser, x), widget="FileChooser", gooey_options=item_default)
    eTEL_args.add_argument("-psm", dest="psm", required=True,
                           help="psm.tsv produced by philisopher", metavar="FILE", widget="FileChooser", gooey_options=item_default)
    eTEL_args.add_argument("-o", dest="output_folder", required=True,
                           help="Output folder", metavar="FILE",
                           type=lambda x: prep_folder(x), widget="DirChooser", gooey_options=item_default)
    eTEL_args.add_argument("-decoy", dest="decoy", required=False,
                           help="decoy prefix (default: rev_)", default="rev_", gooey_options=item_default)
    eTEL_args.add_argument("-p", dest="prefix", required=False,
                           help="prefix for experiment naming", default='substitutions', gooey_options=item_default)
    eTEL_args.add_argument("-tol", dest="tol", required=False,
                           help="m/z tolerance, used to filter DP–BP couples that resemble substitutions "
                                "and exclude pairs that resemble known PTM", default=0.005, gooey_options=item_default)
    eTEL_args.add_argument("-TEST", dest="test", required=False,
                           help="For testing only: use only <X> files", default=-1, gooey_options=item_default)

    mTEL_runner = subs.add_parser("mTEL", prog="mTEL")
    mTEL_args = mTEL_runner.add_argument_group("mTEL", description="mTEL uses observed translation errors \nto estimate a multinomial translation error landscape.", gooey_options=item_default)

    mTEL_args.add_argument("-f", dest="all_files", required=True, help="Folder with codon_count and error files",
                        metavar="FILE", type=lambda x: is_valid_file(parser, x), widget="DirChooser",
                        # default="tests/resources/results_ionquant2",
                           gooey_options=item_default)
    mTEL_args.add_argument("-r", dest="trna_count", required=True, help="tRNA count file", metavar="FILE",
                           # default="tests/resources/tRNA_count/yeast_tRNA_count.csv",
                        type=lambda x: is_valid_file(parser, x), widget="FileChooser", gooey_options=item_default)
    mTEL_args.add_argument("-o", dest="output_folder", required=True, help="Output folder", metavar="FILE",
                           # default="tests/output",
                        type=lambda x: prep_folder(x), widget="DirChooser", gooey_options=item_default)
    mTEL_args.add_argument("-s", dest="samples", required=True, type=int, help="Number of samples",
                            # default="250",
                           gooey_options=item_default)
    mTEL_args.add_argument("-p", dest="post_samples", required=True, type=int, help="Posterior samples",
                           # default="100",
                           gooey_options=item_default)
    mTEL_args.add_argument("-c", dest="cell_vol", required=False, help="Cell Volume", type=float, default=4.2e-17, gooey_options=item_default)
    mTEL_args.add_argument("-t", dest="thinning", required=False, help="Thinning", type=int, default=10, gooey_options=item_default)
    mTEL_args.add_argument("-b", dest="burnin", required=False, help="Burn-in", type=int, default=100, gooey_options=item_default)
    mTEL_args.add_argument("-nb", dest="num_bootsrap", required=False, help="Number of subsamples performed", type=int,
                        default=-1, gooey_options=item_default)
    mTEL_args.add_argument("-os", dest="out_suffix", required=False, help="suffix added to output files (default: date)",
                        type=str, default="", gooey_options=item_default)
    mTEL_args.add_argument("-a", dest="aggregate", required=False, type=str, default="n",
                        help="aggregate all datasets by summation (y,n) Default: No (n)", gooey_options=item_default)

    args = parser.parse_args()
    run(args)
    # convert(args.input_file, args.output_file)


def run(args):
    if args.command == "eTEL":
        eTEL.run(args)
    elif args.command == "mTEL":
        mTEL.run(args)


import sys

mode = sys.argv[1:]
# print(mode)
if len(mode) == 0:
    main()
    exit(1)
else:
    if mode[0] == 'mTEL':
        mTEL.run(sys.argv[2:])
    elif mode[0] == 'eTEL':
        eTEL.run(sys.argv[2:])
    else:
        print('Argument error. Argument length: ', len(mode))
        exit(1)
