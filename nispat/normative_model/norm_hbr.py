#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 17:01:24 2019

@author: seykia
"""

from __future__ import print_function
from __future__ import division

import os
import sys
import numpy as np

try:  # run as a package if installed
    from nispat import fileio
    from nispat.normative_model.normbase import NormBase
    from nispat.hbr import HBR 
except ImportError:
    pass

    path = os.path.abspath(os.path.dirname(__file__))
    if path not in sys.path:
        sys.path.append(path)
    del path
    import fileio
    from hbr import HBR
    from norm_base import NormBase

class NormHBR(NormBase):
    """ Classical GPR-based normative modelling approach
    """

    def __init__(self, **kwargs):
        
        self.configs = dict()
        self.configs['trbefile'] = kwargs.pop('trbefile',None) 
        self.configs['tsbefile'] = kwargs.pop('tsbefile',None) 
        self.configs['type'] = kwargs.pop('model_type', 'linear')
        self.configs['random_intercept'] = kwargs.pop('random_intercept', 'True') == 'True'
        self.configs['random_slope'] = kwargs.pop('random_slope', 'True') == 'True'
        self.configs['random_noise'] = kwargs.pop('random_noise', 'True') == 'True'
        self.configs['hetero_noise'] = kwargs.pop('hetero_noise', 'False') == 'True'
        self.configs['noise_model'] = kwargs.pop('noise_model', 'linear')
        self.configs['nn_hidden_neuron_num'] = int(kwargs.pop('nn_hidden_neuron_num', '2'))
        self.configs['transfer'] = kwargs.pop('new_site', 'False') == 'True'
        self.configs['newsite_training_idx'] = kwargs.pop('newsite_training_idx', None)
        self.configs['pred_type'] = kwargs.pop('pred_type', 'single')

        self.hbr = HBR(self.configs)
        
    @property
    def n_params(self):
        return 1
    
    @property
    def neg_log_lik(self):
        return -1
    
    def estimate(self, X, y, **kwargs):
        
        trbefile = kwargs.pop('trbefile',None) 
        if trbefile is not None:
            batch_effects_train = fileio.load(trbefile)
        else:
            print('Could not find batch-effects file! Initilizing all as zeros ...')
            batch_effects_train = np.zeros([X.shape[0],2])

        self.hbr.estimate(X, y, batch_effects_train)
        
        return self
    
    def predict(self, Xs, X=None, Y=None, **kwargs): 
        
        tsbefile = kwargs.pop('tsbefile',None) 
        if tsbefile is not None:
            batch_effects_test = fileio.load(tsbefile)
        else:
            print('Could not find batch-effects file! Initilizing all as zeros ...')
            batch_effects_test = np.zeros([Xs.shape[0],2])    
        
        pred_type = self.configs['pred_type']
        
        yhat, s2 = self.hbr.predict(Xs, batch_effects_test, pred = pred_type)     
        
        return yhat.squeeze(), s2.squeeze()
    
    def estimate_on_new_sites(self, X, y, batch_effects):
    
        self.hbr.estimate_on_new_site(X, y, batch_effects)
        return self
    
    def predict_on_new_sites(self, X, batch_effects):
    
        yhat, s2 = self.hbr.predict_on_new_site(X, batch_effects)
        return yhat, s2
    