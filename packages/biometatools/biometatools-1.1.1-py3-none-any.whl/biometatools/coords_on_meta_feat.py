"""
Converts the 5' and 3' coordinates of reads into coordinates on meta-features.
In essence, each feature is divided into bins; the 5' and 3' coordinates of
each read contained in each feature are replaced by the bin index in which
they are included. For example for a feature of length 100 containing a read
with coordinates [5', 3']: [15, 95] the corresponding meta-coordinates for
10 bins are [1, 9]. The script works only for +ve strands. The script will
also output a histogram with the read counts corresponding to each bin in
every feature in the BED file. It will also plot an aggregate histogram for
all BED features combined.
"""


import sys
import pysam
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import multiprocessing
from matplotlib.backends.backend_pdf import PdfPages


def parse_args(args_list):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--ifile", required=True, nargs='+',
                        help="Input SAM/BAM file")
    parser.add_argument("-b", "--bed", required=True,
                        help="BED file with features")
    parser.add_argument("-c", "--bins", default=20, type=int,
                        help="Number of bins per feature. default: %(default)s")
    parser.add_argument("-l", "--min-len", default=200, type=int,
                        help="Skip features shorter than this. default:%(default)s")
    parser.add_argument("-s", "--col_delimiter", default="\t",
                        help="Delimiter for output file, default:<TAB>")
    parser.add_argument("-n", "--iname", nargs='+',
                        help="Name to be used for SAM/BAM file in output table columns")
    parser.add_argument("-o", "--pdf", required=True,
                        help="Output pdf file with plots")
    parser.add_argument("--ohist", required=True,
                        help="Output tab-separated file with histogram numbers'")
    parser.add_argument("--skip-stdout", action='store_true',
                        help="Do not print new coordinates to STDOUT")
    parser.add_argument("--keep-secondary", action='store_true',
                        help="Keep secondary alignments. Default: Ignore them")
    parser.add_argument("-t", "--threads", default=10, type=int,
                        help="Number of threads for parallel processing. default: %(default)s")

    # Parse the argument list.
    args = parser.parse_args(args_list)

    # If provided, ensure the number of names is equal to the number of files.
    if args.iname is not None and len(args.iname) != len(args.ifile):
        raise ValueError(
            'Error: provided --iname values should be same number as files')

    return args


def read_bed_to_dict(bedfile, min_len=None):
    """
    Parse BED file and create a dictionary associating the reference name to
    the corresponding start and end positions.
    """
    region_coords = {}
    with open(bedfile) as bed:
        for line in bed:
            line = line.strip().split("\t")
            if line[5] == "-":
                raise ValueError(
                    'Error: BED entry on negative strand found.\n'+line)
            refid = line[0]
            ref_start = int(line[1])
            ref_end = int(line[2])
            if min_len is not None and (ref_end - ref_start) < min_len:
                continue
            if refid in region_coords:
                raise ValueError(
                    'Error: multiple BED entries on same reference found.\n'+line)
            region_coords[refid] = [ref_start, ref_end]
    return region_coords


def save_figs_in_pdf(figs, pdf):
    """
    Plot the figures in a pdf.
    """
    with PdfPages(pdf) as pages:
        for f in figs:
            pages.savefig(f)
            plt.close()


def create_fig_for_df(df, y, name):
    """
    Create the figure.
    """
    fig, ax = plt.subplots(layout='constrained')
    fig.suptitle(name)
    sns.lineplot(ax=ax, data=df, x='bin', y=y, hue='file', errorbar='se')
    plt.xlabel('Binned position')
    plt.ylabel('Read ' + y)
    return fig


def get_binned_coords(bed_start, bed_end, read_pos, bins):
    """
    Calculate the new binned coords for the read.
    """
    bin_len = (bed_end - bed_start)/bins
    binned_pos = int((read_pos - bed_start)/bin_len)

    if binned_pos < 0 or binned_pos >= bins:
        return None

    return binned_pos


