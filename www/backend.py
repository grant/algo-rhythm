from threading import Thread
import os, sys
import subprocess
from Queue import Queue, Empty


def start_process(cmd, stdouthandler, deathhandler):
        """
        Returns a (process, queue) pair, where the process represents the
        running process, the queue can be used to read stdout and stderr from the
        process.
        We assume that cmd is a list of strings, the first containing a program to
        run, and the remaining strings being the arguments to pass to the program
        """

        def block_on_output(out):
            for line in iter(out.readline, b''):
                print line
                stdouthandler(line)
            deathhandler()
            out.close()

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #queue = Queue()
        thread = Thread(target=block_on_output, args=(process.stdout,))
        thread.daemon = True  # thread dies with the program
        thread.start()

        #return process, queue


class Process:
  """
  A class to represent a process,
  it contains a Popen object reference, along
  with some other useful data related to
  the process's execution
  """
  def __init__(self, cmd, progressChangeHandler=None, terminationHandler=None):

    self.lines = []
    self.percentDone = 0
    self.isDead = False

    def handleStdout(line):
      #print "Got line! {}".format(line)
      self.lines.append(line)
      toks = line.split()
      if len(toks) == 2 and toks[0].strip() == 'PERCENT:':
        self.percentDone = int(toks[1])
        #print "Percent change detected!!! {}".format(self.percentDone)
        if self.percentDone > 100:
          raise ValueError("Percentage done unexpectedly greater than 100")
        if self.percentDone < 0:
          raise ValueError("Percentage done unexpectedly less than 0")
        if progressChangeHandler != None:
          progressChangeHandler(self.percentDone)

    def handleDeath():
      #print "DEATH DETECTED!!!"
      self.isDead = True
      if terminationHandler != None:
        terminationHandler()

    start_process(cmd, handleStdout, handleDeath)

  #read the process output, update the
  #lines and percent done fields appropriately
  #Note that between calls to this method, the
  #public state of the process can't change
  #EDIT: We're actually just going to have the
  #thread monitoring the processes make these
  #changes now, so this could probably be
  #removed
  def harvestProcessOut(self):
    pass
#    # read stdout and append to "output"
#    try:
#        stdout = self.q.get_nowait()  # or queue.get(timeout=.1)
#    except Empty:
#        # nothing to read
#        pass
#    else:
#        stdout = stdout.splitlines()
#        if len(stdout) == 0:
#          #I'm not even sure that this can happen
#          #but anyways do nothing
#          pass
#        else:
#          stdout[0] = self.lines[-1] + stdout[0]
#          del self.lines[-1]
#          #possibly a smarter way would be to start
#          #at the end going backwards and bail after
#          #the first update, but probably this is fine
#          for line in stdout:
#            print "Processing stdout line: {}".format(line)
#            toks = line.split()
#            if len(toks) == 2 and toks[0].strip() == 'PERCENT:':
#              self.percentDone = int(toks[1])
#              print "Percent change detected!!! {}".format(self.percentDone)
#              if self.percentDone > 100:
#                raise ValueError("Percentage done unexpectedly greater than 100")
#              if self.percentDone < 0:
#                raise ValueError("Percentage done unexpectedly less than 0")
#          self.lines = self.lines + stdout
#
#    if not self.p.poll() is None:
#      self.isDead = True

  def getAllOutput(self):
    return '\n'.join(self.lines)



