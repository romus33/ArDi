"""
The module finder for web-app ArDi (ArDI (Advanced spectRa Deconvolution Instrument)) for fitting of different types of curves. The application uses the follow packages:
1) micromap (https://github.com/romus33/micromap): time, ctypes, multiprocessing, lmfit, numpy, scipy, termcolor, os, platform

2) dash, plotly, dash_bootstrap, pandas, urllib, base64, io, os, sys, copy


Release: 0.2.0
"""
__author__ = "Roman Shendrik"
__copyright__ = "Copyright (C) 2023R"
__license__ = "GNU GPL 3.0"
__version__ = "0.2.0"

import numpy as np
import scipy.special as sp
#import os,sys,math
import fittingmap as mm

def smooth_als(y, lam, p):
    fit_ = mm.FittingMap()
    yy = fit_.__baseline_als__(y, lam, p)
    return yy

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def readfile(filename, skiprows = 1):
        a = np.loadtxt(filename, skiprows=skiprows)
        xx = np.array([])
        yy = np.array([])
        for item in a:
                xx = np.append(xx,np.float64(item[0]))
                yy = np.append(yy,np.float64(item[1]))
        spectra = {}
        spectra = peakdetect(xx,yy,1,0.5)
        return spectra
        
def peakdetect(xx, yy, lookahead = 1, delta = 0.011):
        #filecp = codecs.open(filename, encoding = 'utf8', errors='ignore')
    #Читаем файл с пропуском первых 9 строк, в которых нет спектра
        
    #Ограничиваем область деконволюции 650-1800 см-1
    #filtered = filter(lambda row: 650<row[0]<1800, a)
        
        fit = mm.FittingMap()
        spectra = {}
        yy = np.array(yy)
        xx = np.array(xx)
        yy = yy/max(yy)
        #Функция, которая ищет максимум. lookahead - минимальная дистанция между соседними пиками. delta - минимальное значение по y. Функция выдает номера элементов массива yy, в которых она нашла максимумы
        dd = fit.peakdet(yy,lookahead = lookahead, delta = delta)
        ampl = []
        x = []
        for each in dd:
                    ampl.append(yy[each])
                    x.append(xx[each])
                    #print(xx[each],'\t',yy[each])                
        spectra['spectrum'] = [xx,yy]
        spectra['peaks'] = x
        spectra['look'] = lookahead
        spectra['delta'] = delta
        spectra['ampl'] = ampl
        return spectra
 
def fitcurve(xx,yy,peaks_str,parameters = None, tolerance = 1e-15):
        limits = {}
        ma = {}
        i = 0  
        fname = 'ab' 
        fit = mm.FittingMap()
        params = {}
        limits = {}
        ma = {}
        i = 0  
        x = [int(i) for i in peaks_str.split(',') if i.strip().isdigit()]
        xx = np.array(xx)
        yy = np.array(yy)
        params['baseline_auto'] = [1e7,0.005,5]
        params['kws'] = {'ftol': tolerance, 'xtol': tolerance, 'gtol': tolerance}
        params['max_nfev'] = 10000000
        limits['baseline_auto'] = [[1e4, 5e9], [0.0001, 0.1]]
        if parameters is None:
            params['amplitude'] = np.full(len(x),1)
            params['center'] = np.array(x)    
            params['width'] = np.full(len(x),4)
            params['method'] = np.full(len(x),'PseudoVoigt')
            limits['amplitude'] = np.full((len(x),2),[0,1000])
            limits['width'] = np.full((len(x),2),[0.2,40])
            limits['center'] = np.full((len(x),2),[5,5])
            
        else:
            p_center = []
            p_amplitude = []
            p_width = []
            p_method = []
            l_center = []
            l_amplitude = []
            l_width = []
            
            for item in parameters:
                p_center.append(float(item['p_center']))
                p_amplitude.append(float(item['p_amplitude']))
                p_width.append(float(item['p_width']))
                p_method.append(item['p_method'])
                l_center.append([float(item['l_center_min']),float(item['l_center_max'])])
                l_amplitude.append([float(item['l_amplitude_min']),float(item['l_amplitude_max'])])
                l_width.append([float(item['l_width_min']),float(item['l_width_max'])])
            params['center'] = np.array(p_center)
            params['amplitude'] = np.array(p_amplitude)
            params['width'] = np.array(p_width)
            params['method'] = p_method
            limits['amplitude'] = np.array(l_amplitude)
            limits['width'] = np.array(l_width)
            limits['center'] = np.array(l_center)
        print(params)
        print(limits)        
        result = fit.fit_array(xx,yy,params,limits,fname)

        A = result['amplitude']
        FWHM = result['FWHM']
        C = result['center']
        H = result['height']
        Rsq = result['r-square']
        Sig = result['sigma']
        
        C_ = []
        H_ = []
        F_ = []
        A_ = []
        S_ = []
        print("Peak N\t"+"||\t"+"Amplitude\t"+"||\t"+"Center\t"+"||\t"+"FWHM\t"+"||\t"+"Height\t"+"\n")
        for (idx), value in np.ndenumerate(A):
                C_.append(C[idx[0]])
                H_.append(H[idx[0]])
                F_.append(FWHM[idx[0]])
                A_.append(value)
                S_.append(Sig[idx[0]])
                print(
                      str(idx[0]+1)+"\t||\t"+
                      value.astype('str')+"\t||\t"+
                      C[idx[0]].astype('str')+"\t||\t"+
                      FWHM[idx[0]].astype('str')+"\t||\t"+
                      H[idx[0]].astype('str')
                      )
        fit_param = {'Center':np.array(C_), 'Amplitude': np.array(A_),'Sigma': np.array(S_), 'FWHM': np.array(F_), 'Height': np.array(H_),  'R-Square': Rsq}
        x1 = fit.map_baseline[fname][0]
        y1 = fit.map_baseline[fname][1]
        #ddd = xx
        length_ = len(xx)
        length_2 = len(x1)
        #Рисуем и сохраняем кривые
        return {'input': [xx,yy], 'output': [x1, y1], 'components': fit.components, 'length_in': length_, 'length_out':  length_2, 'params': fit_param}