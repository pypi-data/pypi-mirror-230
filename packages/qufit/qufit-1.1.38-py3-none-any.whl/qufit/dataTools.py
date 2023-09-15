import numpy as np
import scipy as sp 
import sympy as sy, imp
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from . import optimize as op
op = imp.reload(op)
import math, time as TM
import pprint
from itertools import product


xvar = sy.Symbol('x',real=True)

def Print(*data,width=30, compact=True, indent=1, depth=3):
    
    pp = pprint.PrettyPrinter(width=width, compact=compact, 
                              indent=indent, depth=depth)
    pp.pprint(data)

def printTime(FORMAT="%Y/%m/%d %A %H:%M:%S",printinfo=True):
    x = TM.strftime(FORMAT,TM.localtime())
    if printinfo:
        print(x)
    return x

def bitstring(level=2,repeat=2,dtype='str'):
    x = product(range(level),repeat=repeat)
    if dtype == 'str':
        return iter([''.join(str(i) for i in j) for j in x])
    else:
        return x
    
def numTobinstring(num,ndigits=None):
    if ndigits is None:
        return format(num,'b')
    else:
        x = format(num,'b')
        l = len(x)
        if l != ndigits:
            x = '0'*(ndigits-len(x)) + x
        return x

def nearest(y,target,x=None):
    y = np.array(y)
    if x is None:
        index = np.argmin(np.abs(y-target))
        return index, None
    else:
        x = np.array(x)
        index = np.argmin(np.abs(y-target))
        return index, x[index]

def maxFreq(paras):
    """
    fc: qubit's frequency at known point
    bias=bias(f_target) - bias(fc)
    """
    func,voffset, vperiod = op.Spec2d_Fit().func_f01, paras[0], paras[1]
    v = np.linspace(-vperiod/2,vperiod/2,50001) + voffset
    y = func
    fmax = np.max(y(v,paras))
    return fmax
# def specfunc2data(func,)
def specshift(paras,fc,bias=0,side='lower'):
    """
    fc: qubit's frequency at known point
    bias=bias(f_target) - bias(fc)
    """
    func,voffset, vperiod = op.Spec2d_Fit().func_f01, paras[0], paras[1]
    v = np.linspace(-vperiod/2,vperiod/2,50001) + voffset
    # y = sy.lambdify(xvar,func,'numpy')
    y = func
    if side == 'lower':
        f01 = y(v,paras)[v<voffset]
        _, vtarget = nearest(f01,fc,v[v<voffset])
        vdiff = voffset - vtarget
        paras[0] += vdiff
        # v = np.linspace(-vperiod/2,vperiod/2,50001) + (voffset+vdiff)
        return y(bias,paras), (vtarget+bias)

    if side == 'higher':
        f01 = y(v,paras)[v>voffset]
        _, vtarget = nearest(f01,fc,v[v>voffset])
        vdiff = voffset - vtarget
        paras[0] += vdiff
        # v = np.linspace(-vperiod/2,vperiod/2,50001) + (voffset+vdiff)
        return y(bias,paras), (vtarget+bias)

def biasshift(paras,fc,fshift=0,side='lower'):
    """
    fc: qubit's frequency at known point
    fshift: = f_target - fc
    """
    func,voffset, vperiod = op.Spec2d_Fit().func_f01, paras[0], paras[1]
    v = np.linspace(-vperiod/2,vperiod/2,50001) + voffset
    # y = sy.lambdify(xvar,func,'numpy')
    y = func
    if np.max(fc+fshift)>np.max(y(v,paras)):
        raise('too big')
    if side == 'lower':
        vnew = v[v<voffset]
        f01 = y(v,paras)[v<voffset]
        finterp = sp.interpolate.interp1d(f01,vnew)
        _, vtarget = nearest(f01,fc,vnew)
        return finterp(fc+fshift)-vtarget, vtarget
    if side == 'higher':
        vnew = v[v>voffset]
        f01 = y(v,paras)[v>voffset]
        finterp = sp.interpolate.interp1d(f01,vnew)
        _, vtarget = nearest(f01,fc,vnew)
        return finterp(fc+fshift)-vtarget, vtarget

# def dresscali(funclist,dressenergy,fc,imAmp=0,side='lower'):

#     fnew = dressenergy(imAmp)-f_ex/1e9
#     bias_offset = dt.biasshift(specfuncz,f_ex/1e9,fnew,'lower')

