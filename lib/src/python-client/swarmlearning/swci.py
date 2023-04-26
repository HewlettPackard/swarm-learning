#######################################################################
## (C)Copyright 2023 Hewlett Packard Enterprise Development LP
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.
#######################################################################


##################################################################
#                 S W C I  W E B  A P I                          #
##################################################################
#  The file exports SWCI commands as easy to use methods.        #
#  It is a very light weight wrapper around SWCI command.        #
#  It uses SWCI in WEB MODE as the backend                       #
##################################################################

import logging

import networkx as nx # used for topology visualization
import os
import requests
import urllib3

from enum import Enum
from pathlib import Path
from time import sleep

# list of command whose output does not change frequently 
# hence can be cached to avoid network round trips 
class SwciCacheKey(Enum):
    # space in the string is necessary 
    GET_CONTEXT_INFO    = 'get context info '
    GET_CONTRACT_INFO   = 'get contract info '    
    GET_TASK_BODY       = 'get task body '    
    GET_TASK_INFO       = 'get task info '
    GET_TASKRUNNER_INFO = 'get taskrunner info '
    LIST_CONTEXT        = 'list contexts'
    LIST_CONTRACTS      = 'list contracts'    
    LIST_TASKS          = 'list tasks'    
    LIST_TASKRUNNERS    = 'list taskrunners'

