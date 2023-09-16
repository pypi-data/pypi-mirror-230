#
# Copyright (c) 2023-present Didier Malenfant
#
# This file is part of pfDevTools.
#
# pfDevTools is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pfDevTools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with pfDevTools. If not,
# see <https://www.gnu.org/licenses/>.
#

import os
import sys
import shutil
import traceback
import pfDevTools

from typing import List
from pathlib import Path
from distutils.dir_util import copy_tree


# -- Classes
class OpenFPGACore:
    """A SCons action to build on openFPGA core."""

    @classmethod
    def _cloneRepo(cls, target, source, env):
        command_line: List[str] = []

        debug_on: bool = env.get('PF_DEBUG_ON', False)

        url = env.get('PF_CORE_TEMPLATE_REPO_URL', None)
        if url is not None:
            command_line.append(url)

        tag = env.get('PF_CORE_TEMPLATE_REPO_TAG', None)
        if tag is not None:
            command_line.append(f'tag={tag}')

        repo_folder = env['PF_CORE_TEMPLATE_FOLDER']
        command_line.append(repo_folder)

        if os.path.exists(repo_folder):
            pfDevTools.Utils.deleteFolder(repo_folder, force_delete=True)

        pfDevTools.Clone(command_line, debug_on=debug_on).run()

    @classmethod
    def _copyRepo(cls, target, source, env):
        src_folder = os.path.expanduser(env['PF_CORE_TEMPLATE_REPO_FOLDER'])
        dest_folder = env['PF_CORE_TEMPLATE_FOLDER']

        if not os.path.exists(src_folder) or not os.path.isdir(src_folder):
            raise RuntimeError(f'Cannot find \'{src_folder}\' to copy core tmeplate repo from.')

        print(f'Copying core template repo from \'{src_folder}\'.')

        if os.path.exists(dest_folder):
            pfDevTools.Utils.deleteFolder(dest_folder, force_delete=True)

        copy_tree(src_folder, dest_folder)

        git_folder = os.path.join(dest_folder, '.git')
        if os.path.exists(git_folder):
            pfDevTools.Utils.deleteFolder(git_folder, force_delete=True)

    @classmethod
    def _runDockerCommand(cls, image: str, command: str, build_folder: str = None, quiet: bool = True):
        pfDevTools.Utils.requireCommand('docker')

        if not OpenFPGACore._dockerIsRunning():
            raise RuntimeError('Docker engine does not seem to be running.\nCheck pre-requisites in the pf-dev-tools README or make sure quartus_sh is in your PATH to use native toolchain.')

        if not OpenFPGACore._dockerHasImage(image):
            print(f'Docker needs to download image \'{image}\'. This may take a while...')

        command_line: str = 'docker run --platform linux/amd64 -t --rm '

        if build_folder is not None:
            command_line += f'-v {build_folder}:/build '

        command_line += image + ' ' + command

        return pfDevTools.Utils.shellCommand(command_line, silent_mode=quiet, capture_output=True)

    @classmethod
    def _dockerIsRunning(cls) -> bool:
        try:
            pfDevTools.Utils.shellCommand('docker ps', silent_mode=True, capture_output=False)
        except RuntimeError:
            return False

        return True

    @classmethod
    def _dockerHasImage(cls, image: str) -> bool:
        result = pfDevTools.Utils.shellCommand('docker images', silent_mode=True, capture_output=True)

        image_info = image.split(':')
        if len(image_info) == 2:
            looking_for = f'{image_info[0]}   {image_info[1]}'
            for line in result:
                if line.startswith(looking_for):
                    return True

        return False

    @classmethod
    def _getNumberOfDockerCPUs(cls, image: str, quiet: bool = True) -> int:
        number_of_cpus: int = 1

        result = OpenFPGACore._runDockerCommand(image, 'grep --count ^processor /proc/cpuinfo', quiet=quiet)
        if len(result) == 1:
            num_cpus_found: int = int(result[0])
            if num_cpus_found != 0:
                number_of_cpus = num_cpus_found

        return number_of_cpus

    @classmethod
    def _updateQsfFile(cls, target, source, env):
        core_qsf_file = str(target)
        if not os.path.exists(core_qsf_file):
            if env.get('PF_CORE_TEMPLATE_REPO_FOLDER', None) is None:
                OpenFPGACore._cloneRepo(core_qsf_file, core_qsf_file, env)
            else:
                OpenFPGACore._copyRepo(core_qsf_file, core_qsf_file, env)

        core_fpga_folder = env['PF_CORE_FPGA_FOLDER']

        core_verilog_files = []
        for f in source:
            file_path = str(f)
            if file_path.endswith('.v') or file_path.endswith('.sv'):
                core_verilog_files.append(str(Path(str(f)).relative_to(core_fpga_folder)))

        arguments = [core_qsf_file]
        nb_of_cpus = env.get('PF_NB_OF_CPUS_TO_USE', None)
        if nb_of_cpus is not None:
            arguments.append(f'cpus={nb_of_cpus}')
        else:
            arguments.append('cpus=ALL')

        if env.get('PF_ENABLE_OPTIMIZATION', None) is not None:
            arguments.append('optim=perf')

        pfDevTools.Qfs(arguments + core_verilog_files).run()

    @classmethod
    def _installCore(cls, target, source, env):
        try:
            debug_on: bool = env.get('PF_DEBUG_ON', False)

            pfDevTools.Install([str(source[0])], debug_on=debug_on).run()
            pfDevTools.Eject([], debug_on=debug_on).run()
        except Exception as e:
            if debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error in installCore().')

            sys.exit(1)

    @classmethod
    def _copyFile(cls, target, source, env):
        source_file = str(source[0])
        target_file = str(target[0])
        print(f'Copying {source_file} to {target_file}.')
        parent_dest_dir = Path(target_file).parent
        os.makedirs(parent_dest_dir, exist_ok=True)
        shutil.copyfile(source_file, target_file)

    @classmethod
    def _searchSourceFiles(cls, env, path: str, dest_verilog_folder: str) -> List[str]:
        dest_verilog_files: List[str] = []

        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                if file.endswith('.sv') or file.endswith('.v') or file.endswith('.svh') or file.endswith('.vh'):
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_verilog_folder, Path(src_path).relative_to(path))
                    dest_verilog_files.append(dest_path)

                    env.Command(dest_path, src_path, OpenFPGACore._copyFile)

        return dest_verilog_files

    @classmethod
    def _addExtraFiles(cls, env, path: str, dest_verilog_folder: str, extra_files: List[str] = []) -> List[str]:
        extra_dest_files: List[str] = []

        for file in extra_files:
            dest_path = os.path.join(dest_verilog_folder, Path(file).relative_to(path))
            extra_dest_files.append(dest_path)

            env.Command(dest_path, file, OpenFPGACore._copyFile)

        return extra_dest_files

    @classmethod
    def _compileBitStream(cls, target, source, env):
        print('Compiling core bitstream...')

        try:
            core_qsf_file = env['PF_CORE_QSF_FILE']
            OpenFPGACore._updateQsfFile(core_qsf_file, source, env)

            command: str = 'quartus_sh --flow compile pf_core'
            folder: str = os.path.realpath(env['PF_CORE_FPGA_FOLDER'])

            docker_image_name = os.environ.get('PF_DOCKER_IMAGE_NAME', None)
            if docker_image_name is None:
                pfDevTools.Utils.shellCommand(command, from_dir=folder)
            else:
                OpenFPGACore._runDockerCommand(docker_image_name,
                                               command,
                                               build_folder=folder,
                                               quiet=False)
        except Exception as e:
            if env.get('PF_DEBUG_ON', False):
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error in compileBitStream().')

            sys.exit(1)

    @classmethod
    def _packageCore(cls, target, source, env):
        print('Packaging core...')

        debug_on: bool = env.get('PF_DEBUG_ON', False)

        try:
            pfDevTools.Package([env['PF_CORE_CONFIG_FILE'], env['PF_BUILD_FOLDER'], env['PF_CORE_BITSTREAM_OUTPUT_FOLDER']], debug_on=debug_on).run()
        except Exception as e:
            if debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error in packageCore().')

            sys.exit(1)


