#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   optimize.py
@Time    :   2020/02/10 16:55:28
@Author  :   sk zhao 
@Version :   1.0
@Contact :   2396776980@qq.com
@License :   (C)Copyright 2017-2018, Zhaogroup-iop
@Desc    :   None
'''

# here put the import lib
import time, numpy as np, matplotlib.pyplot as plt
from scipy import fftpack
from sklearn.cluster import KMeans
from scipy.optimize import least_squares as ls, curve_fit, basinhopping as bh
from scipy import signal
import asyncio, scipy
import sympy as sy
from collections import Counter
from collections.abc import Iterable
xvar = sy.Symbol('x',real=True)

'''
主要采用了全局优化的思想进行拟合
相比于optimize_old模块，该模块的思想是利用全局最优化算法进行数据拟合，方法采自scipy.optimize模块，以basinhopping为例，就是来最小化残差函数，
相比于最小二乘法，他要求残差函数返回的为每一点的残差平方和，该法对初始值相对不敏感，精度高。
'''


# func_willBeused = {'Expfunc':Exp_Fit().func}


################################################################################
### 拟合参数边界
################################################################################

class MyBounds(object):
    def __init__(self, xmax=[1.1,1.1], xmin=[-1.1,-1.1] ):
        self.xmax = np.array(xmax)
        self.xmin = np.array(xmin)
    def __call__(self, **kwargs):
        x = kwargs["x_new"]
        tmax = bool(np.all(x <= self.xmax))
        tmin = bool(np.all(x >= self.xmin))
        return tmax and tmin
        
################################################################################
### 生数据预处理  exeFit
###################### ##########################################################

class RowToRipe():
    def __init__(self):
        pass
    def space(self,y):
        ymean, ymax, ymin = np.mean(y), np.max(y), np.min(y)
        d = y[np.abs(y-ymean)>0.05*(ymax-ymin)]
        if len(d) < 0.9*len(y):
            return len(d) + int(len(y)*0.1)
        else:
            return len(y)
    
    def errspace(self,func,paras,args):

        return (func(args['x'],paras)-args['y'])**2

    def deductPhase(self,x,y):
        if np.ndim(y) != 2:
            y = [y]
        s = []
        for i in y:
            phi = np.unwrap(np.angle(i), 0.9 * np.pi)
            phase = np.poly1d(np.polyfit(x, phi, 1))
            base = i / np.exp(1j * phase(x))
            s.append(base)
        return x, np.array(s)

    def manipulation(self,volt,freq,s,which='min',dosmooth=False,f0=0.25,axis=1):
        manfunc = np.argmin if which == 'min' else np.argmax
        s_abs = np.abs(s) 
         
        if dosmooth: 
            s_abs = self.smooth(s_abs,axis=axis,f0=f0)
            # min_index = []      
            # for i in range(np.shape(s)[axis]):
            #     z = s_abs[i,:]
            #     # loc = freq[manfunc(z)]
            #     z_smooth = self.movingAverage(z,smoothnum)
            #     # t,index = self.firstMax(freq,z_smooth,num=loc,peakpercent=0.9,insitu=True)
            #     index = manfunc(z_smooth)
            #     min_index.append(index)
        # else:
        #     min_index = manfunc(s_abs,axis=axis)     
        min_index = manfunc(s_abs,axis=axis)         
        x, y = np.array(volt), np.array([freq[j] for j in min_index]) 
        return x,y

    def extension(self,s,ax=0,periodic_extension=0,padding=0):
        axis = np.shape(s)

        if len(axis) == 2:
            if periodic_extension:
                if ax == 1:
                    s = np.array((list(s)+list(s[:,::-1]))*periodic_extension)
                if ax == 0:
                    s = np.array((list(np.array(s).T)+list(np.array(s[::-1,:]).T))*periodic_extension).T
            shape = (axis[0]*2*periodic_extension+padding,axis[1]) if ax == 1 else (axis[0],axis[1]*2*periodic_extension+padding)
            data = np.zeros(shape)
            rows, cols = np.shape(s)
            print(shape)
            data[:rows,:cols] = s
        else:
            if periodic_extension:
                if ax == 0:
                    s = np.array((list(s)+list(s[::-1]))*periodic_extension)
            shape = (axis[0]*2*periodic_extension+padding,)
            data = np.zeros(shape)
            rows = len(s)
            data[:rows] = s
        return data
  
    def firstMax(self,x,y,num=0,peakpercent=0.9,insitu=False,mean=True,which='max'):
        """
        x:       线性扫描点
        insitu:  如果为True，截取peak值为x为num时对应的值乘以peakpercent，False为最大值乘以peakpercent
        """
        if which != 'max':
            y = np.abs(y-y.max())
        index0 = np.argmin(np.abs(x-num))
        y = y - np.min(y)
        peak = peakpercent*y[index0] if insitu else peakpercent*np.max(y)
        c = np.argwhere(y>peak)
        cdiff = np.diff(c[:,0])
        n_clusters = len(np.argwhere(cdiff>np.mean(cdiff))) + 1
        S = c[:,0]
        d = np.asarray(np.mat(list(zip(S,S))))

        kmeans = KMeans(n_clusters=n_clusters,max_iter=100,tol=0.001)
        yfit = kmeans.fit_predict(d)
        xaxis = S[yfit==yfit[np.argmin(np.abs(S-index0))]]
        index =  int(np.mean(xaxis)) if mean else int(xaxis[np.argmax(y[xaxis])])
        bias0 = round(x[index],5)
        return bias0 ,index

    def smooth(self,y,f0=0.1,axis=-1):
        b, a = signal.butter(3,f0)
        z = signal.filtfilt(b,a,y,axis=axis)
        return z

    def movingAverage(self,data,num2mean=5,ratio=1):
        x = np.exp(np.arange(num2mean))
        window = (x / np.sum(x))
    #     window = np.ones(num2mean)/num2mean
        ynew1 = np.convolve(data, window, 'same')
        ynew1[:num2mean] = data[:num2mean]
        ynew2 = np.convolve(data[::-1], window, 'same')
        ynew2[:num2mean] = data[::-1][:num2mean]
        ynew = (ynew1+ynew2[::-1])/2
        return ynew

    def resample(self,x,y,num=1001):
        down = len(x)
        up = num
        x_new = np.linspace(min(x),max(x),up)
        z = signal.resample_poly(y,up,down)
        return x_new, z

    def findPeaks(self,y,width=None,f0=0.015,h=0.15,threshold=None,prominence=None,plateau_size=None,rel_height=0):
        detrend = np.mean(y - signal.detrend(y))
        # mask = y > (np.max(y)+np.min(y))/2
        z = y if np.max(y)-detrend>detrend-np.min(y) else -y
        background = self.smooth(z,f0=f0)
        height0 = (np.max(z)-np.min(z))
        height = (background+h*height0,background+(1+h)*height0)
        threshold = threshold if threshold == None else threshold*height0
        property_peaks = signal.find_peaks(z,height=height,threshold=threshold,plateau_size=plateau_size)
        index = property_peaks[0]
        half_widths = signal.peak_widths(z,index,rel_height=rel_height)
        print(index,half_widths[0])
        # side = (index+int(half_widths[0]), index-int(half_widths[0]))
        side = 0
        prominence = signal.peak_prominences(z,index)
        return index, side, prominence
    
    def spectrum(self,x,y,method='normal',window='boxcar',detrend='constant',axis=-1,scaling='density',average='mean',shift=True):
        '''
        scaling:
            'density':power spectral density V**2/Hz
            'spcetrum': power spectrum V**2
        '''
        fs = (len(x)-1)/(np.max(x)-np.min(x))
        if method == 'normal':
            f, Pxx = signal.periodogram(y,fs,window=window,detrend=detrend,axis=axis,scaling=scaling)
        if method == 'welch':
            f, Pxx = signal.welch(y,fs,window=window,detrend=detrend,axis=axis,scaling=scaling,average=average)
        f, Pxx = (np.fft.fftshift(f), np.fft.fftshift(Pxx)) if shift else (f, Pxx)
        index = np.argmax(Pxx,axis=axis)
        w = f[index]
        return w, f, Pxx
    
    def cross_psd(self,x,y,z,window='hann',detrend='constant',scaling='density',axis=-1,average='mean'):
        fs = (len(x)-1)/(np.max(x)-np.min(x))
        f, Pxy = signal.csd(y,z,fs,window=window,detrend=detrend,scaling=scaling,axis=axis,average=average)
        return f, Pxy
    
    def ftspectrum(self,x,y,window='hann',detrend='constant',scaling='density',axis=-1,mode='psd'):
        '''
        mode:
            'psd':
            'complex':==stft
            'magnitude':==abs(stft)
            'angle':with unwrapping
            'phase':without unwraping
        '''
        fs = (len(x)-1)/(np.max(x)-np.min(x))
        f, t, Sxx = signal.spectrigram(y,fs,window=window,detrend=detrend,scaling=scaling,axis=axis,mode=mode)
        return f, t, Sxx
    
    def stft(self,x,y,window='hann',detrend=False,axis=-1,boundary='zeros',padded=True,nperseg=256):
        '''
        boundary:you can choose ['even','odd','constant','zeros',None]
        padded: True Or False          
        '''
        fs = (len(x)-1)/(np.max(x)-np.min(x))
        f, t, Zxx = signal.stft(y,fs,window=window,detrend=detrend,axis=axis,boundary=boundary,padded=padded,nperseg=nperseg)
        return f, t, Zxx
     
    def istft(self,x,Zxx,window='hann',boundary=True,time_axis=-1,freq_axis=-2):
        fs = (len(x)-1)/(np.max(x)-np.min(x))
        t, y = signal.stft(Zxx,fs,window=window,boundary=boundary,time_axis=time_axis,freq_axis=freq_axis)
        return t, y


    def fourier(self,x,y,axis=-1,detrend=True,zeroPadding=0,cycleExtension=1,window='boxcar',printinfo=False):
        '''

        x: linear time array or sample_rate
        y: 1d or 2d array 
        axis: FFT along the axis
        detrend: detrend the offset of y if True ,default True.
        zeroPadding: append zero for y along the axis
        cycleExtension: cycleExtend y along the axis
        window: str or tuple. Desired window to use. 
                it is passed to get_window to generate the window values, 
                which are DFT-even by default. See get_window for a list of 
                windows and required parameters. Defaults to a boxcar window.
        '''
        
        y = signal.detrend(y,axis=axis,type='constant') if detrend else y
        shape = list(np.shape(y))
        shape[axis] = zeroPadding
        
        window = signal.get_window(window,np.shape(y)[axis])  
        window = np.expand_dims(window,axis=axis-1).repeat(shape[axis-1],axis=axis-1) if len(shape)!=1 else window
        
        sample = (np.max(x) - np.min(x))/(len(x) - 1) if isinstance(x,Iterable) else x
        if printinfo:
            print(f'Computation resolution:{sample/np.shape(y)[axis]}')

        y0 = np.concatenate([y*window]*cycleExtension,axis=axis)

        ynew = np.concatenate([y0,np.zeros(shape)],axis=axis)
        if printinfo:
            print(f'Computation resolution after zeroPadding:{sample/(np.shape(ynew)[axis]-np.shape(y0)[axis]+np.shape(y)[axis])}')
            print(f'Computation resolution after resample:{sample/np.shape(ynew)[axis]}')

        yt  = np.fft.rfftfreq(np.shape(ynew)[axis],sample)
        amp = np.fft.rfft(ynew,axis=axis)
        w = np.abs(yt[np.argmax(np.abs(amp),axis=axis)])

        return w, yt, amp
        
    def envelope(self,y,responsetime=100):
        mold, out, rc = 0, [], responsetime
        out.append(np.abs(y[0]))
        for j, i in enumerate(y[1:],start=1):
            i = np.abs(i)
            if i > out[j-1]:
                mold = i
            else:
                mold = (out[j-1] * rc)/(rc + 1)
            out.append(mold)
        return out

    def envelope_Hilbert(self,y,axis=0):
        ym = signal.detrend(y,type='constant',axis=axis)
        yh = signal.hilbert(ym,axis=axis) 
        out = np.abs(ym + 1j*yh) + y.mean()
        return out

    def freq_Hilbert(self,x,y,axis=0):
        ym = signal.detrend(y,type='constant',axis=axis)
        yh = signal.hilbert(ym,axis=axis) 
        phase = np.unwrap(np.angle(ym+1j*yh))
        res, func = self.poly(x,phase,1)
        w = res[0]
        return w, phase, func

    def profile(self,v,f,s,peak,axis=1,classify=False):
        if classify:
            index = np.argwhere(np.abs(s)>peak)
            v = v[index[:,0]]
            f = f[index[:,1]]
        else:
            if axis == 1:
                v = v[np.abs(s).max(axis=1)>peak]
                s = s[np.abs(s).max(axis=1)>peak]
                f = f[np.abs(s).argmax(axis=1)]
            if axis == 0:
                f = f[np.abs(s).max(axis=0)>peak]
                s = s[:,np.abs(s).max(axis=0)>peak]
                v = v[np.abs(s).argmax(axis=0)]
        return v, f

    def profile1(self,v,f,s,peak,axis=1,classify=False):
        
        v = v[np.abs(s).max(axis=1)>peak]
        s = s[np.abs(s).max(axis=1)>peak]
        f = f[np.abs(s).argmax(axis=1)]
        if axis == 0:
            f = f[np.abs(s).max(axis=0)>peak]
            s = s[:,np.abs(s).max(axis=0)>peak]
            v = v[np.abs(s).argmax(axis=0)]
        return v, f

    def poly(self,x,y,num=1):
        z = np.polyfit(x, y, num)
        func = np.poly1d(z)
        return z, func

    def interp1d(self,x,y,kind='cubic',axis=-1, copy=True, bounds_error=None, fill_value=np.nan, assume_sorted=False):
        '''
        interp1d(x, y, kind='linear', axis=-1, copy=True, bounds_error=None, fill_value=nan, assume_sorted=False)
        |  
        |  Interpolate a 1-D function.
        |  
        |  `x` and `y` are arrays of values used to approximate some function f:
        |  ``y = f(x)``. This class returns a function whose call method uses
        |  interpolation to find the value of new points.
        |  
        |  Parameters
        |  ----------
        |  x : (N,) array_like
        |      A 1-D array of real values.
        |  y : (...,N,...) array_like
        |      A N-D array of real values. The length of `y` along the interpolation
        |      axis must be equal to the length of `x`.
        |  kind : str or int, optional
        |      Specifies the kind of interpolation as a string or as an integer
        |      specifying the order of the spline interpolator to use.
        |      The string has to be one of 'linear', 'nearest', 'nearest-up', 'zero',
        |      'slinear', 'quadratic', 'cubic', 'previous', or 'next'. 'zero',
        |      'slinear', 'quadratic' and 'cubic' refer to a spline interpolation of
        |      zeroth, first, second or third order; 'previous' and 'next' simply
        |      return the previous or next value of the point; 'nearest-up' and
        |      'nearest' differ when interpolating half-integers (e.g. 0.5, 1.5)
        |      in that 'nearest-up' rounds up and 'nearest' rounds down. Default
        |      is 'linear'.
        |  axis : int, optional
        |      Specifies the axis of `y` along which to interpolate.
        |      Interpolation defaults to the last axis of `y`.
        |  copy : bool, optional
        |      If True, the class makes internal copies of x and y.
        |      If False, references to `x` and `y` are used. The default is to copy.
        |  bounds_error : bool, optional
        |      If True, a ValueError is raised any time interpolation is attempted on
        |      a value outside of the range of x (where extrapolation is
        |      necessary). If False, out of bounds values are assigned `fill_value`.
        |      By default, an error is raised unless ``fill_value="extrapolate"``.
        |  fill_value : array-like or (array-like, array_like) or "extrapolate", optional
        |      - if a ndarray (or float), this value will be used to fill in for
        |        requested points outside of the data range. If not provided, then
        |        the default is NaN. The array-like must broadcast properly to the
        |        dimensions of the non-interpolation axes.
        |      - If a two-element tuple, then the first element is used as a
        |        fill value for ``x_new < x[0]`` and the second element is used for
        |        ``x_new > x[-1]``. Anything that is not a 2-element tuple (e.g.,
        |        list or ndarray, regardless of shape) is taken to be a single
        |        array-like argument meant to be used for both bounds as
        |        ``below, above = fill_value, fill_value``. Using a two-element tuple
        |        or ndarray requires ``bounds_error=False``.
        |  
        |        .. versionadded:: 0.17.0
        |      - If "extrapolate", then points outside the data range will be
        |        extrapolated.
        |  
        |        .. versionadded:: 0.17.0
        |  assume_sorted : bool, optional
        |      If False, values of `x` can be in any order and they are sorted first.
        |      If True, `x` has to be an array of monotonically increasing values.

        return 0, func_interp

        '''
        func = scipy.interpolate.interp1d(x,y,kind=kind,axis=axis, copy=copy, bounds_error=bounds_error, fill_value=fill_value, assume_sorted=assume_sorted)

        return 0, func

################################################################################
### 拟合Exp函数
################################################################################

class Exp_Fit(RowToRipe):
    
    def __init__(self,funcname=None):
        self.funcname = funcname

    def func(self,x,paras):

        if self.funcname == 'gauss':
            A, B, T1, T2 = paras
            return A * np.exp(-T2*x**2-x*T1) + B 
        else:
            A, B, T1 = paras
            return A * np.exp(-x*T1) + B 
    
    def errExp(self,paras, x, y):
        
        if self.funcname == 'gauss':
            return np.sum((self.func(x,paras) - y)**2)
        else:
            return np.sum((self.func(x,paras) - y)**2)

    def guessExp(self,x,y):
        ymin = y.min()
        y = y-y.min()
        mask = y > 0.05*y.max()
        if self.funcname == 'gauss':
            a = np.polyfit(x[mask], np.log(y[mask]), 2)
            return [np.exp(a[2]), ymin, -a[1], -a[0]]
        else:
            a = np.polyfit(x[mask], np.log(y[mask]), 1)
            return [np.exp(a[1]), ymin, -a[0]]

    def fitExp(self,x,y):
        p0 = self.guessExp(x,y)
        # res = ls(self.errExp, p0, args=(x, y)) 
        res = bh(self.errExp,p0,niter = 500,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)}) 
        return res, self.func
func_willBeused = {'Expfunc':Exp_Fit().func}
################################################################################
### 拟合Gaussian函数
################################################################################

class Gaussian_Fit(RowToRipe):
    
    def __init__(self):
        pass

    def func(self,x,paras):
        A, B, sigma, mu = paras
        return A/sigma/np.sqrt(2*np.pi)*np.exp(-(x-mu)**2/2/sigma**2) + B

    def errGaussian(self,paras, x, y,weight):
        return np.sum(weight*(self.func(x,paras) - y)**2)

    def errGaussian_ls(self,paras, x, y,weight):
        return weight*(self.func(x,paras) - y)

    def guessGaussian(self,x,y):
        background = np.mean(y - signal.detrend(y,type='constant'))
        height = (np.max(y)+np.min(y))/2
        B = y.min()
        mu = np.mean(x[y>height]) if y[len(y)//2] > background else np.mean(x[y<height])
        sigma = (np.max(x[y>height]) - np.min(x[y>height])) if y[len(y)//2] > background else (np.max(x[y<height]) - np.min(x[y<height])) 
        A = (np.max(y)-np.min(y))*sigma*np.sqrt(2*np.pi) if y[len(y)//2] > background else -(np.max(y)-np.min(y))*sigma*np.sqrt(2*np.pi)
        return [A, B, sigma,mu]

    def fitGaussian(self,x_old,y_old,correct=False,fine=True):
        l = len(y_old)
        reslst, cost = [], []
        idxLst, rLst = ([0,l//6,-l//6],[1,-1]) if fine else ([0],[1])
        for i in idxLst:
            x , y = (x_old[i:], y_old[i:]) if i >=0 else (x_old[:i], y_old[:i])
            for ratio in rLst:
                A, B, sigma, mu = self.guessGaussian(x,y)
                # weight = (self.func(x,(A,0,sigma,mu))/np.max(self.func(x,(A,0,sigma,mu))))**10
                weight = 1
                A *= ratio
                p0 = A, B, sigma, mu
                # print(p0)
                # mybounds = MyBounds(xmin=[-10,-10,-np.inf,-np.inf,-np.inf,-np.inf],xmax=[10,10,-np.inf,-np.inf,-np.inf,-np.inf])
                res = bh(self.errGaussian,p0,niter = 200,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y,weight)})    
                reslst.append(res)
                cost.append(res.fun)
        index = np.argmin(cost)
        if correct:
            res = ls(self.errGaussian_ls,reslst[index].x,args=(x_old, y_old,weight))
            return res, self.func
        else:
            return reslst[index], self.func

################################################################################
### 拟合双Gaussian函数
################################################################################

class Gaussian2_Fit(RowToRipe):
    
    def __init__(self):
        pass

    def func(self,x,paras):
        amp, mu, sigma = paras
        return np.sum(amp*np.exp(-(x[:,None]-mu)/2/sigma**2),axis=-1)

    def errGaussian(self,paras, x, y,weight):
        return np.sum(weight*(self.func(x,paras) - y)**2)

    def errGaussian_ls(self,paras, x, y,weight):
        return weight*(self.func(x,paras) - y)

    def guessGaussian(self,x,y):
        background = np.mean(y - signal.detrend(y,type='constant'))
        height = (np.max(y)+np.min(y))/2
        B = y.min()
        mu = np.mean(x[y>height]) if y[len(y)//2] > background else np.mean(x[y<height])
        sigma = (np.max(x[y>height]) - np.min(x[y>height])) if y[len(y)//2] > background else (np.max(x[y<height]) - np.min(x[y<height])) 
        A = (np.max(y)-np.min(y))*sigma*np.sqrt(2*np.pi) if y[len(y)//2] > background else -(np.max(y)-np.min(y))*sigma*np.sqrt(2*np.pi)
        return [A, B, sigma,mu]

    def fitGaussian(self,x_old,y_old,correct=False):
        l = len(y_old)
        reslst, cost = [], []
        for i in [0,l//6,-l//6]:
            x , y = (x_old[i:], y_old[i:]) if i >=0 else (x_old[:i], y_old[:i])
            for ratio in [1,-1]:
                A, B, sigma, mu = self.guessGaussian(x,y)
                # weight = (self.func(x,(A,0,sigma,mu))/np.max(self.func(x,(A,0,sigma,mu))))**10
                weight = 1
                A *= ratio
                p0 = A, B, sigma, mu
                # print(p0)
                # mybounds = MyBounds(xmin=[-10,-10,-np.inf,-np.inf,-np.inf,-np.inf],xmax=[10,10,-np.inf,-np.inf,-np.inf,-np.inf])
                res = bh(self.errGaussian,p0,niter = 200,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y,weight)})    
                reslst.append(res)
                cost.append(res.fun)
        index = np.argmin(cost)
        if correct:
            res = ls(self.errGaussian_ls,reslst[index].x,args=(x_old, y_old,weight))
            return res, self.func
        else:
            return reslst[index], self.func

################################################################################
### 拟合Cos函数
################################################################################

class Cos_Fit(RowToRipe):

    def __init__(self,phi=None):
        self.phi = phi
        pass

    def func(self,x,paras):
        A,C,W,phi = paras  
        return A*np.cos(2*np.pi*W*x+phi)+C

    def errCos(self,paras,x,y,kind):      
        if kind == 'bh':       
            return  np.sum((self.func(x,paras)-y)**2)  
        if kind == 'ls':
            return self.func(x,paras) - y

    def guessCos(self,x,y):
        x, y = np.array(x), np.array(y)
        # sample = (np.max(x) - np.min(x))/(len(x) - 1)
        Ag, Cg= np.abs(y-np.mean(y)).max(), np.mean(y) 
        # yt  = np.fft.fftshift(np.fft.fftfreq(len(y))) / sample
        # amp = np.fft.fftshift(np.fft.fft(y))
        Wg,yt,amp = RowToRipe().fourier(x, y)
        z = np.abs(amp[yt!=0])
        ytz = yt[yt!=0]
        # Wg = np.abs(ytz[np.argmax(z)])
        phig =  np.mean(np.arccos((y - Cg)/Ag) - 2*np.pi*Wg*x) % (2*np.pi)
        return Ag, Cg, Wg, 0

    def fitCos(self,volt,s):
        x, y = volt, s
        if x[0] / 1e9 > 1:
            raise 'I hate the large number, please divided by 1e9, processing x in GHz'
        Ag, Cg, Wg, phig = self.guessCos(x,y)
        phig = phig if self.phi is None else self.phi
        p0 = Ag, Cg, Wg, phig
        # print(Ag, Cg, Wg, phig)
        # res = ls(self.errCos, [Ag,Cg,Wg,phig], args=(x, y)) 
        mybounds = MyBounds(xmin=[-np.inf,-np.inf,0,-np.pi],xmax=[np.inf,np.inf,1.5*Wg,np.pi])    
        res = bh(self.errCos,p0,niter=80,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y,'bh')},accept_test=mybounds)   
        res = ls(self.errCos, res.x, args=(x, y,'ls')) 

        return res, self.func

################################################################################
### 拟合洛伦兹函数
################################################################################

class Lorentz_Fit(RowToRipe):
    '''
    I hate the large number
    processing x in GHz
    '''
    def __init__(self):
        pass

    def func(self,x,paras):
        a,b,c,d = paras
        return a/(1.0+c*(x-b)**2)+d

    def errLorentz(self,paras,x,y):
        return np.sum((self.func(x,paras)-y)**2)

    def guessLorentz(self,x,y):
        # index, prominences, widths = self.findPeaks(y)
        z = np.sort(np.abs(y))
        d = np.mean(z[:int(len(z)/2)])
        y = np.abs(y)- d
        b = x[np.abs(y).argmax()]
        # b1, b = x[index]
        bw = (np.max(x[y>0.5*(np.max(y)-np.min(y))])-np.min(x[y>0.5*(np.max(y)-np.min(y))]))/2
        # bw1, bw = widths
        a = np.abs(y).max()
        # a1, a = prominences
        c = 1 / bw**2
        return a,b,c,d

    def fitLorentz(self,x,y):
        if x[0] / 1e9 > 1:
            raise 'I hate the large number, please divided by 1e9, processing x in GHz'
        para = self.guessLorentz(x,y)
        # mybounds = MyBounds(xmin=[-np.inf,-np.inf,-np.inf,-np.inf,0,0],xmax=[np.inf,np.inf,np.inf,np.inf,1.5*w,2*np.pi])    
        res = bh(self.errLorentz,para,niter=20,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)})
        # res = ls(self.errLorentz,para,args=(x,y))
        a,b,c,d = res.x
        return res,self.func,np.sqrt(np.abs(1/c))*2e3

################################################################################
### 拟合T1
################################################################################

class T1_Fit():
    "A, T1"
    def __init__(self,T1_limt=100e3):
        self.T1_limt = T1_limt
    
    def func(self,x,paras):
        A, T1,B = paras
        f = A * np.exp(-x/T1) +B
        return f

    def errT1(self,paras, x, y):
        return np.sum((self.func(x,paras) - y)**2)

    def errT1_ls(self,paras, x, y):
        return self.func(x,paras) - y

    def errT1_cf(self,x,A, T1,B):
        paras = A, T1,B
        return self.func(x,paras) 

    def guessT1(self,x,y):
        y = y/y.max()
        y = RowToRipe().smooth(y,f0=0.25)
        B = y.min()
        y = y-y.min()
        # mask = y > y.min()
        a = np.polyfit(x, np.log(y), 1)
        T1 = np.abs(1/a[0]) if np.abs(1/a[0]) < self.T1_limt else 0.99*self.T1_limt
        A = np.exp(a[1]) if np.exp(a[1]) > 0.95 and np.exp(a[1])<1.1 else 1
        # A, T1, B = 1,x[np.abs(y-np.exp(-1))<0.1][0], 0
        return [A, T1,B]

    def fitT1(self,x,y,s=None):
        """[fit T1 or 2d-T1]

        Args:
            x ([1d-array]): [if s is None,x is time, else voltage or frequency of qubit in 2d-T1]
            y ([1d-array]): [if s is None,y is population of |1>, else time in 2d-T1]
            s ([2d-array]): [population of |1>]. Defaults to None.

        Returns:
            [res, func]: [if s is None]
            [res_lst]: [if s is not None]
        """
        if s is None:
            p0 = self.guessT1(x,y)
            print(p0)
            mybounds = MyBounds(xmin=[0.95,0,0],xmax=[1.1,self.T1_limt,0.25])    
            res = bh(self.errT1,p0,niter = 50,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds) 
            return res,self.func,0
            # res = ls(self.errT1_ls,p0,args=(x,y))
            # popt,pcov = curve_fit(self.errT1_cf,x,y,p0,bounds=([0.95,0,0],[1.1,self.T1_limt,0.25]))
            # return popt, self.func, np.sqrt(np.diag(pcov))
        else:
            T1_lst = []
            pcov_lst = []
            for i in range(len(x)):
                p0 = self.guessT1(y,s[i,:])
                mybounds = MyBounds(xmin=[0.95,0,0],xmax=[1.1,self.T1_limt,0.25])    
                res = bh(self.errT1,p0,niter = 50,minimizer_kwargs={"method":"Nelder-Mead","args":(y,s[i,:])},accept_test=mybounds) 
                T1_lst.append(res.x[1])
                pcov_lst.append(res.fun)
                # res = ls(self.errT1_ls,p0,args=(y,s[i,:]))
                # popt,pcov = curve_fit(self.errT1_cf,y,s[i,:],p0,bounds=([0.95,0,0],[1.1,self.T1_limt,0.25]))
                # T1_lst.append(popt[1])
                # pcov_lst.append(np.sqrt(np.diag(pcov)))
            return T1_lst, pcov_lst

################################################################################
### 拟合指数包络函数
################################################################################

class T2_Fit(Exp_Fit,Cos_Fit):
    '''
    #############
    example:
    import imp
    import optimize
    op = imp.reload(optimize)
    try: 
        fT2 = op.T2_Fit(funcname='gauss',envelopemethod='hilbert')
        A,B,T1,T2,w,phi = fT2.fitT2(t,y)
    finally:
        pass
    ##############
    '''
    def __init__(self,responsetime=100,T1=35000,phi=0,funcname=None,envelopemethod=None):
        Exp_Fit.__init__(self,funcname)
        self.responsetime = responsetime
        self.T1 = T1
        self.phi = phi
        self.envelopemethod = envelopemethod
    
    def guessT2(self,x,y_new,y):
 
        res, _ = self.fitExp(x[5:-5],y_new[5:-5])
        A, B, T1, T2 = res.x
        T1 = 1 / T1 / 2
        if self.T1 is not None:
            T1 = self.T1
        Ag, Cg, Wg, phig = self.guessCos(x,y)
        return A, B, T1, np.sqrt(np.abs(1/T2)), Wg, phig

    def func_T2(self,x,para):
        A,B,T1,T2,w,phi = para
        return A*np.exp(-(x/T2)**2-x/T1/2)*np.cos(2*np.pi*w*x+phi) + B

    def errT2(self,para,x,y):
        return np.sum((self.func_T2(x,para) - y)**2)

    def fitT2(self,x,y):
        '''
        几个参数的限制范围还需要考究，A，T1，T2
        '''
        d = self.space(y)
        if self.envelopemethod == 'hilbert':
            out = self.envelope_Hilbert(y)
        else:
            out = self.envelope(y)
        A,B,T1,T2,w,phi = self.guessT2(x,out,y)
        env = A,B,T1,T2,out
        if T2 > 0.8*x[d-1] and d < 0.8*len(y):
            T2 = 0.37*x[d-1]
        amp = (np.max(y)-np.min(y)) / 2
        A = A if np.abs(A-amp) < 0.1*amp else amp
        p0 = A,B,T1,T2,w,self.phi
        print(p0)
        # res = ls(self.errT2, p0, args=(x, y)) 
        mybounds = MyBounds(xmin=[0,-np.inf,0,0,0,-np.pi],xmax=[np.inf,np.inf,100000,100000,1.5*w,np.pi])    
        res = bh(self.errT2,p0,niter = 80,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds)     
        A,B,T1,T2,w,phi = res.x
        return res, self.func_T2

class T2Envelope_Fit(Exp_Fit,Cos_Fit):
    '''
    #############
    example:
    import imp
    import optimize
    op = imp.reload(optimize)
    try: 
        fT2 = op.T2_Fit(funcname='gauss',envelopemethod='hilbert')
        A,B,T1,T2,w,phi = fT2.fitT2(t,y)
    finally:
        pass
    ##############
    '''
    def __init__(self,funcname=None):
        Exp_Fit.__init__(self,funcname)
    
    def guessT2Envelope(self,x,y):
 
        res, _ = self.fitExp(x,y)
        A, B, T1, T2 = res.x
        T1 = 1 / T1 / 2
        return A, B, T1, np.sqrt(np.abs(1/T2))

    def func_T2Envelope(self,x,para):
        A,B,T1,T2 = para
        return A*np.exp(-(x/T2)**2-x/T1/2) + B

    def errT2Envelope(self,para,x,y):
        return np.sum((self.func_T2Envelope(x,para) - y)**2)

    def fitT2Envelope(self,x,y):
        '''
        几个参数的限制范围还需要考究，A，T1，T2
        '''
        A,B,T1,T2 = self.guessT2Envelope(x,y)
        # env = A,B,T1,T2,out
        # if T2 > 0.8*x[d-1] and d < 0.8*len(y):
        #     T2 = 0.37*x[d-1]
        # amp = (np.max(y)-np.min(y)) / 2
        # A = A if np.abs(A-amp) < 0.1*amp else amp
        p0 = A,B,T1,T2
        print(p0)
        # res = ls(self.errT2, p0, args=(x, y)) 
        mybounds = MyBounds(xmin=[0,-np.inf,0,0],xmax=[np.inf,np.inf,100000,100000])    
        res = bh(self.errT2Envelope,p0,niter = 80,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds)     
        A,B,T1,T2 = res.x
        return res, self.func_T2Envelope

class Rabi_Fit(T2_Fit):

    def __init__(self,responsetime=100,T1=20000,phi=np.pi/2,funcname=None,envelopemethod=None):
        T2_Fit.__init__(self,responsetime,T1,phi,funcname,envelopemethod)
        
    
    def guessRabi(self,x,y_new,y):
 
        res, _ = self.fitExp(x[5:-5],y_new[5:-5])
        A, B, T1 = res.x
        T1 = 1 / T1
        if self.T1 is not None:
            T1 = self.T1
        Ag, Cg, Wg, phig = self.guessCos(x,y)
        return A, B, T1, Wg, phig
    
    def func_Rabi(self,x,paras):
        A,B,T1,w,phi = paras
        return A*np.exp(-x/T1)*np.cos(2*np.pi*w*x+phi) + B

    def errRabi(self,paras,x,y):
        
        return np.sum((self.func_Rabi(x,paras) - y)**2)

    def fitRabi(self,x,y):
        if self.envelopemethod == 'hilbert':
            out = self.envelope_Hilbert(y)
        else:
            out = self.envelope(y)
        A,B,T1,w,phi = self.guessRabi(x,out,y)
        env = (A,B,T1,out)
        amp = (np.max(y)-np.min(y)) / 2
        A = A if np.abs(A-amp) < 0.1*amp else amp
        B = B if np.abs(B-np.mean(y)) < 0.1*np.mean(y) else np.mean(y)
        p0 = A,B,T1,w,self.phi
        print(p0)
        # res = ls(self.errRabi, p0, args=(np.array(x), np.array(y)))   
        mybounds = MyBounds(xmin=[0,-np.inf,100,0,0],xmax=[np.inf,np.inf,100e3,1.5*w,2*np.pi])
        res = bh(self.errRabi,p0,niter=30,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds)      
        A,B,T1,w,phi = res.x
        return res, self.func_Rabi

################################################################################
### 拟合二维谱
################################################################################

class Spec2d_Fit(Cos_Fit):

    def __init__(self,peak=15,threshold=0.001):
        Cos_Fit.__init__(self,phi=None)
        self.peak = peak
        self.threshold = threshold
    
    def profile(self,v,f,s,classify=False):
        if classify:
            index = np.argwhere(s>self.peak)
            v = v[index[:,0]]
            f = f[index[:,1]]
        else:
            v = v[s.max(axis=1)>self.peak]
            # s = s[s.max(axis=1)>self.peak]
            # f = f[s.argmax(axis=1)]
            idx = s > self.peak
            f = [f[i][-1] for i in idx if np.any(i) == True]
        return v, np.array(f)
    def func_f01(self,x,paras):
        voffset, vperiod, ejs, ec, d = paras
        tmp = np.pi*(x-voffset)/vperiod
        f01 = np.sqrt(8*ejs*ec*np.abs(np.cos(tmp))*np.sqrt(1+d**2*np.tan(tmp)**2))-ec
        return f01
    def err(self,paras,x,y):
        # A, C, w, phi = paras
        # f01 = np.sqrt(A*np.abs(np.cos(w*x+phi))) + C
        f01 = self.func_f01(x,paras)
        return np.sum((f01 - y)**2)

    def fitSpec2d(self,v,f,s=None,classify=False):
        if s is not None:
            v,f = self.profile(v,f,s,classify)
            # print(list(v),list(f))
        paras, func = self.fitCos(v,f)
        A, C, W, phi = paras.x
        try:
            voffset = self.firstMax(v,f,num=0)[0]
        except:
            voffset  =  v[np.argmax(f)]
        vperiod, ec, d = 1/W, 0.2, 0.5
        ejs = (np.max(f)+ec)**2/8/ec
        p0 = [voffset, vperiod,ejs,ec,d]
        res, func = self.poly(v,f,2)
        space = np.abs(func(v)-f)
        if np.max(space) > self.threshold:
            # print(space)
            v = v[space<self.threshold]
            f = f[space<self.threshold]

        while 1:
            print(p0)
            # print(list(v),list(f))
            mybounds = MyBounds(xmin=[0.5*voffset,0,0,0,0],xmax=[1.5*voffset,1.5*vperiod,2*ejs,2*ec,1000])
            res = bh(self.err,p0,niter = 200,minimizer_kwargs={"method":"Nelder-Mead","args":(v, f)},accept_test=mybounds) 
            # res = ls(self.err,res.x,args=(v, f)) 
            voffset, vperiod, ejs, ec, d = res.x
            space = self.errspace(self.func_f01,res.x,{'x':v,'y':f})
            if np.max(space) > self.threshold:
                # print(space)
                v = v[space<self.threshold]
                f = f[space<self.threshold]
                p0 = res.x
                # print(len(v),(space<0.001))
            else:
                return f, v, res, self.func_f01
        # return f, v, voffset, vperiod, ejs, ec, d

################################################################################
### 拟合腔频调制曲线
################################################################################

class Cavitymodulation_Fit(Spec2d_Fit):

    def __init__(self,peak=15,phi=None):
        Cos_Fit.__init__(self,phi=phi)
        self.peak = peak

    def func_s(self,x,paras):
        voffset, vperiod, ejs, ec, d, g, fc = paras
        tmp = np.pi*(x-voffset)/vperiod
        f01 = np.sqrt(8*ejs*ec*np.abs(np.cos(tmp))*np.sqrt(1+d**2*np.tan(tmp)**2))-ec
        fr = (fc+f01+np.sqrt(4*g**2+(f01-fc)**2))/2
        # fr = fc - g**2/(f01-fc)
        return fr

    def err(self,paras,x,y):
        return np.sum((self.func_s(x,paras) - y)**2)

    def fitCavitymodulation(self,v,f,s,classify=False):
        v,f = self.manipulation(v,f,s)
        paras, func = self.fitCos(v,f)
        A, C, W, phi = paras.x
        voffset, vperiod, ec, d= self.firstMax(v,f,num=0), 1/W, 0.1*np.min(f), 1
        # g = np.min(f)-fc
        ejs = (np.max(f)+ec)**2/8/ec
        g, fc = ec, np.mean(f)
        p0 = [voffset, vperiod, ejs, ec, d, g, fc]
        print(p0)
        mybounds = MyBounds(xmin=[-0.25*vperiod,0,0,0,0,0,0],xmax=[0.25*vperiod,1.5*vperiod,2*ejs,2*ec,2,2*g,2*fc])
        res = bh(self.err,p0,niter = 200,minimizer_kwargs={"method":"Nelder-Mead","args":(v, f)},accept_test=mybounds)
        # res = ls(self.err,res.x,args=(v, f)) 
        # A, C, W, phi = res.x
        voffset, vperiod, ejs, ec, d, g, fc = res.x
        return f, v, res, self.func_s

################################################################################
### crosstalk直线拟合
################################################################################

class Crosstalk_Fit(Spec2d_Fit):

    def __init__(self,peak=15):
        self.peak = peak

    def two_line(self,f,v):
        fv = []
        for i,j in enumerate(f):
            fv.append([j,v[i]])
        fv = sorted(fv)
        ff = sorted(list(Counter(f).keys()))
        F = [0]*len(ff)
        for i,j in enumerate(ff):
            F_m=[]
            for k,l in enumerate(fv):
                if j==l[0]:
                    F_m.append(l[1])
            F[i]=sorted(F_m )

            
        FF_1 = [0]*len(F)
        FF_2 = [0]*len(F)
        FF_m = [0]*len(F)
        for k,i in enumerate(F):
            F_1 = []
            F_2 = []
            for j in i:
                if j<i[-1]-0.05:
                    F_2.append(j)
                else:
                    F_1.append(j)
            if len(F_2)==len(i):
                FF_m[k]=F_2.copy()
                F_2 = []
            if len(F_1)==len(i):
                FF_m[k]=F_1.copy()
                F_1 = []
                
            FF_1[k] = F_1
            FF_2[k] = F_2

        vm=[]
        for j, i in enumerate(FF_m):
            if i==0:
                vm.append(j)

        FF_m1 = (FF_m[:vm[0]])
        v_m1 = (ff[:vm[0]])
        FF_m2 = (FF_m[vm[-1]+1:])
        v_m2 = (ff[vm[-1]+1:])
                
        c1=[]
        v1=[]
        for j, i in enumerate(FF_1):
            c1+=len(i)*[1*ff[j]]
            v1+=i
            
        c2=[]
        v2=[]
        for j, i in enumerate(FF_2):
            c2+=len(i)*[1*ff[j]]
            v2+=i


        cm1=[]
        vm1=[]
        for j, i in enumerate(FF_m1):
            cm1+=len(i)*[1*v_m1[j]]
            vm1+=i
            
        cm2=[]
        vm2=[]
        for j, i in enumerate(FF_m2):
            cm2+=len(i)*[1*v_m2[j]]
            vm2+=i


        p1 = np.array([np.polyfit(c1, v1 ,1)[1],np.polyfit(c2, v2 ,1)[1]])-np.polyfit(cm1, vm1 ,1)[1]
        p2 = np.array([np.polyfit(c1, v1 ,1)[1],np.polyfit(c2, v2 ,1)[1]])-np.polyfit(cm2, vm2 ,1)[1]

        if abs(p2[1])<abs(p2[0]):
            v2+=vm2
            c2+=cm2
        if abs(p2[1])>abs(p2[0]):
            v1+=vm2
            c1+=cm2

        if abs(p1[1])<abs(p1[0]):
            v2+=vm1
            c2+=cm1
        if abs(p1[1])>abs(p1[0]):
            v1+=vm1
            c1+=cm1
        return v1,c1,v2,c2
        
    def fitCrosstalk(self,v,f,s,classify=False):
        v,f = self.profile(v,f,s,classify)
        res = np.polyfit(f,v,1)
        return v, f, res

################################################################################
### 单比特tomo
################################################################################

def pTorho(plist):
    pz_list, px_list, py_list = plist
    rho_list = []
    for i in range(np.shape(pz_list)[0]):
        pop_z, pop_x, pop_y = pz_list.T[i], px_list.T[i], py_list.T[i]
        rho_00, rho_01 = 1 - pop_z, (2*pop_x - 2j*pop_y - 1 + 1j) / 2j
        rho_10, rho_11 = (1 + 1j - 2*pop_x - 2j*pop_y) / 2j, pop_z
        rho = np.array([[rho_00,rho_01],[rho_10,rho_11]])
        rho_list.append(rho)
    pass

################################################################################
### RB
################################################################################

class RB_Fit:
    def __init__(self):
        pass
    def func_rb(self,x,paras):
        A,B,p = paras
        return A*p**x+B
    def err(self,paras,x,y):
        return self.func_rb(x,paras)-y
    def guess(self,x,y):
        B = np.min(y)
        y = y - np.min(y)
        mask = y > 0
        a = np.polyfit(x[mask], np.log(y[mask]), 1)
        return np.exp(np.abs(a[1])), B, 1/np.exp(np.abs(a[0]))
    def fitRB(self,x,y):
        p0 = self.guess(x,y)
        res = ls(self.err, p0, args=(x, y)) 
        A,B,p = res.x
        return res, self.func_rb

################################################################################
### 双指数拟合
################################################################################

# class TwoExp_Fit(Exp_Fit):
#     def __init__(self,funcname=None,percent=0.2):
#         Exp_Fit.__init__(self,funcname)
#         self.percent = percent
#     def err(self,paras,x,y):
#         a, b, c, d, e = paras
#         return np.sum((a*np.exp(b*x) + c*np.exp(d*x) + e - y)**2)
#     def guess(self,x,y):
#         a,e,b = self.fitExp(x,y)
#         b *= -1
#         e = np.min(y) if a > 0 else np.max(y)
#         return a,b,a*self.percent,b*self.percent,e
#     def fitTwoexp(self,x,y):
#         p0 = self.guess(x,y)
#         a, b, c, d, e = p0
#         lower = [0.95*i if i > 0 else 1.05*i for i in p0]
#         higher = [1.05*i if i > 0 else 0.95*i for i in p0]
#         lower[2], lower[3] = -np.abs(a)*self.percent, -np.abs(b)*self.percent
#         higher[2], higher[3] = self.percent*np.abs(a), self.percent*np.abs(b)
#         print(p0)
#         # res = ls(self.err,p0,args=(x,y),bounds=(lower,higher))
#         res = bh(self.err,p0,niter = 50,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)})

#         return res.x

class TwoExp_Fit(Exp_Fit):
    def __init__(self,funcname=None,percent=0.2):
        Exp_Fit.__init__(self,funcname)
        self.percent = percent
    def fitfunc(self,x,p):
        return (p[0] + np.sum(p[1::2,None]*np.exp(-p[2::2,None]*x[None,:]), axis=0))
    def err(self,paras,x,y):
        return np.sum(((self.fitfunc(x,paras) - y)*(1.0+0.5*scipy.special.erf(0.4*(x-paras[2])))**5)**2)
    def guess(self,x,y,paras):
        offset = np.min(y)
        alist = np.max(y) - np.min(y)
        blist = np.max(x)-np.min(x)
        paras[0] = offset
        paras[1::2] = alist
        paras[2::2] = 1/blist
        return paras
    def fitTwoexp(self,x,y,num=2):
        paras = np.zeros((2*num+1,))
        xmin, xmax = np.zeros((2*num+1,)), np.zeros((2*num+1,))
        p0 = self.guess(x,y,paras)
        xmin[0], xmax[0] = p0[0]*0.5, p0[0]*1.5
        xmin[1::2], xmin[2::2] = p0[1::2]*0.5, -(np.max(x)-np.min(x))*2
        xmax[1::2], xmax[2::2] = p0[1::2]*1.5, (np.max(x)-np.min(x))*2
        mybounds = MyBounds(xmin=xmin,xmax=xmax)
        res = bh(self.err,p0,niter = 50,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)})
        # res = bh(self.err,res.x,niter = 50,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds)
        p0 = res.x
        print(xmin)
        # res = ls(self.err, p0, args=(np.array(x), np.array(y)))  
        return res.x

################################################################################
## 误差函数拟合
################################################################################

class Erf_fit(RowToRipe):
    def __init__(self):
        RowToRipe.__init__(self)
    def func(self,x,paras):
        sigma1, sigma2, center1, center2, a, b = paras
        return a*(scipy.special.erf((x-center1)/sigma1)+np.abs(scipy.special.erf((x-center2)/sigma2)-1))+b
    def err(self,paras,x,y):
        return np.sum((y-self.func(x,paras))**2)
    def guess(self,x,y):
        height = np.max(y) - np.min(y)
        mask = x[y < (np.max(y)+np.min(y))/2]
        center1, center2 = mask[-1], mask[0]
        b = np.mean(y - signal.detrend(y,type='constant'))
        a = (np.max(y) - np.min(y)) if y[len(y)//2] < np.mean(y) else -(np.max(y) - np.min(y))
        z, ynew = x[(np.min(y)+0.1*height)<y], y[(np.min(y)+0.1*height)<y]
        z = z[ynew<(np.max(ynew)-0.2*height)]
        sigma2 = (z[z<np.mean(z)][-1]-z[z<np.mean(z)][0])
        sigma1 = (z[z>np.mean(z)][-1]-z[z>np.mean(z)][0])
        return sigma1, sigma2, center1, center2, a, b
    def fitErf(self,x,y):
        l = len(y)
        reslst, cost = [], []
        for i in [0,l//6,-l//6]:
            x , y = (x[i:], y[i:]) if i >=0 else (x[:i], y[:i])
            for ratio in [1,-1]:
                sigma1, sigma2, center1, center2, a, b = self.guess(x,y)
                a *= ratio
                paras = sigma1, sigma2, center1, center2, a, b
                print(paras)
                # mybounds = MyBounds(xmin=[-10,-10,-np.inf,-np.inf,-np.inf,-np.inf],xmax=[10,10,-np.inf,-np.inf,-np.inf,-np.inf])
                res = bh(self.err,paras,niter = 100,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)}) 
                reslst.append(res)
                cost.append(res.fun)
        index = np.argmin(cost)
        return reslst[index], self.func

################################################################################
## 拟合单个误差函数
################################################################################

class singleErf_fit(RowToRipe):
    def __init__(self):
        RowToRipe.__init__(self)
    def func(self,x,paras):
        sigma1, center1, a, b = paras
        return a*scipy.special.erf((x-center1)/sigma1)+b
    def err(self,paras,x,y):
        return np.sum((y-self.func(x,paras))**2)
    def guess(self,x,y):
        mask = x[y < y.mean()]
        center1 = mask[-1]
        b = np.mean(y - signal.detrend(y))
        a = np.max(y) - np.min(y)
        z = np.abs(y - np.mean(y))
        xnew = x[z<(np.max(z)+np.min(z))/2]
        sigma1 = xnew[-1] - xnew[0]
        return sigma1, center1, a, b
    def fitErf(self,x,y):
        l = len(y)
        reslst, cost = [], []
        for i in [0,l//6,-l//6]:
            x , y = (x[i:], y[i:]) if i >=0 else (x[:i], y[:i])
            for ratio in [1,-1]:
                sigma1, center1, a, b = self.guess(x,y)
                a *= ratio
                paras = sigma1, center1, a, b
                # print(paras)
                res = bh(self.err,paras,niter = 100,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)}) 
                reslst.append(res)
                cost.append(res.fun)
        index = np.argmin(cost)
        return reslst[index], self.func

################################################################################
## 拟合圆
################################################################################

class Circle_Fit():
    def __init__(self):
        pass
    def func(self,paras):
        xc, yc, R = paras
        theta = np.linspace(0,2*np.pi,1001)
        x = R*np.cos(theta) + xc
        y = R*np.sin(theta) + yc
        return x, y
    def errfunc(self,paras,x,y):
        xc, yc, R = paras
        return (x - xc)**2 + (y - yc)**2 - R**2
    def guess(self,x,y):
        xc = (np.max(x)+np.min(x))/2
        yc = (np.max(y)+np.min(y))/2
        R = np.sqrt((x-xc)**2+(y-yc)**2)
        return xc, yc, np.mean(R)
    def fitCircle(self,x,y):
        p0 = self.guess(x,y)
        res = ls(self.errfunc,p0,args=(x,y)) 
        return res, self.func

################################################################################
## 拟合贝塞尔函数绝对值
################################################################################

class Bessel_fit(RowToRipe):
    def __init__(self):
        RowToRipe.__init__(self)
    def func(self,x,paras):
        alpha, a = paras
        return a*np.abs(scipy.special.jv(0,alpha*x))
    def err(self,paras,x,y,kind='bh'):
        if kind == 'bh':
            return np.sum((y-self.func(x,paras))**2)
        if kind == 'ls':
            return y-self.func(x,paras)
    def guess(self,x,y):
        b = np.min(y)
        a = np.max(y)
        alpha = 2.4048/x[np.argmin(y)]
        return alpha, a
    def fitBessel(self,x,y):

        paras = self.guess(x,y)
        print(paras)
        # res = bh(self.err,paras,niter = 100,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)}) 
        # return res, self.func
        while 1:
            # print(p0)
            res = bh(self.err,paras,niter = 100,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y,'bh')}) 
            res = ls(self.err,res.x,args=(x,y,'ls')) 
            # space = self.errspace(self.func,res.x,{'x':x,'y':y})
            # if np.max(space) > 0.001:
            #     x = x[space<0.001]
            #     y = y[space<0.001]
            #     paras = res.x
                # print(len(v),(space<0.001))
            # else:
            return res, self.func

################################################################################
## 拟合zPulse核函数
################################################################################

# class zKernel_fit(RowToRipe):
#     def __init__(self,timeconstants =0,polyNum = 17,tCut = 90,height = 0.9,sigma = 0.4,tstart = 0,tshift = 0,polyRatio = 1,expNum = 1,tCut1 = 0):
#         self.polyNum = 17 #10  polyNum阶多项式拟合
#         self.expNum = 1 #######################目前固定为1,多项式拟合时的指数
#         self.timeconstants =0 # expNum阶指数拟合
#         self.tCut = 90#100 ,200  polyNUm的拟合范围
#         self.tCut1 = 0
#         self.tshift = 0
#         # self.height = eval(tags[1])
#         self.height = 0.9

#         self.polyRatio = 1
#         self.sigma = 0.4
#         self.tstart = 0

#     def fitfunc(t, p):
#         return (t >= 0) * ( np.sum(p[1::2,None]*(np.exp(-p[2::2,None]*(t[None,:]+tp))-np.exp(-p[2::2,None]*t[None,:]))/p[2::2,None], axis=0)) 
#     def errfunc(p,t,phi):
#         return (fitfunc(t, p)* height * diff_height -phi )*(1.0+0.5*scipy.special.erf(0.4*(t-buffer)))**10

#     def err(p,t,phi):
#         return np.sum(errfunc(p,t,phi)**2)

#     p0 = np.zeros(2*timeconstants+1)
#     p0[1::2] = -np.linspace(0, 0.02, timeconstants)
#     p0[2::2] = np.linspace(0, 0.5, timeconstants)
#     # print(p0)
#     p, _ = scipy.optimize.leastsq(errfunc,p0,maxfev=5000)
#     ts = np.arange(0,data[-1,0]*5,0.02)
#     p[0] = 0

#     plt.figure()
#     plt.subplot(211)
#     plt.plot(data[:,0],data[:,1],'bo')
#     plt.plot(ts,fitfunc(ts,p),'k-')

#     data1 = np.copy(data)
#     restData = data[:,1]-fitfunc(data[:,0], p)
#     restData = restData[data1[:,0]<=tCut]
#     data1 = data1[data1[:,0]<=tCut,:]
#     def fitfunc1(t, p):
#         pExp = p[:expNum*2]
#         pPoly = p[expNum*2:]
#         if np.iterable(t):
#             return np.sum(pExp[0::2,None]*np.exp(-pExp[1::2,None]*t[None,:]), axis=0)*np.polyval(pPoly,t)*(t<=tCut+20)
#         else:
#             return np.sum(pExp[0::2]*np.exp(-pExp[1::2]*t))*np.polyval(pPoly,t)*(t<=tCut)
#     def errfunc1(p):
#         return (fitfunc1(data1[:,0], p) - restData)
#     def smoothFuncATtCut(ts,tCut,tshift):    
#         return (0.5-0.5*scipy.special.erf(sigma*(ts-tCut+tshift)))*(0.5+0.5*scipy.special.erf(4.0*(ts-data[0,0]+0.5)))
#     pExp0 = np.zeros(2*expNum)
#     pExp0[1::2] = np.linspace(0.001, 0.03, expNum)
#     pPoly0 = np.zeros(polyNum)
#     pPoly0[-1] = 1.0
#     pAll0 = np.hstack([pExp0,pPoly0])
#     p2, _ = scipy.optimize.leastsq(errfunc1, pAll0)
#     smoothData = fitfunc1(ts,p2)*smoothFuncATtCut(ts,tCut,tshift)*polyRatio
#     timeFunData0 = smoothData+fitfunc(ts,p)
#     paras= {'p':p,'p2':p2,'tCut':tCut,'tshift':tshift,'sigma':sigma}
#     plt.subplot(212)
#     plt.plot(data1[:,0],restData,'bo')
#     # plt.plot(ts,smoothData,'r-')
#     plt.plot(ts,fitfunc1(ts,p2))
#     plt.xlabel('Time (ns)')
#     plt.grid(True)
#     plt.subplot(211)
#     plt.plot(ts,timeFunData0,'r-')
#     plt.grid(True)
#     p2 = np.asarray(p2)
#     p = np.asarray(p)
#     p_uniform = np.copy(p)
#     p2_uniform = np.copy(p2)
#     p_uniform[1::2] = p_uniform[1::2]/height
#     pExp = p2_uniform[:expNum*2]
#     pPoly = p2_uniform[expNum*2:]
#     pExp[0::2] = pExp[0::2]/height*polyRatio
#     p2_uniform[:expNum*2] = pExp

################################################################################
## 真空拉比拟合
################################################################################

class Vcrabi_fit():
    def __init__(self,length=None):
        self.length = length
    def func(self,x,paras):
        g, A0, Z0 = paras
        return np.sqrt(4*(g)**2+A0**2*(x-Z0)**2)
    def err(self,paras,x,y):
        return np.sum((self.func(x,paras)-y)**2)
    def guess(self,x,y):
        Z0 = x[np.argmin(y)]
        g = np.min(y)/2
        x, y = x[x!=Z0], y[x!=Z0]
        A0 = np.mean(np.sqrt(y**2-4*(g)**2)/(x-Z0))
        return g, A0, Z0
    def fitVcrabi(self,x,y):
        if self.length is None:
            p0 = self.guess(x,y)
            mybounds = MyBounds(xmin=[0,0,-1.1],xmax=[0.1,np.inf,1.1])
            res = bh(self.err,p0,niter=100,minimizer_kwargs={"method":"Nelder-Mead","args":(x, y)},accept_test=mybounds)
            return res, self.func
        else:
            index = len(y)//2
            start, end = index-self.length, index+self.length
            x0, y0 = x[start:end], y[start:end]
            p0 = self.guess(x0,y0)
            mybounds = MyBounds(xmin=[0,0,-1.1],xmax=[0.1,np.inf,1.1])
            res = bh(self.err,p0,niter=100,minimizer_kwargs={"method":"Nelder-Mead","args":(x0, y0)},accept_test=mybounds)
            
            space = np.abs(y-self.func(x,res.x)) < 0.1*np.abs(self.func(x,res.x))
            x0, y0 = x[space], y[space]
            p0 = self.guess(x0,y0)
            mybounds = MyBounds(xmin=[0,0,-1.1],xmax=[0.1,np.inf,1.1])
            res = bh(self.err,p0,niter=100,minimizer_kwargs={"method":"Nelder-Mead","args":(x0, y0)},accept_test=mybounds)
            return res, self.func

################################################################################
## 拟合Q值
################################################################################

class Cavity_fit(RowToRipe):
    def __init__(self):
        pass

    def circleLeastFit(self,x, y):
        def circle_err(params, x, y):
            xc, yc, R = params
            return (x - xc)**2 + (y - yc)**2 - R**2

        p0 = [
            x.mean(),
            y.mean(),
            np.sqrt(((x - x.mean())**2 + (y - y.mean())**2).mean())
        ]
        res = ls(circle_err, p0, args=(x, y))
        return res.x

    def guessParams(self,x,s):
        
        y = np.abs(1 / s)
        f0 = x[y.argmax()]
        _bw = x[y > 0.5 * (y.max() + y.min())]
        FWHM = np.max(_bw) - np.min(_bw)
        Qi = f0 / FWHM
        _, _, R = self.circleLeastFit(np.real(1 / s), np.imag(1 / s))
        Qe = Qi / (2 * R)
        QL = 1 / (1 / Qi + 1 / Qe)

        return [f0, Qi, Qe, 0, QL]

    def invS21(self, f, f0, Qi, Qe, phi):
        #QL = 1/(1/Qi+1/Qe)
        return 1 + (Qi / Qe * np.exp(1j * phi)) / (
            1 + 2j * Qi * (np.abs(f) / np.abs(f0) - 1))
    
    def err(self,params,f,s21):
        f0, Qi, Qe, phi = params
        y = np.abs(s21) - np.abs(self.invS21(f, f0, Qi, Qe, phi) )
        return np.sum(np.abs(y)**2)

    def fitCavity(self,x,y):
        f, s = self.deductPhase(x,y)
        s = s[0]/np.max(np.abs(s[0]))
        f0, Qi, Qe, phi, QL = self.guessParams(f,s)
        res = bh(self.err,(f0, Qi, Qe, phi),niter = 100,\
            minimizer_kwargs={"method":"Nelder-Mead","args":(f, 1/s)}) 
        f0, Qi, Qe, phi = res.x
        QL = 1 / (1 / Qi + 1 / Qe)
        return f0, Qi, Qe, QL, phi, f, s

def amp_opt(y,s,radio=0.5):
    s0=[]
    s1=[]
    for i in range(len(s)):
        s1 = (s[i]>(np.max(s[i])*radio+np.min(s[i])*(1-radio)))
        if i ==0:
            s0 = (s[i]>(np.max(s[i])*radio+np.min(s[i])*(1-radio))) 
        if list(s0)!=list(s1):
            for i,j in enumerate(s0):
                if j==False:
                    s1[i]=j
        s0=s1
    val = []
    indexs=[]
    for i,j in enumerate(s0):
        if j:
            val.append(y[i])
            indexs.append(i)
    indexw = np.argmax([np.mean(s[:,i]) for i in indexs])
    return y[indexs[indexw]]

    

def run_points(s0,si,idx=0,radio=0.5):
    s1 = (si>(np.max(si)*radio+np.min(si)*(1-radio)))
    if idx ==0:
        s0 = (si>(np.max(si)*radio+np.min(si)*(1-radio))) 
    if list(s0)!=list(s1):
        for n,j in enumerate(s1):
            if j==False:
                s0[n]=j
    return s0

  