# Primary class that exposes the API     
class Swci:
    def __init__(self, 
                 swciIp, 
                 port = int(30306), 
                 clientCert = None, 
                 clientPKey = None,
                 clientCABundle = None,
                 logger = None, 
                 logLv = logging.WARNING,
                 enableCaching = True): 
        # setup the logger first. If the user has provided 
        # it use , else create a new one.
        self.__logger = logger            
        if not isinstance(self.__logger, logging.Logger):
            self.__logger = logging.getLogger('swci-web')
            logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
            fileHandler = logging.FileHandler("swci-web.log")
            fileHandler.setFormatter(logFormatter)
            self.__logger.addHandler(fileHandler)
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            self.__logger.addHandler(consoleHandler)            
            self.__logger.setLevel(logLv)
            self.__logger.info('Using Default SWCI-WEB Logger')
            
        # perform Input validations
        if swciIp is None:
            errStr = 'SWCI IP not provided!'
            self.__logger.error(errStr)
            raise RuntimeError(errStr)
            
        if not isinstance(port, int):
            errStr = 'SWCI Port not Integer!'
            self.__logger.error(errStr)
            raise RuntimeError(errStr)                    

        # setup client side security for URL access
        # Ref: https://docs.python-requests.org/en/latest/user/advanced/#ca-certificates
        self.__sess = requests.Session()
        # TODO: Clean-up mTLS / TLS with SWCI server
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.__secure = False
        self.__cert = None
        # path to the combined key/client cert file
        if clientCert is not None:
            self.__cert = clientCert
            self.__secure = True
            # path to the key and client cert as seperate files
            if clientPKey is not None:    
                self.__cert = (clientCert, clientPKey)
            if clientCABundle is not None:
                os.environ['REQUESTS_CA_BUNDLE'] = clientCABundle
                
        if self.__secure:
            self.__url = "https://%s:%s/exec?cmd="%(swciIp, port)
            self.__uploadUrl = "https://%s:%s/uploadTaskDef"%(swciIp, port)
            self.__sess.cert = self.__cert
        else:    
            self.__url = "http://%s:%s/exec?cmd="%(swciIp, port)
            self.__uploadUrl = "http://%s:%s/uploadTaskDef"%(swciIp, port)

        self.__logger.info('SWCI Url Prefix = ' + self.__url)
        # cache of resultsets of execCmd , to minimize 
        # the Network calls
        # key = command string 
        # value = ResultSet 
        self.__enableCaching = enableCaching
        self.__rsCache = {}
        # store the error for current command if any
        # if the command was successful , this is set to None
        # see self.__execCmd for details
        self.__curError = None

    def setLogLevel(self, logLv):
        # supported Levels 
        level = {}
        level['CRITICAL'] = logging.CRITICAL
        level['ERROR'] = logging.ERROR
        level['WARNING'] = logging.WARNING
        level['INFO'] = logging.INFO
        level['DEBUG'] = logging.DEBUG
        self.__logger.setLevel(level.get(str(logLv), logging.WARNING))
        
    def getErrors(self):
        errStr = None    
        if self.__curError:
            errStr = '\n'.join(self.__curError)
        return errStr
        
    def clearCache(self):
        # contents will be garbage collected
        self.__rsCache = {}
        
    def __execCmd(self, cmdStr, cache = False):
        # IF 'cache' is True and caching is enabled.
        # we will first check in the cache.
        # If the entry is found we will return it. 
        # Else we will do a 
        # fresh fetch and add it to the cache 
        # IF 'cache' is False 
        # we will always fetch the results and 
        # not cache it as well.
        if cache and self.__enableCaching:
            cRes = self.__rsCache.get(cmdStr, None)
            if cRes:
                # only successful command go into 
                # cache so self.__curError is reset 
                # to None
                self.__curError = None
                return cRes
               
        url = self.__url + cmdStr
        self.__logger.debug("POSTING URL : " + url)
        try:
            # We are passing parameters in URL string 
            # itself, since commands are short strings
            r = self.__sess.post(url, verify=False)
            result = r.json()
            if result:
                ret = []                            
                # check for errors
                for cl in result['CONTENT']:
                    if cl.startswith("ERROR "):
                        self.__logger.error(cl)
                        # set the current error message 
                        # returned by swci server
                        self.__curError = [cl]
                        # return on first error
                        return []
                    else:    
                        # process all lines
                        for l in cl.splitlines():
                            ret.append(l.strip())
                # have some valid values and we are 
                # requested to cache it, cache it!!
                if len(ret) > 0 and cache and self.__enableCaching: 
                    self.__rsCache[cmdStr] = ret
                    
                # command was successful clear previous error
                self.__curError = None 
                return ret
            else:
                errStr = 'ERROR : Command did not produce output'
                self.__logger.warning(errStr)
                self.__curError = [errStr]
                return []
        except Exception as e:
            errStr = 'ERROR : Exception occurred during POST request'        
            print(e)
            self.__logger.debug("EXCEPTION :")
            self.__logger.debug(e)
            self.__logger.error(errStr)
            self.__curError = [errStr]
            return []
            
            
    # list of commands supported by SWCI-WEB 
    
    # Non-Cacheable Operations 
    def ls(self, optStr = ''):
        cmd = 'ls'
        if optStr: 
            cmd += ' ' + optStr
        return self.__execCmd(cmd)
        
    def pwd(self):
        return self.__execCmd('pwd')        
        
    def sleep(self, sleepTime):
        cmd = 'sleep '+str(sleepTime)
        return self.__execCmd(cmd)

    def cd(self, dirPath):
        return self.__execCmd('cd ' + dirPath)
        
    def getTaskRunnerStatus(self, trName):
        return self.__execCmd('get taskrunner status ' + trName)        
        
    def getTaskRunnerPeerStatus(self, trName, idx):
        return self.__execCmd('get taskrunner peer status %s %d'%(trName, idx))                
        
    def getTrainingContractStatus(self, ctName):
        return self.__execCmd('get contract status ' + ctName)                
        
    # this list is dynamic and changes with topology 
    # so dont cache it    
    def listNodes(self):
        return self.__execCmd('list Nodes')                
        
    # cacheable operations 
    # this data does not mutate read once and keep it!
    def getContextInfo(self, ctxName):
        return self.__execCmd(SwciCacheKey.GET_CONTEXT_INFO.value + ctxName, 
                              cache = True)
        
    def getTrainingContractInfo(self, ctName):
        return self.__execCmd(SwciCacheKey.GET_CONTRACT_INFO.value + ctName, 
                              cache = True)
        
    def getTaskRunnerInfo(self, trName):
        return self.__execCmd(SwciCacheKey.GET_TASKRUNNER_INFO.value + trName, 
                              cache = True)

        
    # cacheable also mutable 
    # getTaskBody/TaskInfo mutates with delete task    
    # listContexts/listTrainingContracts/listTaskRunners 
    # mutate due to corresponding Create Operations
    # listTasks mutates due to Create or Delete operation 
    def getTaskInfo(self, taskName):
        return self.__execCmd(SwciCacheKey.GET_TASK_INFO.value + taskName, 
                              cache = True)        
        
    def getTaskBody(self, taskName):
        return self.__execCmd(SwciCacheKey.GET_TASK_BODY.value + taskName, 
                              cache = True)        
                              
    def listTrainingContracts(self):
        return self.__execCmd(SwciCacheKey.LIST_CONTRACTS.value, 
                              cache = True)
        
    def listContexts(self):
        return self.__execCmd(SwciCacheKey.LIST_CONTEXT.value, 
                              cache = True)        
        
    def listTaskRunners(self):
        return self.__execCmd(SwciCacheKey.LIST_TASKRUNNERS.value, 
                              cache = True)        
        
    def listTasks(self):
        return self.__execCmd(SwciCacheKey.LIST_TASKS.value, 
                              cache = True)        
    
    def switchContext(self, ctxName):
        cmd = 'switch context %s'%(ctxName)
        ret = self.__execCmd(cmd)
        return ret

    # operations that change state in the Blockchain        
    # or back end SWCI , these should not be cached
    # User can create SWCI Context with IP and Port
    # Or with service [eg:api.sn.swarm:30304]
    def createContext(self, ctxName, ip=None, port=30304, service=None):
        # Default API server port as documented in
        # Swarm Learning documentation
        # https://github.com/HewlettPackard/swarm-learning/blob/master/docs/RunningSL.md
        if ip is None and service is None:
            raise RuntimeError('For creating context either IP or Service name is mandatory!')
        if ip is not None:
            cmd = 'create context %s with ip %s %d'%(ctxName,ip,int(port))
        else:
            cmd = 'create context %s with service %s'%(ctxName,service)
        ret = self.__execCmd(cmd)
        if ret: # cache maintenance 
            # clean up the context list, ignore errors
            self.__rsCache.pop(SwciCacheKey.LIST_CONTEXT.value, None)
        return ret
    
    def createTrainingContract(self, ctName):
        #https://github.hpe.com/yoshio-sugiyama/swarm-learning-examples/issues/1
        ret = self.__execCmd('create contract ' + ctName)
        if ret: # cache maintenance 
            # clean up the contract list, ignore errors
            self.__rsCache.pop(SwciCacheKey.LIST_CONTRACTS.value, None)
        return ret    
        
    # Clean the Taskrunner for reuse    
    def resetTaskRunner(self, trName = 'defaulttaskbb.taskdb.sml.hpe'):
        return self.__execCmd('reset taskrunner ' + trName)        
        
    # Clean the training contract for reuse    
    def resetTrainingContract(self, ctName = 'defaultbb.cqdb.sml.hpe'):
        return self.__execCmd('reset contract ' + ctName)        
        
    def createTaskFrom(self, yamlFileName):
        ret = self.__execCmd('create task from ' + str(yamlFileName))
        if ret: # cache maintenance 
            # clean up the task list, ignore errors
            self.__rsCache.pop(SwciCacheKey.LIST_TASKS.value, None)                
        return ret 
        
    def deleteTask(self, taskName):
        ret = self.__execCmd('delete task ' + str(taskName))
        if ret: # cache maintenance 
            # clean up the task list, ignore errors
            self.__rsCache.pop(SwciCacheKey.LIST_TASKS.value, None)
            # clean up the task body and task info also
            self.__rsCache.pop(SwciCacheKey.GET_TASK_BODY.value + str(taskName), None)
            self.__rsCache.pop(SwciCacheKey.GET_TASK_INFO.value + str(taskName), None)
        return ret 
        
    def finalizeTask(self, taskName):
        return self.__execCmd('finalize task ' + str(taskName))        
        
    def registerTask(self, yamlFileName, finalize = True):
        ret = self.createTaskFrom(yamlFileName)
        if not ret:
            # if we got an error, execCmd would have 
            # caught it and stored in self.__curError
            # which can be retrieved by getErrors()
            return ret 
            
        # if we are here we are successful in creating 
        # the task
        taskName = None
        for l in ret:
            if 'Task Registered' in l:
                taskName = (l.split(':')[1]).strip()
                break
                
        if finalize and taskName:
            ret = self.finalizeTask(taskName)
            if not ret:
                return []
            else:
                return ['Registered Task : %s'%(taskName)]
        else:
            return ret
        
    def assignTask(self, taskName, trName, peers):
        cmd = 'assign task %s to %s with %d peers'%(taskName,trName,int(peers))
        return self.__execCmd(cmd)
        
    def isTaskDone(self, trName):
        res = self.getTaskRunnerStatus(trName)
        if res:
            for l in res:
                if 'TASK_STATE' in l:
                    status = l.split(':')[1].strip() 
                    if status in ['COMPLETE','ERROR','IDLE']:
                        return True
        else: 
            # taskrunner status call was not successful                        
            raise RuntimeError(self.getErrors())
        return False
        
   
    # Visualization Methods
    # User can pass the node colours and attribute they want to see.
    # Defaults:
    #  SNColour: LightBlue SWOPColour: Green SLColor: Light Red
    #  Default Attributes: ['NodeType' , 'HostIP']
    def plotTopology(self, SNColour="#ADD8E6", SWOPColor="#33FF33", SLColor="#FFCCCB", attrs=[]):
        res = self.listNodes()
        if not res:
            return 
        # Plot the graphs
        # create empty graph
        g = nx.MultiGraph()
        treeDict = {}
        nodeList = []
        nodeColour = []
        nodeLables = {}
        for ix, l in enumerate(res):
            #Skipping the header
            if ix==0:
                continue
            resTup = l.strip().split(',')
            data = {}
            data['NodeType'] = resTup[0].strip()
            data['HostIP'] = resTup[1].strip()
            data['Port'] = resTup[2].strip()
            data['ContainerName'] = resTup[3].strip()
            data['UUID'] = resTup[4].strip()
            data['ParentUUID'] = resTup[5].strip()
            data['i-am-alive'] = resTup[6].strip()
            # check if we have entry for self.
            # if not make one
            tSelf = treeDict.get(data['UUID'], None)
            if tSelf is None:
                treeDict[data['UUID']] = {'ix': ix, 'edges': []}
            else:    
                treeDict[data['UUID']]['ix'] = ix
                
            # check if there is an entry for parent
            tParent = treeDict.get(data['ParentUUID'], None)
            if tParent is None :
                if data['NodeType'] != 'SENTINEL' and data['NodeType'] != 'SN':
                    # at this point we dont know the 
                    # parents idx
                    temp = {'ix': -1, 'edges': []}
                    temp['edges'].append(ix)
                    treeDict[data['ParentUUID']] = temp
            else:
                treeDict[data['ParentUUID']]['edges'].append(ix)
            twoTup = (ix, data)
            nodeList.append(twoTup)
            if data['NodeType'] == 'SN' or data['NodeType'] == 'SENTINEL' or data['NodeType'] == 'FULLNODE':
                nodeColour.append(SNColour)
                nodeLables[ix] = 'SN\n' + data['HostIP']
            elif data['NodeType'] == 'SWOP':
                nodeColour.append(SWOPColor)
                nodeLables[ix] = 'SW\n' + data['HostIP']
            elif data['NodeType'] == 'SL':
                nodeColour.append(SLColor)
                nodeLables[ix] = 'SL\n' + data['HostIP']
            else:
                nodeColour.append('#1f78b4') # Default
            #User can pass any attibute which is part of list nodes output.
            #This includes, NodeType HostIP Port ContainerName UUID ParentUUID 'i-am-alive'.
            for attr in attrs:
              if attr == 'NodeType' or attr == 'HostIP':
                continue
              nodeLables[ix] = nodeLables[ix] + '\n'+ data[attr]
        # add the nodes to the graph
        g.add_nodes_from(nodeList)
        # define edges 
        for k in treeDict:
            parentIx = treeDict[k]['ix']
            edgeList = treeDict[k]['edges']
            if len(edgeList) > 0:
                # this node has children
                for e in edgeList:
                    g.add_edges_from([(parentIx,e)])

        #pick layout 
        pos = nx.spring_layout(g, k=0.8) # k controls the distance between the nodes and varies between 0 and 1
        nx.draw_networkx_nodes(g,pos, node_color=nodeColour) 
        nx.draw_networkx_edges(g,pos, edgelist=g.edges(), edge_color ='black') 
        nx.draw_networkx_labels(g,pos, labels=nodeLables)
        
    def executeTask(self, 
                    taskName, # task to execute  
                    tr ='defaulttaskbb.taskdb.sml.hpe', # which taskrunner to execute it on 
                    peers = int(1), # number of peers required to start
                    pollWaitInSec = int(120), # wait time before polling for status
                    resetTROnSuccess = True): 
        # STEP 1: Assign task to Taskrunner
        res = self.assignTask(taskName,tr,peers)
        if not res:
            self.__logger.error('Could not assign task %s on %s'%(taskName, tr))
            return res
        print('Assigned task %s on %s for execution'%(taskName, tr))
        
        # STEP 2: Monitor task execution and periodically report status 
        done = self.isTaskDone(tr)
        while (not done):
            print('Waiting for task %s to complete'%(taskName))
            sleep(pollWaitInSec)
            done = self.isTaskDone(tr)
            
        # STEP 3: when task completes or errors report the final status 
        res = self.getTaskRunnerStatus(tr)
        success = False
        # identify if the task was successful or errored out 
        # we will reset the taskrunner if the task was successful
        for l in res:
            if 'TASK_STATE' in l:
                status = l.split(':')[1].strip() 
                if status in ['COMPLETE']:
                    success = True 
                    break
                elif status in ['ERROR']:
                    success = False
                    break
        res.append("="*40)
        for i in range(peers):
            res.extend(self.getTaskRunnerPeerStatus(tr, i))
            res.append("="*40)

        for l in res:
            print(l)
            
        if resetTROnSuccess and success:
            self.resetTaskRunner(tr)
            
    def uploadTaskDefintion(self, taskFilePath):
        p = Path(taskFilePath).resolve()
        if not p.is_file():
            raise RuntimeError('Task definition file not found : ' + str(p))
            
        files = {'file': open(str(p), 'rb')}
        try:
            r = self.__sess.post(self.__uploadUrl, files=files, verify=False)
            return r.text
        except Exception as e:
            raise RuntimeError('Task definition file upload failed')            
