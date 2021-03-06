#!/usr/bin/env python

"""
########################################################################
# Author:       Carlos A. Ruiz Perez
# Email:        cruizperez3@gatech.edu
# Intitution:   Georgia Institute of Technology
# Version:      0.9
# Date:         March 05, 2020

# Description: Download the latest refseq protein dataset from NCBI and
# the accompanying genbank files necessary to create the database.
########################################################################
"""

################################################################################
"""---0.0 Import Modules---"""
from shutil import which
from shutil import copyfileobj
from shutil import rmtree
import subprocess
from pathlib import Path
import urllib.request
import gzip

################################################################################
"""---1.0 Define Functions---"""
def refseq_fasta_downloader(output_file_folder, ascp_key = None):
    print("Downloading protein fasta files")
    # Requirements
    if ascp_key == None:
        ascp_key = get_aspera_key()
    release_file = urllib.request.urlopen("https://ftp.ncbi.nlm.nih.gov/refseq/release/RELEASE_NUMBER")
    release_number = release_file.readline().decode('utf-8').strip()
    # Create folders
    temp_fasta_files = Path(output_file_folder) / "01.temp_proteins"
    merged_db_folder = Path(output_file_folder) / "01.Protein_DB"
    Path(temp_fasta_files).mkdir(parents=True, exist_ok=True)
    Path(merged_db_folder).mkdir(parents=True, exist_ok=True)
    with open(merged_db_folder / "refseq_release.txt", 'w') as relinfo:
        relinfo.write("Release number {}".format(release_number))
    # Remove refseq fasta files if present (to avoid repeating files)
    if Path(merged_db_folder / "refseq_protein.fasta").is_file():
        Path(merged_db_folder / "refseq_protein.fasta").unlink()
    # Download compressed protein files
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.gpff.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/viral/',
                    temp_fasta_files])
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.gpff.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/bacteria/',
                    temp_fasta_files])
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.gpff.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/archaea/',
                    temp_fasta_files])
    # Get downloaded files
    viral_list = search_all_files(temp_fasta_files / "viral")
    bacteria_list = search_all_files(temp_fasta_files / "bacteria")
    archaea_list = search_all_files(temp_fasta_files / "archaea")
    final_list = viral_list + bacteria_list + archaea_list
    with open(Path(merged_db_folder) / ("refseq_protein.fasta"), 'w') as merged_db:
        for file in final_list:
            with gzip.open(file, 'rt') as temp_file:
                copyfileobj(temp_file,merged_db)
                Path.unlink(file)
    rmtree(temp_fasta_files)
    


def refseq_genbank_downloader(output_file_folder, ascp_key = None):
    print("Downloading protein genbank files")
    # Requirements
    if ascp_key == None:
        ascp_key = get_aspera_key()
    temp_gb_files = Path(output_file_folder) / "02.temp_genbank"
    Path(temp_gb_files).mkdir(parents=True, exist_ok=True)
    # Download compressed protein files
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.faa.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/viral/',
                    temp_gb_files])
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.faa.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/bacteria/',
                    temp_gb_files])
    subprocess.call(["ascp", '-QTr', '-d', '-l', '100M', '-E', '*wgs_mstr*',
                    '-E', '*rna*', '-E', '*genomic*', '-E', '*.faa.gz',
                    '-i', ascp_key, 'anonftp@ftp.ncbi.nlm.nih.gov:/refseq/release/archaea/',
                    temp_gb_files])
    # Get downloaded files
    viral_list = search_all_files(temp_gb_files / "viral")
    bacteria_list = search_all_files(temp_gb_files / "bacteria")
    archaea_list = search_all_files(temp_gb_files / "archaea")
    final_list = viral_list + bacteria_list + archaea_list
    return final_list

def get_aspera_key():
    path_to_ascp = which("ascp")
    install_folder = Path(path_to_ascp).parents[1]
    key = str(install_folder) + "/etc/asperaweb_id_dsa.openssh"
    return key

def search_all_files(directory):
    dirpath = Path(directory)
    assert(dirpath.is_dir())
    file_list = []
    for file in dirpath.iterdir():
        if file.is_file() and file.suffix == ".gz":
            file_list.append(file)
        else:
            continue
    return file_list


################################################################################
"""---2.0 Main Function---"""

def main():
    import argparse, sys
    # Setup parser for arguments.
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
            description='''This script downloads the fasta and genbank files that\n'''
            '''are needed to build the RefSeq annotation database. By default it\n'''
            '''downloads both but you can specify either\n'''
            '''Usage: ''' + sys.argv[0] + ''' -f [output_file folder]\n'''
            '''Global mandatory parameters: -f [output_file folder]\n'''
            '''Optional Database Parameters: See ''' + sys.argv[0] + ' -h')
    parser.add_argument('-f', '--folder', dest='folder', action='store', required=False,
                        help='Folder to store the fasta and genbank files')
    parser.add_argument('--proteins', dest='proteins', action='store_true', required=False,
                        help='Only download the protein fasta files.')
    parser.add_argument('--genbank', dest='genbank', action='store_true', required=False,
                        help='Only download the genbank files')
    parser.add_argument('--ascp', dest='ascp_key', action='store', required=False, default=None,
                        help='Path to Aspera Connect key')
    args = parser.parse_args()

    folder = args.folder
    proteins = args.proteins
    genbank = args.genbank
    ascp_key = args.ascp_key

    # ----------------------------
    if proteins == False and genbank == False:
        refseq_fasta_downloader(folder, ascp_key)
        refseq_genbank_downloader(folder, ascp_key)
    elif proteins == True:
        refseq_fasta_downloader(folder, ascp_key)
    elif genbank == True:
        refseq_genbank_downloader(folder, ascp_key)
    # ----------------------------

if __name__ == "__main__":
    main()