def build(env, config_file: str, extra_files: List[str] = []):
    debug_on: bool = env.get('PF_DEBUG_ON', False)

    if env.get('PF_SRC_FOLDER', None) is None:
        env.SetDefault(PF_SRC_FOLDER=Path(config_file).parent)

    src_folder: str = env['PF_SRC_FOLDER']

    env.SetDefault(PF_BUILD_FOLDER='_build')
    build_folder: str = env['PF_BUILD_FOLDER']

    env.Replace(PF_CORE_CONFIG_FILE=config_file)

    core_template_folder: str = os.path.join(build_folder, '_core_template_repo')
    env.Replace(PF_CORE_TEMPLATE_FOLDER=core_template_folder)

    core_fpga_folder: str = os.path.join(core_template_folder, 'src', 'fpga')
    env.Replace(PF_CORE_FPGA_FOLDER=core_fpga_folder)

    core_qsf_file = os.path.join(core_fpga_folder, 'pf_core.qsf')
    env.Replace(PF_CORE_QSF_FILE=core_qsf_file)

    core_bitstream_output_folder = os.path.join(core_fpga_folder, 'output_files')
    env.Replace(PF_CORE_BITSTREAM_OUTPUT_FOLDER=core_bitstream_output_folder)

    packaging_process: pfDevTools.Package = pfDevTools.Package([config_file, build_folder, core_bitstream_output_folder], debug_on=debug_on)
    packaged_core = os.path.join(build_folder, packaging_process.packagedFilename())

    if not env.get('PF_SKIP_BUILD', False):
        if env.get('PF_CORE_TEMPLATE_REPO_FOLDER', None) is None:
            env.Command(core_template_folder, '', OpenFPGACore._cloneRepo)
        else:
            env.Command(core_template_folder, '', OpenFPGACore._copyRepo)

        dest_verilog_folder: str = os.path.join(core_fpga_folder, 'core')
        dest_verilog_files: List[str] = OpenFPGACore._searchSourceFiles(env, src_folder, dest_verilog_folder)
        extra_dest_files: List[str] = OpenFPGACore._addExtraFiles(env, src_folder, dest_verilog_folder, extra_files)

        config = pfDevTools.CoreConfig(config_file)
        core_output_bitstream_files: List[str] = []
        for core_id in config.coresList():
            core_output_bitstream_file = os.path.join(core_bitstream_output_folder, config.coreSourceFile(core_id))
            core_output_bitstream_files.append(core_output_bitstream_file)
            env.Precious(core_output_bitstream_file)

        env.Command(core_output_bitstream_files, dest_verilog_files + extra_dest_files, OpenFPGACore._compileBitStream)
        env.Command(packaged_core, packaging_process.dependencies(), OpenFPGACore._packageCore)

    env.Default(packaged_core)
    env.Clean(packaged_core, build_folder)

    install_command = env.Command(None, packaged_core, OpenFPGACore._installCore)
    env.Alias('install', install_command)

    return packaged_core
