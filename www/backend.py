from threading import Thread
import os
import subprocess
from Queue import Queue, Empty

UPLOAD_DIR = 'backend/music_uploads/'
CONFIG_DIR = 'backend/trained_configs/'
GENERATED_SONG_DIR = 'backend/generated_music/'


class Backend:
    # some constants:

    def __init__(self):
        self.trainingProcesses = {}
        self.musicGenProcesses = {}

    def __check_process_triple(self, processTriple):
        """
        takes a (process, queue, buffer) triple, removes
        all stdout/stderr and places in buffer, returns
        (boolean, triple) pair, where boolean is true
        iff process is still alive, and triple is
        a replacement triple with an updated output
        buffer
        """

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
            stillAlive, triple = self.__check_process_triple(triple)
            self.trainingProcesses[trainingProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(trainingProcess)
        for tp in dead:
            # delete dead processes from hashmap
            del self.trainingProcesses[tp]
        dead = set()
        for genProcess in self.musicGenProcesses.keys():
            triple, targetConfig = self.musicGenProcesses[genProcess]
            stillAlive, triple = self.__check_process_triple(triple)
            self.musicGenProcesses[genProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(genProcess)
        for gp in dead:
            # delete dead processes from hashmap
            del self.musicGenProcesses[gp]

    def getTrainingFiles(self):
        self.__cleanup()
        return os.listdir(UPLOAD_DIR)

    def getCompletedTrainedConfigs(self):
        self.__cleanup()
        return os.listdir(CONFIG_DIR)

    def getGeneratedMusic(self):
        self.__cleanup()
        return os.listdir(GENERATED_SONG_DIR)

    def getTrainedConfigsInProgress(self):
        self.__cleanup()
        ret = []
        for procname in self.trainingProcesses.keys():
            triple, targetConfig = self.trainingProcesses[procname]
            ret.append(targetConfig)
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

    def __start_process_from_command(self, cmd):
        """
        Returns a (process, queue, string) triple, where the process represents the
        running process, the queue can be used to read stdout and stderr from the
        process, and the string is the empty string, for use later to buffer read
        output
        We assume that cmd is a list of strings, the first containing a program to
        run, and the remaining strings being the arguments to pass to the program
        """

        def enqueue_output(out, queue):
            for line in iter(out.readline, b''):
                queue.put(line)
            out.close()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        queue = Queue()
        thread = Thread(target=enqueue_output, args=(process.stdout, queue))
        thread.daemon = True  # thread dies with the program
        thread.start()

        return process, queue, ''

    def start_training_process(self, process_name, config, file_names, iterations, start_config=None):
        self.__cleanup()
        trainingFiles = self.getTrainingFiles()
        for xmlfile in file_names:
            if not xmlfile in trainingFiles:
                raise ValueError("got {} as xml file argument, but this is not a training file")
        if start_config != None:
            raise ValueError("Start config not supported yet")
        if process_name == None:
            raise ValueError("got None as process name")
        if process_name in self.trainingProcesses.keys():
            raise ValueError("name {} is already a training process".format(process_name))
        if config in self.getCompletedTrainedConfigs():
            raise ValueError("target config name {} is already an existing config".format(config))
        if config in self.getTrainedConfigsInProgress():
            raise ValueError(
                "target config name {} is already in use by currently running process".format(config))

        cmd = ['python', 'train_dummy.py', CONFIG_DIR + config,
               ' '.join([UPLOAD_DIR + xmlfile for xmlfile in file_names]), str(iterations)]
        processTriple = self.__start_process_from_command(cmd)

        self.trainingProcesses[process_name] = (processTriple, config)

    def start_music_generation_process(self, process_name, trained_config, output_song_name, song_length):
        """
        Starts generating the song.
        :param process_name: The name of the process
        :param trained_config: The name of the config
        :param output_song_name: The name of the output song
        :param song_length: The number of seconds of the generated song
        """
        self.__cleanup()
        if process_name == None:
            raise ValueError("got None as process name")
        if process_name in self.musicGenProcesses.keys():
            raise ValueError("name {} is already a music generation process".format(process_name))
        if output_song_name in self.getGeneratedMusic():
            raise ValueError("target music file {} is already a generated piece of music".format(output_song_name))
        if output_song_name in self.getMusicBeingGenerated():
            raise ValueError(
                "target music file  {} is already being generated by currently running process".format(
                    output_song_name))

        cmd = [
            'python',
            'genmusic_dummy.py',
            CONFIG_DIR + trained_config,
            GENERATED_SONG_DIR + output_song_name, str(song_length)
        ]
        processTriple = self.__start_process_from_command(cmd)

        self.musicGenProcesses[process_name] = (processTriple, output_song_name)

    def get_output_for_training_process(self, process_name):
        self.__cleanup()
        if process_name not in self.trainingProcesses:
            return "(terminated)"
        else:
            processTriple, targetConfig = self.trainingProcesses[process_name]
            proc, q, outputbuf = processTriple
            return outputbuf

    def get_status(self):
        """
        Gets the status of the system
        """
        print self.getTrainingFiles()
        print self.getCompletedTrainedConfigs()
        print self.getGeneratedMusic()
        print self.getTrainedConfigsInProgress()
        print self.getTrainingProcessNames()
        print self.getMusicBeingGenerated()
        return {}

    def get_music_gen_process_names(self, process_name):
        return self.musicGenProcesses.keys()

    def get_output_for_music_gen_process(self, process_name):
        self.__cleanup()
        if process_name not in self.musicGenProcesses:
            return "(terminated)"
        else:
            processTriple, targetConfig = self.musicGenProcesses[process_name]
            proc, q, outputbuf = processTriple
            return outputbuf


# for testing
if __name__ == '__main__':
    adm = Backend()
    adm.start_music_generation_process('genproc', 'config', 'generated_out.mid', 100)
