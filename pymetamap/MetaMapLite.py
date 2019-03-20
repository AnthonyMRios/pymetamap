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

import abc
from os.path import isabs


class MetaMapLite:
    """ Abstract base class for extracting concepts from text using
        MetaMapLite. To use this you will need to have downloaded the
        recent MetaMapLite software from NLM. metamap_filename should point
        to the binary you intend to use.

        Subclasses need to override the extract_concepts method.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, metamap_filename):
        self.metamap_filename = str(metamap_filename)
        assert isabs(self.metamap_filename), "metamap_filename: {0} should be an absolute path".format(self.metamap_filename)

    @abc.abstractmethod
    def extract_concepts(self, sentences=None, ids=None, filename=None):
        """ Extract concepts from a list of sentences using MetaMapLite. """
        return

    @staticmethod
    def get_instance(metamap_filename, backend='subprocess', **extra_args):
        extra_args.update(metamap_filename=metamap_filename)
        assert isabs(metamap_filename), "metamap_filename: {0} should be an absolute path".format(metamap_filename)

        if backend == 'subprocess':
            from .SubprocessBackendLite import SubprocessBackendLite
            return SubprocessBackendLite(**extra_args)

        raise ValueError("Unknown backend: %r (known backends: "
                         "'subprocess')" % backend)
