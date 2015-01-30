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

import jpype
from multiprocessing import Process, Queue, cpu_count
from Queue import Full as QueueFull
from Queue import Empty as QueueEmpty
from .MetaMap import MetaMap
from .Concept import Corpus

class JPypeBackend(MetaMap):
    def __init__(self, jar_folder_name):
        self.jar_folder_name = jar_folder_name
        MetaMap.__init__(self, None, version)

    def extract_concepts(self, sentences=None, ids=None,
                         composite_phrase=4, filename=None,
                         file_format='sldi', allow_acronym_variants=False,
                         word_sense_disambiguation=False, allow_large_n=False,
                         no_derivational_variants=False,
                         derivational_variants=False, ignore_word_order=False,
                         unique_acronym_variants=False,
                         prefer_multiple_concepts=False,
                         ignore_stop_phrases=False, compute_all_mappings=False,
                         num_procs=cpu_count(), batch_size=100):
         """ extract_concepts takes a list of sentences and ids(optional)
            then returns a list of Concept objects extracted via
            MetaMap.

            Supported Options:
                Composite Phrase -Q
                Word Sense Disambiguation -y
                allow large N -l
                No Derivational Variants -d
                Derivational Variants -D
                Ignore Word Order -i
                Allow Acronym Variants -a
                Unique Acronym Variants -u
                Prefer Multiple Concepts -Y
                Ignore Stop Phrases -K
                Compute All Mappings -b

            For information about the available options visit
            http://metamap.nlm.nih.gov/.

            Note: If an error is encountered the process will be closed
                  and whatever was processed, if anything, will be
                  returned along with the error found.
        """
        if allow_acronym_variants and unique_acronym_variants:
            raise ValueError("You can't use both allow_acronym_variants and "
                             "unique_acronym_variants.")
        if (sentences is not None and filename is not None) or \
                (sentences is None and filename is None) or \
                (sentences is not None):
            raise ValueError("You must read from a file when using "
                             "JPypeBackend.")
        if file_format not in ['sldi','sldiID']:
            raise ValueError("file_format must be either sldi or sldiID")

        sendq = Queue(batch_size)
        recvq = Queue()

        for rpt in xrange(num_procs):
            Process(target=worker, args=(sendq, recvq)).start()

        send_len = 0
        recv_len = 0
        try:
            in_file = open(filename, 'r')
        except IOError:
            print "Can't open file %s." % filename
            raise
        itr = iter(in_file)

        try:
            line = itr.next()
            if file_format == 'sldi':
                sentence = ['0000', line.rstrip()]
            else:
                sentence = line.rstrip().split('|')
            while True:
                try:
                    sendq.put(sentence, True, 0.1)
                    send_len += 1
                    line = itr.next()
                    if file_format == 'sldi':
                        sentence = ['0000', line.rstrip()]
                    else:
                        sentence = line.rstrip().split('|')
                except QueueFull:
                    while True:
                        try:
                            result = recvq.get(False)
                            recv_len += 1
                            yield result
                        except QueueEmpty:
                            break
        except StopIteration:
            pass
        
        in_file.close()

        while recv_len < send_len:
            result = recvq.get()
            recv_len += 1
            yield result

        for rpt in xrange(num_procs):
            sendq.put(None)
            
    def worker(recvq, sendq):
        jpype.startJVM(jpype.getDefaultJVMPath(),
                       '-ea',
                       '-Djava.class.path=' + self.java_classes + '/*',
                       *(extra_jvm_argsd or []))
        mm_package = jpype.JPackage('gov').nih.nlm.nls.metamap
        api = mm_package.MetaMapApiImpl()
        theOptions = jpype.java.util.ArrayList()
        theOptions.append('-Q')
        theOptions.append(str(composite_phrase))
        if word_sense_disambiguation:
            theOptions.append('-y')
        if allow_large_n:
            theOptions.append('-l')
        if no_derivational_variants:
            theOptions.append('-d')
        if derivational_variants:
            theOptions.append('-D')
        if ignore_word_order:
            theOptions.append('-i')
        if allow_acronym_variants:
            theOptions.append('-a')
        if unique_acronym_variants:
            theOptions.append('-u')
        if prefer_multiple_concepts:
            theOptions.append('-Y')
        if ignore_stop_phrases:
            theOptions.append('-K')
        if compute_all_mappings:
            theOptions.append('-b')
        api.setOptions(theOptions)

        for terms in iter(recvq.get, None):
            results = api.processCitationsFromString(terms)
            for result in results:
                for utterance in result.getUtteranceList():
                    for pcm in utterance.getPCMList():
                        for mapping in pcm.getMappingList():
                            for mapEv in mapping.getEvList():
                                score = mapEV.getScore()
                                cui = mapEv.getConceptId()
                                pref_name = mapEv.getPreferredName()
                                sem_types = mapEv.getSemanticTypes()
                                match_words = mapEv.getMatchedWords()
                                pos_info = mapEv.getPositionalInfo()
                                tree = 'a.b.c'
                                sendq.put('%s|MM|%s|%s|%s|%s|%s|TX|%s|%s' %
                                          (index, score, pref_name, cui,
                                           sem_types, match_words, pos_info,
                                           tree))
        jpype.shutdownJVM()