def calc_meta_coords_for_file(ifile, name, bed_coords, print_lock, bins=20,
                              skip_stdout=False, keep_secondary=False,
                              delim='\t'):

    class hist():

        """A simple wrapper class the holds a distribution"""

        def __init__(self, name, bins):
            self.name = name
            self.hist = [0 for _ in range(0, bins)]

        def increment_count_at(self, pos):
            self.hist[pos] += 1

        def total_count(self):
            return sum(self.hist)

    # Identify whether we have a BAM or SAM file.
    filemode = 'rb' if ifile[-3:] == 'bam' else 'r'

    # Define variables.
    transcript_hists = {}
    lib_count = 0

    # Loop on the BAM/SAM file and calculate the bins
    infile = pysam.AlignmentFile(ifile, filemode)
    for read in infile.fetch(until_eof=True):
        if (read.is_unmapped or
            read.is_reverse or
            (read.is_secondary and not keep_secondary)):
            continue

        lib_count += 1

        # This is separate from the above checks because these reads need to
        # be counted in the lib_count.
        if read.reference_name not in bed_coords:
            continue

        rname = read.reference_name
        bstart, bend = bed_coords[rname]
        bin5p = get_binned_coords(bstart, bend, read.reference_start, bins)
        bin3p = get_binned_coords(bstart, bend, read.reference_end-1, bins)

        if read.reference_name not in transcript_hists:
            transcript_hists[rname] = {
                    '5p':hist(rname, bins),
                    '3p':hist(rname, bins)}
        hists = transcript_hists[rname]

        if bin5p is not None:
            hists['5p'].increment_count_at(bin5p)
        if bin3p is not None:
            hists['3p'].increment_count_at(bin3p)

        if not skip_stdout:  # Print the binned coordinates
            with print_lock:
                print(delim.join([name, read.query_name, read.reference_name,
                                  str(bin5p), str(bin3p)]))

    # Prepare all the data in a list of lists to be loaded in a dataframe.
    # Initialize an empty list
    data = []
    for hists in transcript_hists.values():
        for which_end in hists.keys():
            for b in range(bins):
                data.append([name, hists[which_end].name, which_end, b,
                             hists[which_end].hist[b], lib_count])
    df = pd.DataFrame(data, columns=['file', 'ref', 'which_end', 'bin',
                                     'count', 'lib_count'])

    return df


def worker_process(job):
    jid, ifile, iname, coords, bins, delim, skip_stdout, keep_secondary, print_lock = job

    # Calculate meta coordinates for BAM file against the BED entries.
    df = calc_meta_coords_for_file(ifile, iname, coords, print_lock,
                                   bins=bins,
                                   skip_stdout=skip_stdout,
                                   delim=delim,
                                   keep_secondary=keep_secondary)

    return df


def main():
    args = parse_args(sys.argv[1:])
    delim = args.col_delimiter

    # Print header to stdout.
    if not args.skip_stdout:
        print(delim.join(['file', 'qname', 'feat', 'bin5p', 'bin3p']))

    # Parse BED file and create a dict associating the reference name to
    # the corresponding start and end positions.
    coords = read_bed_to_dict(args.bed, args.min_len)

    # Create a manager to hold shared data.
    manager = multiprocessing.Manager()
    print_lock = manager.Lock()
    coords = manager.dict(coords)

    # Define jobs and put them in the queue. One job for each BAM file.
    jobs = []
    for i, ifile in enumerate(args.ifile):
        iname = str(i) if args.iname is None else args.iname[i]
        jobs.append((i, ifile, iname, coords, args.bins, args.col_delimiter,
                     args.skip_stdout, args.keep_secondary, print_lock))

    # Create a pool of worker processes.
    with multiprocessing.Pool(processes=args.threads) as pool:
        dataframes = pool.map(worker_process, jobs)

    # Concatenate all data frames. The data frames contain column 'file',
    # 'which_end' and 'ref' that help distinguish between histograms of
    # different files, 5p/3p and transcripts.
    df = pd.concat(dataframes)
    df.reset_index(drop=True, inplace=True)

    # Aggregate to calculate the total number of reads in each reference and
    # merge with df
    df_agg_ref = df.groupby(['file', 'ref', 'which_end']).agg(
        ref_count=('count', 'sum'),
    ).reset_index()
    df2 = pd.merge(df, df_agg_ref, how="left").dropna()

    # Calculate count density per reference
    df2['density'] = df2['count'] / df2['ref_count']

    # Create figures.
    figs = []
    figs.append(create_fig_for_df(df2[df2['which_end'] == '5p'], 'density', '5p'))
    figs.append(create_fig_for_df(df2[df2['which_end'] == '3p'], 'density', '3p'))
    save_figs_in_pdf(figs, args.pdf)

    # Print the data frame with histograms to a file.
    df.to_csv(args.ohist, sep=delim, index=False)


if __name__ == "__main__":
    main()
