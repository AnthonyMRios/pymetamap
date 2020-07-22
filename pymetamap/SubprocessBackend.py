# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys
import tempfile
from .MetaMap import MetaMap
from .Concept import Corpus


class SubprocessBackend(MetaMap):
    def __init__(self, metamap_filename, version=None):
        """ Interface to MetaMap using subprocess. This creates a
            command line call to a specified metamap process.
        """
        MetaMap.__init__(self, metamap_filename, version)

    def extract_concepts(self,
                         sentences=None,
                         ids=None,
                         composite_phrase=4,
                         filename=None,
                         file_format='sldi',
                         allow_acronym_variants=False,
                         word_sense_disambiguation=False,
                         allow_large_n=False,
                         strict_model=False,
                         relaxed_model=False,
                         allow_overmatches=False,
                         allow_concept_gaps=False,
                         term_processing=False,
                         no_derivational_variants=False,
                         derivational_variants=False,
                         ignore_word_order=False,
                         unique_acronym_variants=False,
                         prefer_multiple_concepts=False,
                         ignore_stop_phrases=False,
                         compute_all_mappings=False,
                         prune=False,
                         mm_data_version=False,
                         exclude_sources=[],
                         restrict_to_sources=[],
                         restrict_to_sts=[],
                         exclude_sts=[],
                         no_nums=[]):
        """ extract_concepts takes a list of sentences and ids(optional)
            then returns a list of Concept objects extracted via
            MetaMap.

            Supported Options:
                Composite Phrase -Q
                Word Sense Disambiguation -y
                use strict model -A
                use relaxed model -C
                allow large N -l
                allow overmatches -o
                allow concept gaps -g
                term processing -z
                No Derivational Variants -d
                All Derivational Variants -D
                Ignore Word Order -i
                Allow Acronym Variants -a
                Unique Acronym Variants -u
                Prefer Multiple Concepts -Y
                Ignore Stop Phrases -K
                Compute All Mappings -b
                MM Data Version -V
                Exclude Sources -e
                Restrict to Sources -R
                Restrict to Semantic Types -J
                Exclude Semantic Types -k
                Suppress Numerical Concepts --no_nums


            For information about the available options visit
            http://metamap.nlm.nih.gov/.

            Note: If an error is encountered the process will be closed
                  and whatever was processed, if anything, will be
                  returned along with the error found.
        """
        if allow_acronym_variants and unique_acronym_variants:
            raise ValueError("You can't use both allow_acronym_variants and unique_acronym_variants.")
        if (sentences is not None and filename is not None) or \
                (sentences is None and filename is None):
            raise ValueError("You must either pass a list of sentences OR a filename.")
        if file_format not in ['sldi', 'sldiID']:
            raise ValueError("file_format must be either sldi or sldiID")

        input_file = None
        output_file = None
        error = None

        try:
            command = list()
            command.append(self.metamap_filename)
            command.append('-N')
            command.append('-Q')
            command.append(str(composite_phrase))
            if mm_data_version is not False:
                if mm_data_version not in ['Base', 'USAbase', 'NLM']:
                    raise ValueError("mm_data_version must be Base, USAbase, or NLM.")
                command.append('-V')
                command.append(str(mm_data_version))
            if word_sense_disambiguation:
                command.append('-y')
            if strict_model:
                command.append('-A')
            if prune is not False:
                command.append('--prune')
                command.append(str(prune))
            if relaxed_model:
                command.append('-C')
            if allow_large_n:
                command.append('-l')
            if allow_overmatches:
                command.append('-o')
            if allow_concept_gaps:
                command.append('-g')
            if term_processing:
                command.append('-z')
            if no_derivational_variants:
                command.append('-d')
            if derivational_variants:
                command.append('-D')
            if ignore_word_order:
                command.append('-i')
            if allow_acronym_variants:
                command.append('-a')
            if unique_acronym_variants:
                command.append('-u')
            if prefer_multiple_concepts:
                command.append('-Y')
            if ignore_stop_phrases:
                command.append('-K')
            if compute_all_mappings:
                command.append('-b')
            if len(exclude_sources) > 0:
                command.append('-e')
                command.append(str(','.join(exclude_sources)))
            if len(restrict_to_sources) > 0:
                command.append('-R')
                command.append(str(','.join(restrict_to_sources)))
            if len(restrict_to_sts) > 0:
                command.append('-J')
                command.append(str(','.join(restrict_to_sts)))
            if len(exclude_sts) > 0:
                command.append('-k')
                command.append(str(','.join(exclude_sts)))
            if len(no_nums) > 0:
                command.append('--no_nums')
                command.append(str(','.join(no_nums)))
            if ids is not None or (file_format == 'sldiID' and sentences is None):
                command.append('--sldiID')
            else:
                command.append('--sldi')

            command.append('--silent')

            if sentences is not None:
                input_text = None
                if ids is not None:
                    for identifier, sentence in zip(ids, sentences):
                        if input_text is None:
                            input_text = '{0!r}|{1!r}\n'.format(identifier, sentence).encode('utf8')
                        else:
                            input_text += '{0!r}|{1!r}\n'.format(identifier, sentence).encode('utf8')
                else:
                    for sentence in sentences:
                        if input_text is None:
                            input_text = '{0!r}\n'.format(sentence).encode('utf8')
                        else:
                            input_text += '{0!r}\n'.format(sentence).encode('utf8')

                input_command = list()
                input_command.append('echo')
                input_command.append('-e')
                input_command.append(input_text)

                input_process = subprocess.Popen(input_command, stdout=subprocess.PIPE)
                metamap_process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=input_process.stdout)

                output, error = metamap_process.communicate()
                if sys.version_info[0] > 2:
                    if isinstance(output, bytes):
                        output = output.decode()

                # "Processing" sentences are returned as stderr. Hence success/failure of metamap_process needs to be
                #  checked by its returncode.
                if metamap_process.returncode == 0:
                    # Initial line(s) of output contains MetaMap command and MetaMap details.
                    # Even on using --silent option, MetaMap command is sent to stdout.
                    # Hence pre-processing is required to segregate these from MetaMap output in stdout.
                    prev_new_line = -1
                    while (prev_new_line + 1) < len(output):
                        next_new_line = output.find('\n', prev_new_line + 1)
                        if next_new_line < 0:
                            next_new_line = len(output)
                        # Check if the current line is in MMI output format i.e. fields separated by '|'
                        fields = output[prev_new_line + 1:next_new_line].split('|')
                        # https://metamap.nlm.nih.gov/Docs/MMI_Output_2016.pdf
                        #   This document explains the various fields in MMI output.
                        if len(fields) > 1 and fields[1] in ['MMI', 'AA', 'UA']:
                            break
                        else:
                            prev_new_line = next_new_line

                    output = output[prev_new_line + 1:]
                else:
                    error = "ERROR: MetaMap failed"
            else:
                input_file = open(filename, 'r')
                output_file = tempfile.NamedTemporaryFile(mode="r", delete=False)

                command.append(input_file.name)
                command.append(output_file.name)

                metamap_process = subprocess.Popen(command, stdout=subprocess.PIPE)
                while metamap_process.poll() is None:
                    stdout = str(metamap_process.stdout.readline())
                    if 'ERROR' in stdout:
                        metamap_process.terminate()
                        error = stdout.rstrip()
                output = str(output_file.read())
        finally:
            if sentences is not None:
                # os.remove(input_file.name)
                pass
            else:
                input_file.close()
                os.remove(output_file.name)

        concepts = Corpus.load(output.splitlines())
        return (concepts, error)
