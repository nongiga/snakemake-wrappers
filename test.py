import subprocess
import os
import tempfile
import shutil

def run(wrapper, cmd):
    origdir = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        dst = os.path.join(d, "master", wrapper)
        os.makedirs(dst, exist_ok=True)
        copy = lambda src: shutil.copy(os.path.join(wrapper, src), dst)
        copy("wrapper.py")
        copy("environment.yaml")
        testdir = os.path.join(wrapper, "test")
        os.chdir(testdir)
        if os.path.exists(".snakemake"):
            shutil.rmtree(".snakemake")
        cmd = cmd + ["--wrapper-prefix", "file://{}/".format(d)]
        subprocess.check_call(["snakemake", "--version"])
        try:
            subprocess.check_call(cmd)
        finally:
            os.chdir(origdir)
            for d, _, files in os.walk(os.path.join(testdir, "logs")):
                for f in files:
                    path = os.path.join(d, f)
                    with open(path) as f:
                        msg = "###### Logfile: " + path + " ######"
                        print(msg, "\n")
                        print(f.read())
                        print("#" * len(msg))


def test_bowtie2_align():
    run("bio/bowtie2/align",
        ["snakemake", "mapped/a.bam", "--use-conda", "-F"])


def test_bwa_mem():
    run("bio/bwa/mem",
        ["snakemake", "mapped/a.bam", "--use-conda", "-F"])


def test_freebayes():
    run("bio/freebayes",
        ["snakemake", "calls/a.vcf", "--use-conda", "-F"])


def test_picard_collectalignmentsummarymetrics():
    run("bio/picard/collectalignmentsummarymetrics",
        ["snakemake", "stats/a.summary.txt", "--use-conda", "-F"])


def test_picard_collectinsertsizemetrics():
    run("bio/picard/collectinsertsizemetrics",
        ["snakemake", "stats/a.isize.txt", "--use-conda", "-F"])


def test_pindel_call():
    run("bio/pindel/call",
        ["snakemake", "pindel/all_D", "--use-conda", "-F"])


def test_pindel_pindel2vcf():
    run("bio/pindel/pindel2vcf",
        ["snakemake", "pindel/all_D.vcf", "--use-conda", "-F"])


def test_star_align():
    # generate index on the fly, because it is huge regardless of genome size
    os.makedirs("bio/star/align/test/index", exist_ok=True)
    try:
        subprocess.check_call("conda env create "
                              "--file bio/star/align/environment.yaml "
                              "-p star-env",
                              shell=True,
                              executable="/bin/bash")
        subprocess.check_call("source activate star-env; STAR --genomeDir "
                              "bio/star/align/test/index "
                              "--genomeFastaFiles bio/star/align/test/genome.fasta "
                              "--runMode genomeGenerate",
                              shell=True,
                              executable="/bin/bash")
    finally:
        shutil.rmtree("star-env", ignore_errors=True)

    run("bio/star/align",
        ["snakemake", "star/a/Aligned.out.bam", "--use-conda", "-F"])


def test_trimmomatic_pe():
    run("bio/trimmomatic/pe",
        ["snakemake", "trimmed/a.1.fastq.gz", "--use-conda", "-F"])


def test_trimmomatic_se():
    run("bio/trimmomatic/se",
        ["snakemake", "trimmed/a.fastq.gz", "--use-conda", "-F"])