class Backend:

    def __init__(self, upload_dir, config_dir, generated_song_dir, scriptroot):
        self.upload_dir = upload_dir + '/'
        self.config_dir = config_dir + '/'
        self.generated_song_dir = generated_song_dir + '/'
        self.scriptroot = scriptroot + '/'
        self.training_configs = {}
        self.generating_songs = {}

    def __cleanup(self):
        dead = set()
        for pname in self.training_configs.keys():
            proc = self.training_configs[pname]
            proc.harvestProcessOut()
            if proc.isDead:
              dead.add(pname)
        for pname in dead:
            # delete dead processes from hashmap
            del self.training_configs[pname]
        dead = set()
        for pname in self.generating_songs.keys():
            proc = self.generating_songs[pname]
            proc.harvestProcessOut()
            if proc.isDead:
              dead.add(pname)
        for pname in dead:
            # delete dead processes from hashmap
            del self.generating_songs[pname]

    def start_training_process(self, config, files, iterations, progressChangeHandler=None, terminationHandler=None, start_config=None):
        """
        Starts training a configuration.
        :param config: The config name
        :param files: The list of files to train on
        :param iterations: The number of iteration to train
        :param start_config: An optional start config
        """

        #Check that training files are all valid
        trainingFiles = os.listdir(self.upload_dir)
        for xmlfile in files:
            if xmlfile not in trainingFiles:
                raise ValueError("got {} as xml file argument, but this is not a training file".format(xmlfile))

        #Check start_config parameter is unused
        if start_config is not None:
            raise ValueError("Start config not supported yet")

        #Check config hasn't already been generated
        if config in os.listdir(self.config_dir):
            raise ValueError("target config name {} is already an existing config".format(config))

        #Check config isn't being generated
        if config in self.training_configs.keys():
            raise ValueError(
                "target config is already being generated".format(config))

        cmd = [
            'python',
            self.scriptroot + 'train.py',
            self.config_dir + config,
            ' '.join([self.upload_dir + xmlfile for xmlfile in files]),
            str(iterations)
        ]
        print ' '.join(cmd)

        self.training_configs[config] = Process(cmd, progressChangeHandler, terminationHandler)
        self.__cleanup()

    def start_music_generation_process(self, trained_config, song_name, song_length, progressChangeHandler=None, terminationHandler=None):
        """
        Starts generating the song.
        The process name is the unique combination of the config name and song name
        :param trained_config: The name of the config
        :param song_name: The name of the output song
        :param song_length: The number of seconds of the generated song
        """

        #check config file exists
        if not trained_config in os.listdir(self.config_dir):
            raise ValueError("Config to use does not exist")
        #check we're not already generating this song
        if song_name in self.generating_songs.keys():
            raise ValueError("song {} is already being generated".format(process_name))
        #check the song hasn't already been generated
        if song_name in os.listdir(self.generated_song_dir):
            raise ValueError("target music file {} is already a generated piece of music".format(song_name))

        cmd = [
            'python',
            self.scriptroot + 'genmusic.py',
            self.config_dir + trained_config,
            self.generated_song_dir + song_name, str(song_length)
        ]

        self.generating_songs[song_name] = Process(cmd, progressChangeHandler, terminationHandler)
        self.__cleanup()

    def get_status(self):
        """
        Gets the status of the system
        """

        #Will remove dead processes, also
        #update output/percent complete
        #for all process objects
        self.__cleanup()

        trainingConfigs = []
        for tcname in self.training_configs.keys():
          proc = self.training_configs[tcname]
          trainingConfigs.append({
            'name': tcname,
            'output': proc.getAllOutput(),
            'progress': proc.percentDone
          })

        generatingSongs = []
        for gsname in self.generating_songs.keys():
          proc = self.generating_songs[gsname]
          generatingSongs.append({
            'name': gsname,
            'output': proc.getAllOutput(),
            'progress': proc.percentDone
          })

        generatedSongs = []
        for song in os.listdir(self.generated_song_dir):
          #TODO: We can open the midi file and determine
          #the length by counting midi ticks, for generated
          #music it should be 8*55 ticks per seconds, we can
          #also cache these in a hashmap for faster lookup,
          #but this isn't implemented yet
          generatedSongs.append({
            'name': song,
            'length': '3:02'
          })

        return {
            'music_files': os.listdir(self.upload_dir),
            'training_configs': trainingConfigs,
            'trained_configs': os.listdir(self.config_dir),
            'generating_songs': generatingSongs,
            'generated_songs': generatedSongs,
        }


# for testing
if __name__ == '__main__':
    BACKEND_BASE = '../blog-code'
    UPLOAD_DIR = BACKEND_BASE + '/training_xml_web/'
    CONFIG_DIR = BACKEND_BASE + '/trained_configs/'
    GENERATED_SONG_DIR = BACKEND_BASE + '/generated_music/'
    SCRIPT_ROOT = BACKEND_BASE

    def handleProgress(pctDone):
      print "{}%".format(pctDone)

    def handleTerminationTraining():
      print "Training done!"

    def handleTerminationGeneration():
      print "Generation done!"

    backend = Backend(UPLOAD_DIR, CONFIG_DIR, GENERATED_SONG_DIR, SCRIPT_ROOT)
    #backend.start_training_process("config", ["Marcia_Turca.xml", "bach_bouree_eminor.xml", "Mozart_Cadenza_2.0.xml"], 3, handleProgress, handleTerminationTraining)
    # backend.start_music_generation_process('config', 'generated_out.mid', 100)

    backend.start_music_generation_process('params300.p', 'myexamplesong.mid', 15, handleProgress, handleTerminationGeneration)

    for line in sys.stdin:
      print line


