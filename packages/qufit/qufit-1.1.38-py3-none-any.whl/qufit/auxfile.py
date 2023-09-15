import numpy as np

def saveconfig(task_id, title = 'title', fig=None, fold=None, show=True, basepath=r'G:\QuLabData\skzhao\data',cover=False):
    from datetime import date
    from pathlib import Path
    import os
    today=date.today()
    basepath = Path(r'G:\QuLabData\skzhao\data') if fold is None else Path(r'G:\QuLabData\skzhao\data'+f'\{fold}')
    basepath = basepath/today.strftime('%Y%m%d')
    foder=os.path.exists(basepath)
    if not foder:
        os.makedirs(basepath)
        print('New foder!')
    else:
        print('Exist!')

    a = 0
    title_new = title
    while basepath / (title_new+'.html') in [f for f in basepath.iterdir()]:
        a +=1
        title_new = title+f'_{a}'
#     np.savez(basepath / title_new, **data)
    if fig is not None:
        name = fig.layout.title.text
        if '_id' not in name:
            name += f'_id={task_id}'
            fig.update_layout(title=name)
        title_new_html = title_new + '.html'
        title_new_fig = title_new + '.png'
        fig.write_html(basepath / title_new_html)
        fig.write_image(basepath / title_new_fig)
    if show:
        fig.show()
    return basepath / title_new


