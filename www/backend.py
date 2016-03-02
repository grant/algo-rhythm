from threading import Thread
import os
import subprocess
from Queue import Queue, Empty

UPLOAD_DIR = 'backend/music_uploads/'
CONFIG_DIR = 'backend/trained_configs/'
GENERATED_SONG_DIR = 'backend/generated_music/'


class Backend:
    def __init__(self):
        self.training_configs = {}
        self.generating_songs = {}

    def __check_process_triple(self, processTriple):
        """
        takes a (process, queue, buffer) triple, removes
        all stdout/stderr and places in buffer, returns
        (boolean, triple) pair, where boolean is true
        iff process is still alive, and triple is
        a replacement triple with an updated output
        buffer
        """

        process, queue, outputbuf = processTriple
        # read stdout and append to "output"
        try:
            line = queue.get_nowait()  # or queue.get(timeout=.1)
        except Empty:
            # nothing to read
            pass
        else:
            # print "Process output: " + line
            print line
            outputbuf = outputbuf + line
        # According to docs, this is the process died condition
        processDied = not process.poll() is None
        if processDied:
            print "Process died..."
        return not processDied, (process, queue, outputbuf)

    def __cleanup(self):
        dead = set()
        for trainingProcess in self.training_configs.keys():
            triple, targetConfig = self.training_configs[trainingProcess]
            stillAlive, triple = self.__check_process_triple(triple)
            self.training_configs[trainingProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(trainingProcess)
        for tp in dead:
            # delete dead processes from hashmap
            del self.training_configs[tp]
        dead = set()
        for genProcess in self.generating_songs.keys():
            triple, targetConfig = self.generating_songs[genProcess]
            stillAlive, triple = self.__check_process_triple(triple)
            self.generating_songs[genProcess] = (triple, targetConfig)
            if not stillAlive:
                dead.add(genProcess)
        for gp in dead:
            # delete dead processes from hashmap
            del self.generating_songs[gp]

    def get_music_files(self):
        self.__cleanup()
        return os.listdir(UPLOAD_DIR)

    def get_trained_configs(self):
        self.__cleanup()
        return os.listdir(CONFIG_DIR)

    def get_generated_songs(self):
        self.__cleanup()
        return os.listdir(GENERATED_SONG_DIR)

    def get_training_configs(self):
        self.__cleanup()
        return [{
                    'name': self.training_configs[config][1],
                    'output': self.get_config_output(config)
                } for config in self.training_configs.keys()]

    def get_generating_songs(self):
        self.__cleanup()
        return [{
                    'name': self.generating_songs[procname][1],
                    'output': self.get_generating_song_output(procname),
                } for procname in self.generating_songs.keys()]

    def __start_process(self, cmd):
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

    def start_training_process(self, config, files, iterations, start_config=None):
        """
        Starts training a configuration.
        :param config: The config name
        :param files: The list of files to train on
        :param iterations: The number of iteration to train
        :param start_config: An optional start config
        """
        self.__cleanup()
        trainingFiles = self.get_music_files()
        for xmlfile in files:
            if xmlfile not in trainingFiles:
                raise ValueError("got {} as xml file argument, but this is not a training file")
        if start_config is not None:
            raise ValueError("Start config not supported yet")
        if config in self.get_trained_configs():
            raise ValueError("target config name {} is already an existing config".format(config))
        if config in [name for name, output in self.get_training_configs()]:
            raise ValueError(
                "target config name {} is already in use by currently running process".format(config))

        cmd = [
            'python',
            'train_dummy.py',
            CONFIG_DIR + config,
            ' '.join([UPLOAD_DIR + xmlfile for xmlfile in files]),
            str(iterations)
        ]
        print ' '.join(cmd)

        self.training_configs[config] = (self.__start_process(cmd), config)

    def start_music_generation_process(self, trained_config, song_name, song_length):
        """
        Starts generating the song.
        The process name is the unique combination of the config name and song name
        :param trained_config: The name of the config
        :param song_name: The name of the output song
        :param song_length: The number of seconds of the generated song
        """
        self.__cleanup()
        process_name = trained_config + song_name
        if process_name in self.generating_songs.keys():
            raise ValueError("name {} is already a music generation process".format(process_name))
        if song_name in self.get_generated_songs():
            raise ValueError("target music file {} is already a generated piece of music".format(song_name))
        if song_name in [name for name, output in self.get_generating_songs()]:
            raise ValueError(
                "target music file  {} is already being generated by currently running process".format(song_name))

        cmd = [
            'python',
            'genmusic_dummy.py',
            CONFIG_DIR + trained_config,
            GENERATED_SONG_DIR + song_name,
            str(song_length)
        ]

        self.generating_songs[process_name] = (self.__start_process(cmd), song_name)

    def get_config_output(self, process_name):
        processTriple, targetConfig = self.training_configs[process_name]
        proc, q, outputbuf = processTriple
        return outputbuf

    def get_generating_song_output(self, process_name):
        processTriple, targetConfig = self.generating_songs[process_name]
        proc, q, outputbuf = processTriple
        return outputbuf

    def get_status(self):
        """
        Gets the status of the system
        """
        self.__cleanup()
        return {
            'music_files': self.get_music_files(),
            'training_configs': self.get_training_configs(),
            'trained_configs': self.get_trained_configs(),
            'generating_songs': self.get_generating_songs(),
            'generated_songs': self.get_generated_songs(),
        }


# for testing
if __name__ == '__main__':
    backend = Backend()
    backend.start_training_process("config", ["JSB_BWV1047_1.xml"], 100)
    # backend.start_music_generation_process('config', 'generated_out.mid', 100)
