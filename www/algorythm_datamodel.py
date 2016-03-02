import thread, threading, sys, time, os, subprocess
from threading  import Thread
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


class AlgorythmDatamodel:

  def __init__(self):
    self.trainingProcesses = {}
    self.musicGenProcesses = {}

  def __cleanup(self):
    torem = set()
    for trainingProcess in self.trainingProcesses.keys():
      proc, targetconfig, q, output = self.trainingProcesses[trainingProcess]
      if not proc.poll() is None:
        print "Detected process {} died.".format(trainingProcess)
        torem.add(trainingProcess)

        ##DEBUG##
        print "Reading process output"
        try:  line = q.get_nowait() # or q.get(timeout=.1)
        except Empty:
          #nothing to read
          pass
        else:
          print "Output from dead process: " + line


      else:
        #read stdout and append to "output"
        try:  line = q.get_nowait() # or q.get(timeout=.1)
        except Empty:
          #nothing to read
          pass
        else:
          print "Process output: " + line
          output = output + line
        self.trainingProcesses[trainingProcess] = (proc, targetconfig, q, output)
    for tp in torem:
      pass
      #del self.trainingProcesses[tp]

  def __getFilesInDir(self, thedir):
    self.__cleanup()
    retlist = []
    for f in os.listdir('backend/' + thedir):
      retlist.append(f)
    return retlist

  def getTrainingFiles(self):
    self.__cleanup()
    return self.__getFilesInDir('music_uploads/')

  def getCompletedTrainedConfigs(self):
    self.__cleanup()
    return self.__getFilesInDir('trained_configs/')

  def getTrainedConfigsInProgress(self):
    self.__cleanup()
    ret = []
    for procname in self.trainingProcesses.keys():
      popenobj, targetconfig, q, output = self.trainingProcesses[procname]
      ret.append(targetconfig)
    return ret

  def getTrainingProcessNames(self):
    self.__cleanup()
    return self.trainingProcesses.keys()

  def startTrainingProcess(self, newProcessName, targetConfig, xmlFileList, startConfig = None):
    self.__cleanup()
    if startConfig != None:
      raise ValueError("Start config not supported yet")
    if newProcessName == None:
      raise ValueError("got None as process name")
    if newProcessName in self.trainingProcesses.keys():
      raise ValueError("name {} is already a training process".format(newProcessName))
    if targetConfig in self.getCompletedTrainedConfigs():
      raise ValueError("target config name {} is already an existing config".format(targetConfig))
    if targetConfig in self.getTrainedConfigsInProgress():
      raise ValueError("target config name {} is already in use by currently running process".format(targetConfig))
#    cmd = ['python', 'train.py', targetConfig]

    #if startConfig == None:
    #  cmd = ['python train.py {}'.format(targetConfig)
    #else:
#    if startConfig != None:
#      if startConfig in getTrainedConfigs:
#        cmd.append(startConfig)
#      else:
#        raise ValueError('start config is not a valid config')
    #cmd = 'python backend/train.py {} {}'.format(targetConfig, startConfig)

    cmd = ['python', 'train.py', targetConfig, ' '.join(['backend/music_uploads/' + xmlfile for xmlfile in xmlFileList])]

    def enqueue_output(out, queue):
      for line in iter(out.readline, b''):
        queue.put(line)
      out.close()

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True # thread dies with the program
    t.start()

    self.trainingProcesses[newProcessName] = (p, targetConfig, q, '')

  def getOutputForTrainingProcess(self, processName):
    self.__cleanup()
    if not processName in self.trainingProcesses:
      return "(terminated)"
    else:
      proc, targetconfig, q, output = self.trainingProcesses[processName]
      return output