def Z_scale_predict(q_ex,q_z,measure,f_ref=4.437e9,freq_up=120e6,freq_down=20e6):
    qubits = list(measure.qubits.values())
    up_scales = {}
    down_scales = {}
    n_bar = (q_ex.index+q_z.index)/2
    i_counts = 0
    for qubit in qubits:

        if abs(qubit.index-n_bar)<0.6:
            up_scales[qubit.q_name]=qubit.volt

        if 0.6<abs(qubit.index-n_bar)<1.6:
            f_target = f_ref+(-1)**i_counts*freq_up
            zc_ref = qubit.volt
            up_scales[qubit.q_name]=f_ref_To_f_target(qubit,f_target/1e9,f_ref/1e9,0,zc_ref=zc_ref)[1]
            i_counts += 1

        if abs(qubit.index-n_bar)>1.6:
            f_target = f_ref+(-1)**i_counts*freq_down
            zc_ref = qubit.volt
            up_scales[qubit.q_name]=f_ref_To_f_target(qubit,f_target/1e9,f_ref/1e9,0,zc_ref=zc_ref)[1] 
            i_counts += 1

    up_scales_copy = up_scales.copy()
    
    for i,qubit in enumerate(qubits):
        down_scales[qubit.q_name] = 2*qubit.volt - up_scales_copy[qubit.q_name]
    return [up_scales,down_scales]

def f_ref_To_f_target(qubit_ex,f_target,f_ref,dc_ref=0,zc_ref=0):
    volt_ex1, vtarget = biasshift(qubit_ex.specfuncz,f_ref,f_target-f_ref,side=qubit_ex.side)
    dc = volt_ex1*qubit_ex.T_bias[0]/qubit_ex.T_z[0] + dc_ref
    zc = volt_ex1 + zc_ref
    return dc, zc

def vTophi(funclist,T_bias,fc,side='lower'):
    assert fc < 10
    func,voffset, vperiod, ejs, ec, d = funclist
    vperiod, voffset = T_bias
    tmp_s = np.pi*(xvar-voffset)/vperiod
    func = sy.sqrt(8*ejs*ec*sy.Abs(sy.cos(tmp_s))*sy.sqrt(1+d**2*sy.tan(tmp_s)**2))-ec
    v = np.linspace(-vperiod/2,vperiod/2,50001) + voffset
    y = sy.lambdify(xvar,func,'numpy')
    if side == 'lower':
        vnew = v[v<voffset]
        f01 = y(v)[v<voffset]
        # finterp = sp.interpolate.interp1d(f01,vnew)
        index, vtarget = nearest(f01,fc,vnew)
        return vtarget
    if side == 'higher':
        vnew = v[v>voffset]
        f01 = y(v)[v>voffset]
        # finterp = sp.interpolate.interp1d(f01,vnew)
        index, vtarget = nearest(f01,fc,vnew)
        return vtarget

def search_idle_point(measure,f_now,f_targets,dcstate):
    print(dcstate)
    for i,j in enumerate(measure.qubitToread):
        qubit_ex=measure.qubits[j]
        f_target = f_targets[i]
        num = measure.qubitToread.index(qubit_ex.q_name)
        f_ref = f_now[num]
        dc_ref = dcstate[qubit_ex.q_name]
        dcstate[qubit_ex.q_name] = round(f_ref_To_f_target(qubit_ex,f_target,f_ref,dc_ref)[0],5)
    print(dcstate)
    return dcstate

def chi_cq(qubit):
    delta_cq = qubit.f_lo - qubit.f_ex
    g_cq, alpha = qubit.g_cq, qubit.alpha
    chi = g_cq**2/delta_cq/(1+delta_cq/alpha)
    return chi

def acstarkShift(qubit,readamp=0,side='lower'):
    res, _, chi = qubit.acstark_shift
    chiRatio = chi_cq(qubit) / chi
    freqdownShift = chiRatio*res[0]*readamp**2   ###### -2*chi*n = -2*chi*m*readamp**2
    print(freqdownShift)
    readvolt, _ = biasshift(qubit.specfuncz,qubit.f_ex/1e9,fshift=freqdownShift,side=side)
    return -readvolt