class common():
    def __init__(self,**kws):
        attribute = ['qubits_read','all_qubits','all_couplers','all_jpas','ampLst_read','biasLst_read','biasLst_qubit',\
            'biasLst_couplers','biasLst_jpa','ampLst_jpa','output_jpa','phaseLst_jpa','biasLst_reset','duringLst_reset',
            'edgeLst_reset','ring_up_amp','ring_up_time']
        for j in attribute:
            self.__setattr__(j,None)
        if len(kws) != 0:
            for i in kws:
                self.__setattr__(i,kws[i])

        # self.kernel = kernel
        self.readmatrix = {}
        self.readoutM = {}
        self.info = {}

    def asdict(self):
        arg = self.__dict__
        arg_copy = arg.copy()
        # del arg_copy['kernel']
        return arg_copy

    def check_repeat(self):
        assert len(set(self.all_couplers)) == len(self.all_couplers)
        assert len(set(self.all_qubits)) == len(self.all_qubits)
        assert len(set(self.qubits_read)) == len(self.qubits_read)
        assert len(set(self.all_jpas)) == len(self.all_jpas)

    def replace(self,**kws):
        for i in kws:
            assert hasattr(self,i)
            self.__setattr__(i,kws[i])

    def getvalue(self,name):
        return self.__getattribute__(name)

    def setvalue(self,name,value):
        # argLst = self.__getattribute__(name)
        # idx = argLst.index()
        self.__setattr__(name,value)

    def initCfg(self,kernel):
        self.check_repeat()
        biasLst_read = [kernel.get(f'gate.Measure.{q}.params.bias') for q in self.qubits_read]
        ampLst_read = [kernel.get(f'gate.Measure.{q}.params.amp') for q in self.qubits_read]
        ring_up_amp = [kernel.get(f'gate.Measure.{q}.params.ring_up_amp') for q in self.qubits_read]
        ring_up_time = [kernel.get(f'gate.Measure.{q}.params.ring_up_time') for q in self.qubits_read]
        shelving = [kernel.get(f'gate.Measure.{q}.params.shelving') for q in self.qubits_read]

        biasLst_jpa = [kernel.get(f'{q}.setting.OFFSET') for q in self.all_jpas]
        output_jpa = [kernel.get(f'{q}.setting.OUTPUT') for q in self.all_jpas]
        ampLst_jpa = [kernel.get(f'gate.Amplify.{q}.params.amp') for q in self.all_jpas]
        phaseLst_jpa = [kernel.get(f'gate.Amplify.{q}.params.phase') for q in self.all_jpas]

        biasLst_reset = [kernel.get(f'gate.Reset.{q}.params.amp') for q in self.all_qubits]
        duringLst_reset = [kernel.get(f'gate.Reset.{q}.params.duration') for q in self.all_qubits]
        edgeLst_reset = [kernel.get(f'gate.Reset.{q}.params.edge') for q in self.all_qubits]

        biasLst_couplers = [kernel.get(f'{coupler0}.bias') for coupler0 in self.all_couplers]
        biasLst_qubit = [kernel.get(f'{q}.bias') for q in self.all_qubits]
        self.biasLst_read = biasLst_read
        self.ampLst_jpa = ampLst_jpa
        self.biasLst_jpa = biasLst_jpa
        self.output_jpa = output_jpa
        self.phaseLst_jpa = phaseLst_jpa
        self.ampLst_read = ampLst_read
        self.ring_up_amp = ring_up_amp
        self.ring_up_time = ring_up_time
        self.biasLst_couplers = biasLst_couplers
        self.biasLst_qubit = biasLst_qubit
        self.shelving = shelving
        self.biasLst_reset = biasLst_reset
        self.duringLst_reset = duringLst_reset
        self.edgeLst_reset = edgeLst_reset

        print('biasLst_read=',biasLst_read)
        print('ampLst_read=',ampLst_read)
        print('biasLst_jpa=',biasLst_jpa)
        print('ampLst_jpa=',ampLst_jpa)
        print('output_jpa=',output_jpa)
        print('phaseLst_jpa=',phaseLst_jpa)
        print(f'shelving={self.shelving}')
        print('ring_up_amp=',ring_up_amp)
        print('ring_up_time=',ring_up_time)
        print('biasLst_couplers=',biasLst_couplers)
        print('biasLst_qubit=',biasLst_qubit)
        print('biasLst_reset=',biasLst_reset)
        print('duringLst_reset=',duringLst_reset)
        print('edgeLst_reset=',edgeLst_reset)

    def write(self, kernel, name = None):
        # kernel = self.kernel if kernel is None else kernel
        if name is None:
            # count = 0
            for i,qubit in enumerate(self.all_qubits):
                kernel.set(f'{qubit}.bias',self.biasLst_qubit[i])
                kernel.set(f'gate.Reset.{qubit}.params.amp',self.biasLst_reset[i])
                kernel.set(f'gate.Reset.{qubit}.params.duration',self.duringLst_reset[i])
                kernel.set(f'gate.Reset.{qubit}.params.edge',self.edgeLst_reset[i])
                if qubit in self.qubits_read:
                    idx_meas = self.qubits_read.index(qubit)
                    kernel.set(f'gate.Measure.{qubit}.params.bias',self.biasLst_read[idx_meas])
                    kernel.set(f'gate.Measure.{qubit}.params.amp',self.ampLst_read[idx_meas])
                    kernel.set(f'gate.Measure.{qubit}.params.ring_up_amp',self.ring_up_amp[idx_meas])
                    kernel.set(f'gate.Measure.{qubit}.params.ring_up_time',self.ring_up_time[idx_meas])
                    # count += 1
                    
            for i, coupler in enumerate(self.all_couplers):
                kernel.set(f'{coupler}.bias',self.biasLst_couplers[i])
        else:
            for i,qubit in enumerate(self.qubits_read):
                paras = self.biasLst_read if name == 'bias' else self.ampLst_read
                kernel.set(f'gate.Measure.{qubit}.params.{name}',paras[i])

    def loadcfg(self,kernel):
        cfg = kernel.get('measure_mrw')
        for k in cfg:
            self.__setattr__(k,cfg[k])

        v = self.asdict()
        for k in v:
            print(k,v[k])

    def uploadcfg(self,kernel):

        v = self.asdict()
        for k in v:
            kernel.set(f'measure_mrw.{k}',v[k])

