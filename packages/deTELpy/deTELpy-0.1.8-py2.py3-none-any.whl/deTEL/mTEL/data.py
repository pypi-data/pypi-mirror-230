from dataclasses import dataclass, field
import pandas as pd


@dataclass
class DataSet:
    substitution_file: str = ""
    count_file: str = ""

    substitutions: pd.DataFrame = field(default_factory=pd.DataFrame, init=True, repr=True)
    counts: pd.DataFrame = field(default_factory=pd.DataFrame, init=True, repr=True)

    # CONSTANTS
    ONE_LETTER_AA: list = field(default_factory=lambda: list("ACDEFGHKLMNPQRSTVWY"), repr=False)  # removed I!
    THREE_LETTER_AA: list = field(default_factory=lambda: ['Ala', 'Cys', 'Asp', 'Glu', 'Phe', 'Gly', 'His', 'Lys',
                                                           'Leu', 'Met', 'Asn', 'Pro', 'Gln', 'Arg', 'Ser', 'Thr',
                                                           'Val', 'Trp', 'Tyr'])
    ONE_TO_THREE: dict = field(default_factory=lambda: {'A': 'Ala', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu', 'F': 'Phe',
                                                        'G': 'Gly', 'H': 'His', 'K': 'Lys', 'L': 'Leu', 'M': 'Met',
                                                        'N': 'Asn', 'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser',
                                                        'T': 'Thr', 'V': 'Val', 'W': 'Trp', 'Y': 'Tyr'})
    # I codons are translated as L
    CODONTABLE: dict = field(default_factory=lambda: {'ATA': 'L', 'ATC': 'L', 'ATT': 'L', 'ATG': 'M', 'ACA': 'T',
                                                      'ACC': 'T', 'ACG': 'T', 'ACT': 'T', 'AAC': 'N', 'AAT': 'N',
                                                      'AAA': 'K', 'AAG': 'K', 'AGC': 'S', 'AGT': 'S', 'AGA': 'R',
                                                      'AGG': 'R', 'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
                                                      'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P', 'CAC': 'H',
                                                      'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q', 'CGA': 'R', 'CGC': 'R',
                                                      'CGG': 'R', 'CGT': 'R', 'GTA': 'V', 'GTC': 'V', 'GTG': 'V',
                                                      'GTT': 'V', 'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
                                                      'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E', 'GGA': 'G',
                                                      'GGC': 'G', 'GGG': 'G', 'GGT': 'G', 'TCA': 'S', 'TCC': 'S',
                                                      'TCG': 'S', 'TCT': 'S', 'TTC': 'F', 'TTT': 'F', 'TTA': 'L',
                                                      'TTG': 'L', 'TAC': 'Y', 'TAT': 'Y', 'TAA': 'Stop', 'TAG': 'Stop',
                                                      'TGC': 'C', 'TGT': 'C', 'TGA': 'Stop', 'TGG': 'W'}, repr=False)
    CODONS: list = field(default_factory=lambda: ["GCA", "GCC", "GCG", "GCT", "TGC", "TGT", "GAC", "GAT", "GAA",
                                                  "GAG", "TTT", "TTC", "GGT", "GGC", "GGA", "GGG", "CAT", "CAC",
                                                  "ATT", "ATC", "ATA", "AAA", "AAG", "TTA", "TTG", "CTT", "CTC",
                                                  "CTA", "CTG", "ATG", "AAT", "AAC", "CCT", "CCC", "CCA", "CCG",
                                                  "CAA", "CAG", "CGT", "CGC", "CGA", "CGG", "AGA", "AGG", "TCT",
                                                  "TCC", "TCA", "TCG", "AGT", "AGC", "ACT", "ACC", "ACA", "ACG",
                                                  "GTT", "GTC", "GTA", "GTG", "TGG", "TAT", "TAC"], repr=False)

    def __post_init__(self):
        # in some cases, there are multiple candidate codons even though the position is uniquely determined. Why?
        if self.count_file != "":
            df = pd.read_csv(self.count_file, index_col=1)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            self.set_codon_count(df=df)
        if self.substitution_file != "":
            subs = pd.read_csv(self.substitution_file)
            self.substitutions = self.create_substitution_matrix(subs, counts=self.counts)

    def create_substitution_matrix(self, df, counts):
        subs = df[['codon', 'destination', 'origin']]
        subs = subs.query("destination != 'False'")  # filter out any potential SRT (that are not also a substitution)
        subs = subs.dropna(axis=0)  # per row
        subs = subs.groupby(['codon', 'destination']).count()
        subs = subs.unstack(fill_value=0.0)
        # remove multilevel created by unstacking df
        subs.columns = subs.columns.droplevel(0)

        if '*' in subs.columns:
            subs.drop('*', axis=1, inplace=True)
        if 'I/L' in subs.columns:
            subs.rename(mapper={'I/L': 'L'}, axis=1, inplace=True)
        if 'L/I' in subs.columns:
            subs.rename(mapper={'L/I': 'L'}, axis=1, inplace=True)

        # add missing amino acid columns (in case some AA where not detected as substitution)
        if any(aa in subs.columns for aa in self.ONE_LETTER_AA):  # df uses one letter code
            subs.columns = [self.ONE_TO_THREE[aa] for aa in subs.columns]

        for aa in self.THREE_LETTER_AA:
            if aa not in subs:
                subs[aa] = 0.0
        # add missing codon rows (in case some codons had no substitution)
        for codon in self.CODONS:
            if codon not in subs.index:
                subs.loc[codon] = 0.0

        subs_per_codon = subs.sum(axis=1)
        # need loop since they are not in the same order, maybe sorting instead?
        for codon in counts.index:
            correct_incorporated = counts.at[codon, 'total_count'] - subs_per_codon.loc[codon]
            subs.at[codon, self.ONE_TO_THREE[self.CODONTABLE[codon]]] = int(correct_incorporated)

        return subs.astype('int32')

    def set_codon_count(self, df):
        if 'TAA' in df.index:
            df = df.drop('TAA')
        if 'TGA' in df.index:
            df = df.drop('TGA')
        if 'TAG' in df.index:
            df = df.drop('TAG')
        self.counts = df.astype('int32')

    def set_substitutions(self, df):
        self.substitutions = df

    def __add__(self, o):
        new_subs = self.substitutions + o.substitutions
        new_cc = self.counts + o.counts

        return DataSet(substitutions=new_subs, counts=new_cc)


if __name__ == "__main__":
    data = DataSet(substitution_file='~/repositories/darkproteome/output/cedric/pxd001714_errors.csv',
                   count_file='~/repositories/darkproteome/output/cedric/pxd001714_codon_count.csv')

