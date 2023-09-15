import asyncio, inspect
import functools

import nest_asyncio
import numpy as np
from scipy.optimize import minimize
from bayes_opt import BayesianOptimization as bayes
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs

nest_asyncio.apply()


def get_initial_simplex(start, senstive=None):
    if senstive is None:
        senstive = np.ones(len(start))

    initial_simplex = [list(start)]
    for i, v in enumerate(senstive):
        row = list(start)
        row[i] += v
        initial_simplex.append(row)
    return np.asarray(initial_simplex)


def parameter_filter(x, dec=None, high=None, low=None):
    if dec is not None:
        x = np.asarray([np.round(a, decimals=d) for a, d in zip(x, dec)])
    if high is None and low is None:
        return x
    return x.clip(low, high)


def optimize(target,
             start,
             senstive=None,
             dec=None,
             high=None,
             low=None,
             method='Nelder-Mead',
             print_info=False,
             tol = None,
             kws={},
             options={}):
    """
    搜索最小值
    target: 目标函数
    start: 起始点
    senstive: list 敏感度
    dec: list 小数位数
    high: list 上限
    low: list 下限
    print_info: bool
    """

    optimizedTargetValue = None

    if asyncio.iscoroutinefunction(target):

        def _target(*x):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(target(*x,**kws))
    else:
        _target = target

    @functools.lru_cache()
    def cache_target(*x):
        return _target(*x,**kws)

    def f(x):
        nonlocal optimizedTargetValue
        x = parameter_filter(x, dec, high, low)
        ret = cache_target(*x)
        if print_info:
            print('.', end='')
        if optimizedTargetValue is None or optimizedTargetValue > ret:
            optimizedTargetValue = ret
            if print_info:
                print('o')
                print(list(x), ret, end='   ')
        return ret
    options['initial_simplex'] = get_initial_simplex(start, senstive)

    ret = minimize(
        f,
        start,
        method=method,
        tol=tol,
        options=options)

    if print_info:
        print('\n', cache_target.cache_info())

    ret['x'] = parameter_filter(ret['x'], dec, high, low)

    return ret

def optimize_bayes(target,
             start,
             senstive=None,
             dec=None,
             high=None,
             low=None,
             print_info=False,
             init_points=5,
             n_iter=25,
             saveStatus=False,
             loadStatus=False,
             path=r"D:\skzhao\bayes_optimize_paras\bayes_paras.json"):
    """
    搜索最大值
    target: 目标函数
    start: 起始点
    senstive: list 敏感度
    dec: list 小数位数
    high: list 上限
    low: list 下限
    print_info: bool
    n_iter: 优化迭代次数
    """
    verbose= 2 if print_info else 1
    insp = inspect.getfullargspec(target)
    kwsLst = insp[0]

    pbounds, params_start = {}, {}
    for i, j in enumerate(kwsLst):
        pbounds[j] = (low[i],high[i])
        params_start[j] = start[i]

    # print('pbounds:',pbounds,'params_start:',params_start)

    if asyncio.iscoroutinefunction(target):

        def _target(**x):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(target(**x))
    else:
        _target = target

    @functools.lru_cache()
    def cache_target(**x):
        return _target(**x)

    rf_bo = bayes(cache_target,pbounds=pbounds,verbose=verbose,random_state=7)

    if loadStatus:
        load_logs(rf_bo, logs=[path])

    rf_bo.probe(params=params_start,lazy=True,)

    rf_bo.maximize(init_points=init_points,n_iter=n_iter,allow_duplicate_points=True)

    if saveStatus:
        logger = JSONLogger(path=path)
        rf_bo.subscribe(Events.OPTIMIZATION_STEP, logger)

    return rf_bo.max, rf_bo