def readPop(result,readmatrix=False,reshape=True,datatype='population',
            statenum=2,qubits_read=None,caliMatrix=False,method='count1'):
    
    from collections import Counter
    from itertools import product
    result = result if isinstance(result,dict) else result()
    measure = result['meta']['arguments']['measure_mrw']
    readmatrix = measure['readmatrix'] if readmatrix else None
#     info = measure.info
    qubits_read = measure['qubits_read'] if qubits_read is None else qubits_read
    idxLst = np.array([measure['qubits_read'].index(q) for q in qubits_read])
    arg = list(result['index'].keys())
    
    def statePop(data=None,qubits_read_=None,reshape=reshape,caliMatrix=caliMatrix):
        qubits_read_, idxLst_ = (qubits_read,idxLst) if qubits_read_ is None \
        else (qubits_read_,np.array([measure.qubits_read.index(q) for q in qubits_read_]))

        coQubit = ''.join((*qubits_read,))
        caliMatrix = measure['readoutM'][coQubit] if caliMatrix else None
        
        def count1(data,qubits_read,statenum=2):

            state = product(2**np.arange(statenum), repeat=len(qubits_read))
            c = Counter(map(tuple, data))
            pop = [c[tuple(i)] for i in state]
            return np.array(pop)/np.sum(pop)
        def count2(data,qubits_read,statenum=2):
            state = product(2**np.arange(statenum), repeat=len(qubits_read))
            # print(list(state),data.shape)
            c = Counter(map(tuple, data))
            # print(c)
            pop = [c[tuple(i)] for i in state]
            return np.array(pop)/np.sum(pop)
        methodLst = {'count1':count1,'count2':count2}
        count_method = methodLst[method]
        s = result['state']
        y = s[:,:,idxLst_] if data is None else data
#         y = s
        # print(y.shape,y[0,:,:].shape)
        repeats = np.shape(s)[-2]
        pop = np.array([count_method(y[i,:,:],qubits_read,statenum) for i in range(np.shape(s)[0])])
        # pop = np.array([count1(y[i,:,:],qubits_read,statenum) for i in range(np.shape(y)[0])])

        coMatrix = np.mat(caliMatrix) if caliMatrix is not None else np.mat(np.eye(statenum**len(qubits_read)))
        pop_cali = np.array((coMatrix.I*np.mat(pop).T).T).flatten()
        # print(pop_cali)
        if reshape:
            length = []
            for idx_arg in arg:
                length.append(len(result['index'][idx_arg]))
            length.append(statenum**len(qubits_read))
            pop_cali = np.array(pop_cali).reshape(*length)
        return pop_cali
            
    def population():
        
        p1 = result['population']
        p0 = 1-p1
        if readmatrix is None:
            pop_cali = p1
        else:
            pop_cali = []
            for i,q in enumerate(qubits_read):
                mat = readmatrix[q] if q in readmatrix else np.mat(np.eye(2))
                pop = np.array(np.mat(mat).I*np.mat([p0[:,i],p1[:,i]]))
                pop_cali.append(pop[1,:])
            pop_cali = np.array(pop_cali).T
            
        if reshape:
            length = []
            for idx_arg in arg:
                length.append(len(result['index'][idx_arg]))
            length.append(len(qubits_read))
            pop_cali = (pop_cali).reshape(*length)
        return pop_cali

    def state2Pop(pop):
        state = product(range(statenum), repeat=len(qubits_read))
        state = np.array(list(state))
        pop_cali = []
        for i,q in enumerate(qubits_read):
            idx = state[:,i]==1
            p1 = pop[...,idx]
            p1 = np.sum(p1,axis=-1)
            pop_cali.append(p1)
        pop_cali = np.array(pop_cali).T

        return pop_cali
    
    if datatype == 'population':
        pop_cali = population()
        
    if datatype == 'state':
        pop_cali = statePop()

    if datatype == 'state2Pop':
        pop_cali = statePop(reshape=True)
        pop_cali = state2Pop(pop_cali)
        
    return pop_cali
