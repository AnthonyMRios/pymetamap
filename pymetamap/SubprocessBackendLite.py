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
import tempfile
from .MetaMapLite import MetaMapLite
from .ConceptLite import CorpusLite


class SubprocessBackendLite(MetaMapLite):
    def __init__(self, metamap_home):
        """ Interface to MetaMap using subprocess. This creates a
            command line call to a specified metamap process.
        """
        MetaMapLite.__init__(self, metamap_home=metamap_home)

    def extract_concepts(self, sentences=None, ids=None, filename=None,
                         restrict_to_sts=None, restrict_to_sources=None):
        """ extract_concepts takes a list of sentences and ids(optional)
            then returns a list of Concept objects extracted via
            MetaMapLite.

            Supported Options:
                Restrict to Semantic Types --restrict_to_sts
                Restrict to Sources --restrict_to_sources

            For information about the available options visit
            http://metamap.nlm.nih.gov/.

            Note: If an error is encountered the process will be closed
                  and whatever was processed, if anything, will be
                  returned along with the error found.
        """
        if (sentences is not None and filename is not None) or \
                (sentences is None and filename is None):
            raise ValueError("You must either pass a list of sentences "
                             "OR a filename.")

        input_file = None
        if sentences is not None:
            input_file = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix='.mmi')
        else:
            input_file = open(filename, 'r')

        # Unlike MetaMap, MetaMapLite does not take an output filename as a parameter.
        # It creates a new output file at same location as "input_file" with the default file extension ".mmi".
        # output_file = tempfile.NamedTemporaryFile(mode="r", delete=False)
        output_file_name = None
        error = None
        try:
            if sentences is not None:
                if ids is not None:
                    for identifier, sentence in zip(ids, sentences):
                        input_file.write('{0!r}|{1}\n'.format(identifier, sentence).encode('utf8'))
                else:
                    for sentence in sentences:
                        input_file.write('{0!r}\n'.format(sentence).encode('utf8'))
                input_file.flush()
                input_file.close()

            command = ["bash", os.path.join(self.metamap_home, "metamaplite.sh")]
            if restrict_to_sts:
                if isinstance(restrict_to_sts, str):
                    restrict_to_sts = [restrict_to_sts]
                if len(restrict_to_sts) > 0:
                    command.append('--restrict_to_sts={}'.format(str(','.join(restrict_to_sts))))
                    #command.append(str(','.join(restrict_to_sts)))

            if restrict_to_sources:
                if isinstance(restrict_to_sources, str):
                    restrict_to_sources = [restrict_to_sources]
                if len(restrict_to_sources) > 0:
                    command.append('--restrict_to_sources')
                    command.append(str(','.join(restrict_to_sources)))

            if ids is not None:
                command.append('--inputformat=sldiwi')

            command.append(input_file.name)
            command.append('--overwrite')
            #command.append('--indexdir={}data/ivf/2020AA/USAbase'.format(self.metamap_home))
            #command.append('--specialtermsfile={}data/specialterms.txt'.format(self.metamap_home))
            # command.append(output_file.name)

            output_file_name, file_extension = os.path.splitext(input_file.name)
            output_file_name += "." + "mmi"

            output_file_name, file_extension = os.path.splitext(input_file.name)
            output_file_name += "." + "mmi"

            # output = str(output_file.read())
            metamap_process = subprocess.Popen(command, stdout=subprocess.PIPE)
            while metamap_process.poll() is None:
                stdout = str(metamap_process.stdout.readline())
                if 'ERROR' in stdout:
                    metamap_process.terminate()
                    error = stdout.rstrip()

            # print("input file name: {0}".format(input_file.name))
            output_file_name, file_extension = os.path.splitext(input_file.name)
            output_file_name += "." + "mmi"
            # print("output_file_name: {0}".format(output_file_name))
            with open(output_file_name) as fd:
                output = fd.read()
            # output = str(output_file.read())
            # print("output: {0}".format(output))
        except:
            pass
        concepts = CorpusLite.load(output.splitlines())
        return concepts, error
#finally:
#    if sentences is not None:
#        os.remove(input_file.name)
#    else:
#        input_file.close()
#    # os.remove(output_file.name)
#    #os.remove(output_file_name)
