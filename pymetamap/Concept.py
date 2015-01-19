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

from collections import namedtuple

FIELD_NAMES = ('index', 'mm', 'score', 'preferred_name', 'cui', 'semtypes',
               'trigger', 'location', 'pos_info', 'tree_codes')

class Concept(namedtuple('Concept', FIELD_NAMES)):
    def __repr__(self):
        items = [(field, getattr(self, field, None)) for field in FIELD_NAMES]
        fields = ['%s=%r' % (k, v) for k, v in items if v is not None]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(fields))

    def as_mmi(self):
        return '|'.join([get(field) for field in FIELD_NAMES])

    @classmethod
    def from_mmi(this_class, line):
         fields = line.split('|')
         return this_class(**dict(zip(FIELD_NAMES, fields)))


class Corpus(list):
    @classmethod
    def load(this_class, stream):
        stream = iter(stream)
        corpus = this_class()
        for line in stream:
            corpus.append(Concept.from_mmi(line))

        return corpus

