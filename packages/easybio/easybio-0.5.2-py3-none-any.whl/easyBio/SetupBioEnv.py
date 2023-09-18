# -*- coding: utf-8 -*-
# Author: Lei
# Date: 2023-07-21
# Description:
import argparse
import subprocess
import os
from .installConda import InstallConda

class SetupBioEnv:
    def __init__(self, env_name):
        self.env_name = env_name
        self.conda_path = self.get_conda_path()

    def get_conda_path(self):
        ic = InstallConda()
        if not ic.is_conda_installed():
            print("Conda not found. Installing...")
            ic.remove_conda_directory()
            print(ic.install_anaconda())
        return ic.get_conda_path()

    def is_environment_exist(self, env_name):
        env_path = os.path.join(os.path.dirname(
            self.conda_path), "envs", env_name)
        return os.path.exists(env_path)

    def setup_conda_environment(self, env_name, packages, channels):
        # If the environment already exists, ask the user whether to remove it
        if self.is_environment_exist(env_name):
            response = input(
                f"环境 {env_name} 已存在，你希望删除它吗？(y/n): | The environment {env_name} already exists. Do you want to remove it? (y/n): ")
            if response.lower() == 'y':
                print(
                    f"正在删除环境 {env_name}... | Removing the environment {env_name}...")
                subprocess.run(
                    [self.conda_path, "env", "remove", "-n", env_name])
                print(
                    f"环境 {env_name} 已被删除。 | The environment {env_name} has been removed.")
            else:
                print("环境未被删除，退出... | Environment was not removed. Exiting...")
                return

        # Define the commands to set up channels
        commands = [[self.conda_path, "config", "--add", "channels", channel]
                    for channel in channels]

        # Add other configuration commands
        commands.extend([
            [self.conda_path, "config", "--set", "show_channel_urls", "yes"],
            [self.conda_path, "create", "-n", env_name, "-y", "python=3.10"]
        ])

        # Add commands to install packages
        for package in packages:
            commands.append([self.conda_path, "install", "-n", env_name,
                            "-y", "-c", package["channel"], package["name"]])

        # Add command to install easyBio using pip
        commands.append([self.conda_path, "run", "-n",
                        env_name, "pip", "install", "easyBio"])

        # Run each command
        for command in commands:
            subprocess.run(command)
            
# Define the packages to be installed
packages = [
    {"name": "aspera-cli", "channel": "hcc"},
    {"name": "sra-tools", "channel": "bioconda"},
    {"name": "cutadapt", "channel": "bioconda"},
    {"name": "fastqc", "channel": "bioconda"},
    {"name": "trim-galore", "channel": "bioconda"},
    {"name": "multiqc", "channel": "bioconda"},
    {"name": "hisat2", "channel": "bioconda"},
    {"name": "parallel-fastq-dump", "channel": "bioconda"},
    {"name": "subread", "channel": "bioconda"},
    {"name": "salmon", "channel": "bioconda"},
    {"name": "samtools", "channel": "bioconda"}
]

# Define the channels to be added
mirrorsChannels = [
    "https://mirrors.bfsu.edu.cn/anaconda/cloud/bioconda/",
    "https://mirrors.bfsu.edu.cn/anaconda/cloud/conda-forge/",
    "https://mirrors.bfsu.edu.cn/anaconda/pkgs/free/",
    "https://mirrors.bfsu.edu.cn/anaconda/pkgs/main/"
]

def main():
    parser = argparse.ArgumentParser(description="Setup Conda environment.")
    parser.add_argument('-n', '--env_name', default="easyBio", type=str,
                        help='The name of the conda environment to be set up.')
    args = parser.parse_args()
    env_name = args.env_name

    seb = SetupBioEnv(env_name)
    seb.setup_conda_environment(env_name, packages, mirrorsChannels)


if __name__ == '__main__':
    main()