def anglehist(value,bins=100,circle=False):
#     comstd = lambda x: np.sqrt(np.std(np.real(x))**2+np.std(np.imag(x))**2)
    if circle:
        center = np.mean(value)
        r = np.std(value)
        mask = np.abs(value-center) <= r
        value = value[mask]
    comspace = lambda x: np.abs(x-np.mean(x))
    angle = np.angle(value-np.mean(value))
    space = comspace(value)
    step = math.gcd(len(angle),bins)
    index = np.argsort(angle)
    # x = angle[index]
    y = space[index]
    noise = []
    for i in range(0,len(angle)//step):
        start, end = i*step, (i+1)*step
        noise.append(np.mean(y[start:end]))
    noise_mean, noise_std = np.mean(noise), np.std(noise)
    return np.mean(value), noise_mean, noise_std, noise

# def Classify_fit(data,qnum=0,nstate=2):
#     data = np.array(data)
#     S = np.array([data[i,:,qnum] for i in range(nstate)]).flatten()
#     x,z = np.real(S), np.imag(S)
#     d = list(zip(x,z))
#     center = [(np.real(np.mean(data[i,:,qnum])),np.imag(np.mean(data[i,:,qnum]))) for i in range(nstate)] 

#     kmeans = KMeans(n_clusters=nstate,max_iter=1000,tol=0.0001,init =np.array(center))
#     kmeans.fit(d)
# #     c0, c1, c2 = kmeans.cluster_centers_[0,:], kmeans.cluster_centers_[1,:], kmeans.cluster_centers_[2,:]
#     color = kmeans.predict(d)
    
#     return x,z, kmeans.predict, kmeans.cluster_centers_, color

def Classify_fit(data,qnum=0,nstate=2):
    data = np.array(data)
    S = np.array([data[i,:,qnum] for i in range(nstate)]).flatten()
    x,z = np.real(S), np.imag(S)
    d = list(zip(x,z))
    center = [(np.real(np.mean(data[i,:,qnum])),np.imag(np.mean(data[i,:,qnum]))) for i in range(nstate)]

    kmeans = KMeans(n_clusters=nstate,max_iter=1000,tol=0.0001,init =np.array(center),n_init=1)
    kmeans.fit(d)
    center_fit = [kmeans.cluster_centers_[i,:] for i in range(nstate)]
#     c0, c1, c2 = kmeans.cluster_centers_[0,:], kmeans.cluster_centers_[1,:], kmeans.cluster_centers_[2,:]
    color = kmeans.predict(d)
    color0 = [kmeans.predict(d[i*(len(d)//nstate):(i+1)*(len(d)//nstate)]) for i in range(nstate)]
    # print(center_fit)
    p = [list(color0[i]).count(i)/len(color0[i]) for i in range(nstate)]
    
    return x,z, kmeans.predict, center_fit, color, p

def FFCC(FF,CC,f_rabi,dcstate,f_target):
    for i,q in enumerate(dcstate):
        f_t = f_target[i]
        c = CC[i]+[dcstate[q]]
        f = FF[i]+ [f_rabi[i]]
        if len(f)==3:
            index = np.argmax(abs(np.array(f)-f_t))
            f.pop(index)
            c.pop(index)
        FF[i]=f
        CC[i]=c
    return FF,CC

def classify(measure,s_st,target=None,predictexe=True,n_cluster=2):
    
    num = measure.n//2+measure.n%2
    name = ''
    for i in measure.qubitToread:
        name += i
    if target is not None:
        name = f'q{target+1}'
    fig, axes = plt.subplots(ncols=2,nrows=num,figsize=(9,4*num))
    n = measure.n if target is None else 1
    if predictexe:
        for i in range(n):
            i = target if target is not None else i
            # s_off, s_on = s_st[0,:,i], s_st[1,:,i]
            # S = list(s_off) + list(s_on)
            # x,z = np.real(S), np.imag(S)
            # d = list(zip(x,z))
            # kmeans = KMeans(n_clusters=n_cluster,max_iter=1000,tol=0.0001)
            # kmeans.fit(d)
            x,z, predict,center,color=Classify_fit(s_st,qnum=i,nstate=n_cluster)

            measure.predict[measure.qubitToread[i]] = predict
            # y = predict(d)
            y=color
            print(list(y).count(1)/len(y))
            ax = axes[i//2][i%2] if num>1 else axes[i]
            ax.scatter(x,z,c=y,s=10)
            ax.axis('equal')
            ax.set_title(f'p0={list(y).count(0)/len(y)},p1={list(y).count(1)/len(y)}')
        plt.savefig(r'D:\skzhao\fig\%s.png'%(name+'predict'))
        plt.close()

        fig, axes = plt.subplots(ncols=2,nrows=num,figsize=(9,4*num))
        for i in range(n):
            i = target if target is not None else i
            s_off, s_on = s_st[0,:,i], s_st[1,:,i]
            ss, which = s_on, 0
            d = list(zip(np.real(ss),np.imag(ss)))
            y = measure.predict[measure.qubitToread[i]](d)
            percent1 = list(y).count(which)/len(y)
            # measure.which[measure.qubitToread[i]]={'g':0,'e':1,'f':2}
            measure.onwhich[measure.qubitToread[i]] = (which if percent1 > 0.5 else 1-which)
            measure.offwhich[measure.qubitToread[i]] = (1-which if percent1 > 0.5 else which)
            percent_on = list(y).count(measure.onwhich[measure.qubitToread[i]])/len(y)
            ax = axes[i//2][i%2] if num>1 else axes[i]
            ax.scatter(np.real(ss),np.imag(ss),c=y,s=10)
            ax.set_title(f'|1>pop={round(percent_on*100,3)}%')
            ax.axis('equal')
        plt.savefig(r'D:\skzhao\fig\%s.png'%(name+'e'))
        plt.close()

        fig, axes = plt.subplots(ncols=2,nrows=num,figsize=(9,4*num))
        for i in range(n):
            i = target if target is not None else i
            s_off, s_on = s_st[0,:,i], s_st[1,:,i]
            ss, which = s_off, measure.offwhich[measure.qubitToread[i]]
            d = list(zip(np.real(ss),np.imag(ss)))
            y = measure.predict[measure.qubitToread[i]](d)
            percent_off = list(y).count(which)/len(y)
            measure.readmatrix[measure.qubitToread[i]] = np.mat([[percent_off,1-percent_on],[1-percent_off,percent_on]])
            ax = axes[i//2][i%2] if num>1 else axes[i]
            ax.scatter(np.real(ss),np.imag(ss),c=y,s=10)
            ax.set_title(f'|0>pop={round(percent_off*100,3)}%')
            ax.axis('equal')
        plt.savefig(r'D:\skzhao\fig\%s.png'%(name+'g'))
        plt.close()
    else:
        fig, axes = plt.subplots(ncols=2,nrows=num,figsize=(9,4*num))
        for i in range(n):
            i = target if target is not None else i
            s_off, s_on = s_st[0,:,i], s_st[1,:,i]
            ss, which = s_on, measure.onwhich[measure.qubitToread[i]] 
            d = list(zip(np.real(ss),np.imag(ss)))
            y = measure.predict[measure.qubitToread[i]](d)
            percent_on = list(y).count(which)/len(y)
            ax = axes[i//2][i%2] if num>1 else axes[i]
            ax.scatter(np.real(ss),np.imag(ss),c=y,s=10)
            ax.set_title(f'|1>pop={round(percent_on*100,3)}%')
            ax.axis('equal')
        plt.savefig(r'D:\skzhao\fig\%s.png'%(name+'classify'))
        plt.close()

def cutCircle(info_c0,info_c1,data):
        # print(data.shape)
        # data0, data1 = data[0,:], data[1,:]
        c0, r0 = info_c0[0], info_c0[1]
        c1, r1 = info_c1[0], info_c1[1]
        s0 = (data.real-c0.real)**2+(data.imag-c0.imag)**2
        s1 = (data.real-c1.real)**2+(data.imag-c1.imag)**2
        # idx = ((np.abs(s0)<r0**2) +  (np.abs(s1)<r1**2))
        s1_cut = (s1<r1**2)*1
        s0_cut = (s0<r0**2)*1
        num0 = np.count_nonzero(s0_cut)
        num1 = np.count_nonzero(s1_cut)
        # print(num0)
        num0 /= (num0+num1)
        num1 /= (num0+num1)

        return num0, num1

def find_circle(s_st,target=0,stdnum=[[1,1]],n_clusters=2,figsize=(9,14)):
    from collections.abc import Iterable
    dim = np.shape(s_st)[-1]
    target = target if isinstance(target,Iterable) else [target]
    fig, axes = plt.subplots(ncols=2,nrows=dim,figsize=(9,14))
    cLst_m, num0Lst, num1Lst = [], [], []
    cLst, pLst = [], []
    count = 0
    for i,qi in enumerate(range(dim)):
        ax0 = axes[i][0] if dim>1 else axes[0]
        ax1 = axes[i][1] if dim>1 else axes[1]
        if qi not in target:
            s_off, s_on = s_st[0,:,qi], s_st[1,:,qi]
            center1, center0 = np.mean(s_off), np.mean(s_on)
            sdiff = complex((center1-center0))
            s0 = s_off / (sdiff/np.abs(sdiff))
            s1 = s_on / (sdiff/np.abs(sdiff))
            s0 = np.real(s0)
            s1 = np.real(s1)
            bins = 120

            bin0 = ax1.hist(s0,bins=bins)
            bin1 = ax1.hist(s1,bins=bins)
         
            ax0.plot(np.real(s_off),np.imag(s_off),'.')
            ax0.plot(np.real(s_on),np.imag(s_on),'.')
            ax0.axis('equal')
            plt.tight_layout()
        else:
            
            x,z, predict,center,color,p=Classify_fit(s_st,qnum=i,nstate=n_clusters)
            pLst.append(p)
            center = np.array([center[i][0]+1j*center[i][1] for i in range(n_clusters)])
            center0, center1 = center[:2]
            if n_clusters < 3:
                s_off, s_on = s_st[0,:,qi], s_st[1,:,qi]
                sdiff = complex((center1-center0))
                s0 = s_off / (sdiff/np.abs(sdiff))
                s1 = s_on / (sdiff/np.abs(sdiff))
                s0 = np.real(s0)
                s1 = np.real(s1)
                bins = 120
                mu = complex(center1)/ (sdiff/np.abs(sdiff))
                x0 = np.linspace(min(s0),max(s0),bins)
                x1_old = np.linspace(min(s1),max(s1),bins)
                lower, high = np.real(mu)-2*np.std(s1), np.real(mu)+2*np.std(s1)
                x1 = x1_old[x1_old>lower]

                bin0 = ax1.hist(s0,bins=bins)
                bin1 = ax1.hist(s1,bins=bins)
                # para0, func0 = op.Gaussian_Fit().fitGaussian(x0,bin0[0],fine=False)
                # ax1.plot(x0,func0(x0,para0.x))
                b1 = bin1[0][x1_old>lower]
                b1 = b1[x1<high]
                x1 = x1[x1<high]
                # para1, func1 = op.Gaussian_Fit().fitGaussian(x1,b1,fine=False)
                # ax1.plot(x1,func1(x1,para1.x))
            #     axes[0].set_title(f'center={center0,center1}')

                # offstd, onstd = stdnum[count][0]*np.abs(para0.x[2]), stdnum[count][1]*np.abs(para1.x[2])
                offstd, onstd = stdnum[count][0]*np.std(s_off), stdnum[count][1]*np.std(s_on)
                theta = np.arange(0, 2*np.pi, 0.01)
                roff = center0.real + offstd * np.cos(theta)
                ioff = center0.imag + offstd * np.sin(theta)
                ron = center1.real + onstd * np.cos(theta)
                ion = center1.imag + onstd * np.sin(theta)
                ax0.plot(np.real(s_off),np.imag(s_off),'.')
                # ax0.plot(np.real(s_on2),np.imag(s_on2),'.',alpha=0.4)
                ax0.plot(np.real(s_on),np.imag(s_on),'.')
                ax0.plot(center1.real,center1.imag,'bo')
                ax0.plot(center0.real,center0.imag,'ro')
                ax0.plot(roff,ioff)
                ax0.plot(ron,ion)
                ax0.axis('equal')
                cLst_m = [(center0,offstd),(center1,onstd)]
                # cLst.append([c0Lst,c1Lst])
                num0, _ = cutCircle((center0,offstd),(center1,onstd),s_off)
                _, num1 = cutCircle((center0,offstd),(center1,onstd),s_on)
                num0Lst.append(num0)
                num1Lst.append(num1)
                plt.tight_layout()
            else:

                cLst_m = [(center[i],stdnum[count][i]*np.std(s_st[i,:,qi])) for i in range(n_clusters)]
                num0Lst, num1Lst = p[:2]
                for n_state in range(n_clusters):
                    s = s_st[n_state,:,qi]
                    ax0.plot(np.real(s),np.imag(s),'.')
                color = ['ko','wo','bo']
                for n_state in range(n_clusters):
                    s = s_st[n_state,:,qi]
                    theta = np.arange(0, 2*np.pi, 0.01)
                    roff = np.real(center[n_state]) + stdnum[count][n_state]*np.std(s) * np.cos(theta)
                    ioff = np.imag(center[n_state]) + stdnum[count][n_state]*np.std(s) * np.sin(theta)
                    ax0.plot(np.real(center[n_state]),np.imag(center[n_state]),color[n_state],label=str(n_state))
                    ax0.plot(roff,ioff)
                    ax0.axis('equal')
                ax0.legend()
            cLst.append(cLst_m)
            count += 1
    return cLst, num0Lst, num1Lst, fig, axes, pLst
    

def post_selection(measure,s,sigma_num=2):
    center0,center1 = [], []
    radius0, radius1 = [], []
    for i in measure.postSle:
        center0.append(np.complex(*(measure.postSle[i][0][0])))
        radius0.append(measure.postSle[i][0][1])
        center1.append(np.complex(*(measure.postSle[i][1][0])))
        radius1.append(measure.postSle[i][1][1])
    pop = []
    for i in range(np.shape(s)[1]):
        x0 = (np.abs(s[:,i,:]-np.array(center0))<np.array(radius0)*sigma_num)*1.0
        x1 = (np.abs(s[:,i,:]-np.array(center1))<np.array(radius1)*sigma_num)*1.0
#         y = x0 + x1
#         c = np.sum(y ,axis=1)
#         x0, x1 = x0[c==10,:], x1[c==10,:]
#         print(x0)
        pop_sum1 = np.sum(x1,axis=1)
#         pop_sum0 = np.sum(x0,axis=1)
        pop_q = x1[pop_sum1==5,:]
#         print(pop_q[:,8])
#         print(np.shape(pop_q))
        pop.append((np.count_nonzero(pop_q,axis=0)/len(pop_q)))
    return np.array(pop)

################################################################################
# 对比度
################################################################################

def visibility(n,s0,s1, center=None):
    theta = np.arange(0, 2*np.pi, 0.01)
    data = []
    for i in range(n):
        c0, c1 = (np.mean(s0), np.mean(s1)) if center is None else center
        s0 = s0 / ((c1-c0)/np.abs(c1-c0))
        s1 = s1 / ((c1-c0)/np.abs(c1-c0))
        s0 = np.real(s0)
        s1 = np.real(s1)
        bins = np.linspace(np.min(np.r_[s0,s1]), np.max(np.r_[s0,s1]), 61)
        y0,_ = np.histogram(s0, bins=bins)
        y1,_ = np.histogram(s1, bins=bins)
        inte0 = np.cumsum(y0)/np.sum(y0)
        inte1 = np.cumsum(y1)/np.sum(y0)
        inte_diff = np.cumsum(y0)/np.sum(y0) - np.cumsum(y1)/np.sum(y1)
        offstd, onstd = np.std(s0), np.std(s1)
        roff = np.real(c0) + offstd * np.cos(theta)
        ioff = np.imag(c0) + offstd * np.sin(theta)
        ron = np.real(c1) + onstd * np.cos(theta)
        ion = np.imag(c1) + onstd * np.sin(theta)
        data.append([inte0,inte1,inte_diff,(roff,ioff),(ron,ion)])
    return data

# def visibility(n,s0,s1, center=None):
#     from scipy.optimize import least_squares as ls, curve_fit, basinhopping as bh
#     def Two_Gaussian(x, amp0,amp1, mu0,mu1, sigma0,sigma1):
#         amp = np.array([amp0,amp1])
#         mu = np.array([mu0,mu1])
#         sigma = np.array([sigma0,sigma1])
#         return np.sum(amp*np.exp(-(x[:,None]-mu)**2/2/sigma**2),axis=-1)
    
#     theta = np.arange(0, 2*np.pi, 0.01)
#     data = []
#     for i in range(n):
#         c0, c1 = (np.mean(s0), np.mean(s1)) if center is None else np.array(center)[:,0]+1j*np.array(center)[:,1]
#         s0 = s0 / ((c1-c0)/np.abs(c1-c0))
#         s1 = s1 / ((c1-c0)/np.abs(c1-c0))
#         s0 = np.real(s0)
#         s1 = np.real(s1)
#         bins = np.linspace(np.min([s0,s1]), np.max([s0,s1]), 61)
#         y0,_ = np.histogram(s0, bins=bins)
#         y1,_ = np.histogram(s1, bins=bins)
#         inte0 = np.cumsum(y0)/np.sum(y0)
#         inte1 = np.cumsum(y1)/np.sum(y0)
#         inte_diff = np.cumsum(y0)/np.sum(y0) - np.cumsum(y1)/np.sum(y1)
#         offstd, onstd = np.std(s0), np.std(s1)
#         roff = np.real(c0) + offstd * np.cos(theta)
#         ioff = np.imag(c0) + offstd * np.sin(theta)
#         ron = np.real(c1) + onstd * np.cos(theta)
#         ion = np.imag(c1) + onstd * np.sin(theta)
#         data.append([inte0,inte1,inte_diff,(roff,ioff),(ron,ion)])
#         vmax = np.max(inte_diff)
#         thr, phi = bins[inte_diff==vmax], phi = np.angle(c1-c0)
        
#         center_new = (c0/((c1-c0)/np.abs(c1-c0)),c1/((c1-c0)/np.abs(c1-c0)))
#         popt0 ,pcov0 = curve_fit(Two_Gaussian,bins[:-1],y0,p0=[0,np.max(y1),np.array(center_new).real[0],np.array(center_new).real[1],np.std(y1),np.std(y1)])
#         popt1 ,pcov1 = curve_fit(Two_Gaussian,bins[:-1],y1,p0=[0,np.max(y1),np.array(center_new).real[0],np.array(center_new).real[1],np.std(y1),np.std(y1)])
#     return data, thr, phi, bins, y0, y1, popt0, pcov0, popt1, pcov1

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import EngFormatter, LogFormatterSciNotation
from scipy.optimize import least_squares as ls, curve_fit, basinhopping as bh
def Two_Gaussian(x, amp0,amp1, mu0,mu1, sigma0,sigma1):
    amp = np.array([amp0,amp1])
    mu = np.array([mu0,mu1])
    sigma = np.array([sigma0,sigma1])
    return np.sum(amp*np.exp(-(x[:,None]-mu)**2/2/sigma**2),axis=-1)


def plotLine(c0, c1, ax, **kwargs):
    t = np.linspace(0, 1, 11)
    c = (c1 - c0) * t + c0
    ax.plot(c.real, c.imag, **kwargs)


def plotCircle(c0, r, ax, **kwargs):
    t = np.linspace(0, 1, 1001) * 2 * np.pi
    s = c0 + r * np.exp(1j * t)
    ax.plot(s.real, s.imag, **kwargs)


def plotEllipse(c0, a, b, phi, ax, **kwargs):
    t = np.linspace(0, 1, 1001) * 2 * np.pi
    c = np.exp(1j * t)
    s = c0 + (c.real * a + 1j * c.imag * b) * np.exp(1j * phi)
    ax.plot(s.real, s.imag, **kwargs)


def plotDistribution(s0,
                     s1,
                     fig=None,
                     axes=None,
                     info=None,
                     hotThresh=10000,
                     logy=False):
    from waveforms.math.fit import get_threshold_info, mult_gaussian_pdf

    if info is None:
        info = get_threshold_info(s0, s1)
    else:
        info = get_threshold_info(s0, s1, info['threshold'], info['phi'])
    thr, phi = info['threshold'], info['phi']
    # visibility, p0, p1 = info['visibility']
    # print(
    #     f"thr={thr:.6f}, phi={phi:.6f}, visibility={visibility:.3f}, {p0}, {1-p1}"
    # )

    if axes is not None:
        ax1, ax2 = axes
    else:
        if fig is None:
            fig = plt.figure()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

    if (len(s0) + len(s1)) < hotThresh:
        ax1.plot(np.real(s0), np.imag(s0), '.', alpha=0.8)
        ax1.plot(np.real(s1), np.imag(s1), '.', alpha=0.8)
    else:
        _, *bins = np.histogram2d(np.real(np.hstack([s0, s1])),
                                  np.imag(np.hstack([s0, s1])),
                                  bins=50)

        H0, *_ = np.histogram2d(np.real(s0),
                                np.imag(s0),
                                bins=bins,
                                density=True)
        H1, *_ = np.histogram2d(np.real(s1),
                                np.imag(s1),
                                bins=bins,
                                density=True)
        vlim = max(np.max(np.abs(H0)), np.max(np.abs(H1)))

        ax1.imshow(H1.T - H0.T,
                   alpha=(np.fmax(H0.T, H1.T) / vlim).clip(0, 1),
                   interpolation='nearest',
                   origin='lower',
                   cmap='coolwarm',
                   vmin=-vlim,
                   vmax=vlim,
                   extent=(bins[0][0], bins[0][-1], bins[1][0], bins[1][-1]))

    ax1.axis('equal')
    # ax1.set_xticks([])
    # ax1.set_yticks([])
    for s in ax1.spines.values():
        s.set_visible(False)

    # c0, c1 = info['center']
    # a0, b0, a1, b1 = info['std']
    params = info['params']
    r0, i0, r1, i1 = params[0][0], params[1][0], params[0][1], params[1][1]
    a0, b0, a1, b1 = params[0][2], params[1][2], params[0][3], params[1][3]
    c0 = (r0 + 1j * i0) * np.exp(1j * phi)
    c1 = (r1 + 1j * i1) * np.exp(1j * phi)
    phi0 = phi + params[0][6]
    phi1 = phi + params[1][6]
    plotEllipse(c0, 2 * a0, 2 * b0, phi0, ax1)
    plotEllipse(c1, 2 * a1, 2 * b1, phi1, ax1)

    im0, im1 = info['idle']
    lim = min(im0.min(), im1.min()), max(im0.max(), im1.max())
    t = (np.linspace(lim[0], lim[1], 3) + 1j * thr) * np.exp(-1j * phi)
    ax1.plot(t.imag, t.real, 'k--')

    ax1.plot(np.real(c0), np.imag(c0), 'o', color='C3')
    ax1.plot(np.real(c1), np.imag(c1), 'o', color='C4')

    re0, re1 = info['signal']
    x, a, b, c = info['cdf']

    xrange = (min(re0.min(), re1.min()), max(re0.max(), re1.max()))

    n0, bins0, *_ = ax2.hist(re0, bins=100, range=xrange, alpha=0.5)
    n1, bins1, *_ = ax2.hist(re1, bins=100, range=xrange, alpha=0.5)

    x_range = np.linspace(x.min(), x.max(), 1001)
    *_, cov0, cov1 = info['std']

    c0, c1 = info['center']
    c0 /= ((c1-c0)/np.abs(c1-c0))
    c1 /= ((c1-c0)/np.abs(c1-c0))
    # print(len(n0),len(bins0))
    try:
        popt0 ,pcov0 = curve_fit(Two_Gaussian,bins0[:-1],n0,p0=[np.max(n0),0,c0.real,c1.real,np.std(n0),np.std(n1)])
        popt1 ,pcov1 = curve_fit(Two_Gaussian,bins1[:-1],n1,p0=[0,np.max(n1),c0.real,c1.real,np.std(n0),np.std(n1)])
        y0new = Two_Gaussian(x_range,*popt0)
        y1new = Two_Gaussian(x_range,*popt1)
    except:
        popt0 ,pcov0 = 0,0
        popt1 ,pcov1 = 0,0
        y0new = np.zeros_like(x_range)
        y1new = np.zeros_like(x_range)

    ax2.plot(
        x_range,
        y0new)
    ax2.plot(
        x_range,
        y1new)
    ax2.set_ylabel('Count')
    ax2.set_xlabel('Projection Axes')
    if logy:
        ax2.set_yscale('log')
        ax2.set_ylim(0.1, max(np.sum(n0), np.sum(n1)))

    ax3 = ax2.twinx()
    ax3.plot(x, a, '--', lw=1, color='C0')
    ax3.plot(x, b, '--', lw=1, color='C1')
    ax3.plot(x, c, 'k--', alpha=0.5, lw=1)
    ax3.set_ylim(0, 1.1)
    ax3.vlines(thr, 0, 1.1, 'k', alpha=0.5)
    ax3.set_ylabel('Probility')

    return info, [[popt0 ,pcov0],[popt1 ,pcov1]]

