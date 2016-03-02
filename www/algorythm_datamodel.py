from threading import Thread
import os
import subprocess
from Queue import Queue, Empty

class AlgorythmDatamodel:
    # some constants:
    UPLOAD_DIR = 'backend/music_uploads/'
    CONFIG_DIR = 'backend/trained_configs/'
    GENERATED_SONG_DIR = 'backend/generated_music/'

    def __init__(self):
        self.trainingProcesses = {}
        self.musicGenProcesses = {}

    # takes a (process, queue, buffer) triple, removes
    # all stdout/stderr and places in buffer, returns
    # (boolean, triple) pair, where boolean is true
    # iff process is still alive, and triple is
    # a replacement triple with an updated output
    # buffer
    def __checkProcessTriple(self, processTriple):
        proc, q, outputbuf = processTriple
        # read stdout and append to "output"
        try:
            line = q.get_nowait()  # or q.get(timeout=.1)
        except Empty:
            # nothing to read
            pass
        else:
            # print "Process output: " + line
            print line
            outputbuf = outputbuf + line
        # According to docs, this is the process died condition
        processDied = not proc.poll() is None
        if processDied:
            print "Process died..."
        return not processDied, (proc, q, outputbuf)

    def __cleanup(self):
        dead = set()
        for trainingProcess in self.trainingProcesses.keys():
            triple, targetConfig = self.trainingProcesses[trainingProcess]
            stillAlive, triple = self.__checkProcessTriple(triple)
            self.trainingProcesses[trainingProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(trainingProcess)
        for tp in dead:
            # delete dead processes from hashmap
            del self.trainingProcesses[tp]
        dead = set()
        for genProcess in self.musicGenProcesses.keys():
            triple, targetConfig = self.musicGenProcesses[genProcess]
            stillAlive, triple = self.__checkProcessTriple(triple)
            self.musicGenProcesses[genProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(genProcess)
        for gp in dead:
            # delete dead processes from hashmap
            del self.musicGenProcesses[gp]

    def __getFilesInDir(self, thedir):
        self.__cleanup()
        retlist = []
        for f in os.listdir(thedir):
            retlist.append(f)
        return retlist

    def getTrainingFiles(self):
        self.__cleanup()
        return self.__getFilesInDir(AlgorythmDatamodel.UPLOAD_DIR)

    def getCompletedTrainedConfigs(self):
        self.__cleanup()
        return self.__getFilesInDir(AlgorythmDatamodel.CONFIG_DIR)

    def getGeneratedMusic(self):
        self.__cleanup()
        return self.__getFilesInDir(AlgorythmDatamodel.GENERATED_SONG_DIR)

    def getTrainedConfigsInProgress(self):
        self.__cleanup()
        ret = []
        for procname in self.trainingProcesses.keys():
            triple, targetConfig = self.trainingProcesses[procname]
            ret.append(targetconfig)
        return ret

    def getTrainingProcessNames(self):
        self.__cleanup()
        return self.trainingProcesses.keys()

    def getMusicBeingGenerated(self):
        self.__cleanup()
        ret = []
        for procname in self.musicGenProcesses.keys():
            triple, targetMusicFile = self.trainingProcesses[procname]
            ret.append(targetMusicFile)
        return ret

    # Returns a (process, queue, string) triple, where the process represents the
    # running process, the queue can be used to read stdout and stderr from the
    # process, and the string is the empty string, for use later to buffer read
    # output
    # We assume that cmd is a list of strings, the first containing a program to
    # run, and the remaining strings being the arguments to pass to the program
    def __startProcessFromCommand(self, cmd):
        def enqueue_output(out, queue):
            for line in iter(out.readline, b''):
                queue.put(line)
            out.close()

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        q = Queue()
        t = Thread(target=enqueue_output, args=(p.stdout, q))
        t.daemon = True  # thread dies with the program
        t.start()

        return (p, q, '')

    def startTrainingProcess(self, newProcessName, targetConfig, xmlFileList, numIterations, startConfig=None):
        self.__cleanup()
        trainingFiles = self.getTrainingFiles()
        for xmlfile in xmlFileList:
            if not xmlfile in trainingFiles:
                raise ValueError("got {} as xml file argument, but this is not a training file")
        if startConfig != None:
            raise ValueError("Start config not supported yet")
        if newProcessName == None:
            raise ValueError("got None as process name")
        if newProcessName in self.trainingProcesses.keys():
            raise ValueError("name {} is already a training process".format(newProcessName))
        if targetConfig in self.getCompletedTrainedConfigs():
            raise ValueError("target config name {} is already an existing config".format(targetConfig))
        if targetConfig in self.getTrainedConfigsInProgress():
            raise ValueError(
                "target config name {} is already in use by currently running process".format(targetConfig))

        cmd = ['python', 'train_dummy.py', AlgorythmDatamodel.CONFIG_DIR + targetConfig,
               ' '.join([AlgorythmDatamodel.UPLOAD_DIR + xmlfile for xmlfile in xmlFileList]), str(numIterations)]
        processTriple = self.__startProcessFromCommand(cmd)

        self.trainingProcesses[newProcessName] = (processTriple, targetConfig)

    def startMusicGenerationProcess(self, newProcessName, trainedConfig, outputSongName, numSecondsToGenerate):
        self.__cleanup()
        if newProcessName == None:
            raise ValueError("got None as process name")
        if newProcessName in self.musicGenProcesses.keys():
            raise ValueError("name {} is already a music generation process".format(newProcessName))
        if outputSongName in self.getGeneratedMusic():
            raise ValueError("target music file {} is already a generated piece of music".format(outputSongName))
        if outputSongName in self.getMusicBeingGenerated():
            raise ValueError(
                "target music file  {} is already being generated by currently running process".format(outputSongName))

        cmd = ['python', 'genmusic_dummy.py', AlgorythmDatamodel.CONFIG_DIR + trainedConfig,
               AlgorythmDatamodel.GENERATED_SONG_DIR + outputSongName, str(numSecondsToGenerate)]
        processTriple = self.__startProcessFromCommand(cmd)

        self.musicGenProcesses[newProcessName] = (processTriple, outputSongName)

    def getOutputForTrainingProcess(self, processName):
        self.__cleanup()
        if not processName in self.trainingProcesses:
            return "(terminated)"
        else:
            processTriple, targetConfig = self.trainingProcesses[processName]
            proc, q, outputbuf = processTriple
            return outputbuf

    # Gets the status of the system
    def getStatus(self):
        print self.getTrainingFiles()
        print self.getCompletedTrainedConfigs()
        print self.getGeneratedMusic()
        print self.getTrainedConfigsInProgress()
        print self.getTrainingProcessNames()
        print self.getMusicBeingGenerated()
        return {}

    def getMusicGenProcessNames(self, processName):
        return self.musicGenProcesses.keys()

    def getOutputForMusicGenProcess(self, processName):
        self.__cleanup()
        if not processName in self.musicGenProcesses:
            return "(terminated)"
        else:
            processTriple, targetConfig = self.musicGenProcesses[processName]
            proc, q, outputbuf = processTriple
            return outputbuf


# for testing
if __name__ == '__main__':
    adm = AlgorythmDatamodel()
    adm.startMusicGenerationProcess('genproc', 'config', 'generated_out.mid', 100)
