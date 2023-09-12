"""
Plots the distribution of reads in a BAM file around a given set of features
in a BED file. The user can specify which end (5' or 3') of the reads and the
features will be used as reference for the comparison. For example: We assume
that the user selects the 5' end of the reads and the 5' end of the features
as reference. Then a read that maps at position 10 of chr1 will be at a
relative position of -5 nt compared to a feature aligning at position 15 of
chr1. The same concept is applied for all reads against all features and a
distribution of relative positions is constructed.
"""


import pysam
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class Feature:
    def __init__(self, chrom, start, end, strand):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.strand = strand

    def __str__(self):
        return "{}:{}-{}-{}".format(
            self.chrom, self.start, self.end, self.strand)


def get_5p_or_3p_pos(start, end, strand, which_end):
    """
    get_5p_or_3p_pos returns the position of the 5' or 3' end of a region.
    """
    if which_end not in ['5p', '3p']:
        raise ValueError('Incorrectly specified position')
    if strand not in ['+', '-']:
        raise ValueError('Incorrectly specified strand')

    if strand == '-' and which_end == '5p' or strand == '+' and which_end == '3p':
        return end
    return start


def get_rel_pos(feat, read, fpos, rpos):
    """
    get_rel_pos calculates the relative position between the two reference
    positions of a bed and a reads entry.
    """
    feat_pos = get_5p_or_3p_pos(feat.start, feat.end, feat.strand, fpos)

    read_strand = '+' if read.is_forward else '-'
    read_pos = get_5p_or_3p_pos(read.reference_start, read.reference_end - 1,
                                read_strand, rpos)

    rel_pos = read_pos - feat_pos
    if feat.strand == '-':
        rel_pos *= -1
    return rel_pos


def read_length_in_limits(read, minL, maxL):
    """
    read_length_in_limits returns True if the read sequence lengths is within
    given boundaries. False otherwise.
    """
    if minL != None and read.query_length < minL:
        return False
    if maxL != None and read.query_length > maxL:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-m", "--bam", required=True,
                        help="BAM file with reads. Must be indexed.")
    parser.add_argument("-b", "--bed", required=True,
                        help="BED file with features.")
    parser.add_argument("-u", "--up", type=int, default=100,
                        help="Number of nts to plot upstream of fpos. (default: %(default)s)")
    parser.add_argument("-d", "--down", type=int, default=100,
                        help="Number of nts to plot downstream of fpos. (default: %(default)s)")
    parser.add_argument("-f", "--fpos", default='5p', choices=['5p', '3p'],
                        help="Reference point for features; one of 5p or 3p (default: %(default)s)")
    parser.add_argument("-r", "--rpos", default='5p', choices=['5p', '3p'],
                        help="Reference point for reads; one of 5p or 3p (default: %(default)s)")
    parser.add_argument("--plot-feats", action='store_true',
                        help="Also plot a histogram for each BED feature")
    parser.add_argument("--lmin", type=int,
                        help="Minimum length for acceptable reads.")
    parser.add_argument("--lmax", type=int,
                        help="Maximum length for acceptable reads.")
    parser.add_argument("-o", "--pdf", required=True,
                        help="Output pdf file with plot")
    args = parser.parse_args()

    # Initialize a histogram
    positions = list(range(-1 * args.up, args.down + 1))
    hist = {i: 0 for i in positions}

    # Open the bam file
    bamfile = pysam.AlignmentFile(args.bam, "rb")

    # Loop on the BED file and query the BAM file to get overlapping reads for
    # each line. Calculate relative positions and add in the histogram.
    bhists = {}
    with open(args.bed) as bed:
        for line in bed:
            cols = line.strip().split('\t')
            feat = Feature(cols[0], int(cols[1]), int(cols[2]), cols[5])
            bhists[str(feat)] = {i: 0 for i in positions}

            # skip feature if no reads aligned to it.
            if bamfile.header.get_tid(feat.chrom) == -1:
                continue

            ref_len = bamfile.header.get_reference_length(feat.chrom)

            max_pos = max(args.up, args.down)
            qstart = feat.start-max_pos if feat.start-max_pos > 0 else 0
            qend = feat.end+max_pos if feat.end+max_pos > ref_len else ref_len
            reads = bamfile.fetch(feat.chrom, qstart, qend)

            for read in reads:
                if not read_length_in_limits(read, args.lmin, args.lmax):
                    continue

                rel_pos = get_rel_pos(feat, read, args.fpos, args.rpos)
                if rel_pos >= -1 * args.up and rel_pos <= args.down:
                    hist[rel_pos] += 1
                    if args.plot_feats:
                        bhists[str(feat)][rel_pos] += 1

    # Print a table with the histogram to stdout.
    print("\t".join(["pos", "count"]))
    for i in positions:
        print("\t".join([str(i), str(hist[i])]))

    # Plot the histogram in a pdf.
    with PdfPages(args.pdf) as pages:
        values = [hist[i] for i in positions]
        fig = create_fig_for_hist(positions, values, "All")
        pages.savefig(fig)
        plt.close()

        if args.plot_feats:
            for fname, bhist in bhists.items():
                values = [bhist[i] for i in positions]
                fig = create_fig_for_hist(positions, values, fname)
                pages.savefig(fig)
                plt.close()


def create_fig_for_hist(x, y, name):
    fig, ax = plt.subplots(layout='constrained')
    fig.suptitle(name)
    plt.bar(x, y)
    plt.xlabel('Relative position of read to feature')
    plt.ylabel('Read-feature pairs count')
    return fig


if __name__ == "__main__":
    main()
