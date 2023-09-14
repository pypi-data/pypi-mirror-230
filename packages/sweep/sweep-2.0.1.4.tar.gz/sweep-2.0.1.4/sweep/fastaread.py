#!/usr/bin/python3
# -*- coding: utf-8 -*-

from Bio import SeqIO


def fastaread(fastaname):
    """
    Read sequences from a FASTA file.

    Args:
        fastaname (str): Path to the FASTA file.

    Returns:
        list: List of SeqRecord objects containing the sequences.
    """

    records = list(SeqIO.parse(fastaname, "fasta"))
    return records
