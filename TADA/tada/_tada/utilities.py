# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import tarfile
import itertools
import os
import numpy as np
import shutil
from heapq import nlargest

def isfloat(x):
	try:
		_ = float(x)
	except ValueError:
		return False
	else:
		return True

def isint(x):
	try:
		a = float(x)
		b = int(a)
	except ValueError:
		return False
	else:
		return a == b

def logp(x):
	try:
		a = np.log(float(x)+0.01)
	except ValueError:
		exit(1)
	else:
		return a
def return_instance(num):
	if isinstance(num, list) or isinstance(num, set):
		ret_lst = list()
		for x in num:
			if x is None:
				ret_lst.append(None)
			elif x == "False":
				ret_lst.append(False)
			elif x == "True":
				ret_lst.append(True)
			elif x == "None":
				ret_lst.append(None)
			elif isint(x):
				ret_lst.append(int(x))
			elif isfloat(x):
				ret_lst.append(float(x))
			elif x == "all":
				ret_lst.append(x)
			elif x == "auto":
				ret_lst.append(x)
			else:
				ret_lst.append(x)
		if isinstance(num, list):
			if len(num) == 1:
				return ret_lst[0]
			else:
				return ret_lst
		else:
			if len(num) == 1:
				return ret_lst[0]
			else:
				return set(ret_lst)
	else:
		if num is None:
			return None
		if num == "None":
			return None
		if num == "False" or num == "True":
			return eval(num)
		if isint(num):
			return int(num)
		if isfloat(num):
			return float(num)
		if num == "all":
			return num
		if num == "auto":
			return "auto"
		else:
			return None



def map_names(y_true,y_pred,maplabels):
	y_true_labeled = ["" for _ in range(len(y_true))]
	y_pred_labeled = ["" for _ in range(len(y_pred))]
	for i in range(len(y_true)):
		y_true_labeled[i] = maplabels[str(int(y_true[i]))]
		y_pred_labeled[i] = maplabels[str(int(y_pred[i]))]
	return (y_true_labeled, y_pred_labeled)


def make_tarfile(output_filename, source_dir):
	with tarfile.open(output_filename, "w:gz") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))
	shutil.rmtree(source_dir)


def freqCut(x, ratio):
	if ratio is None or ratio == 0:
		return None
	unique, counts = np.unique(np.array(x), return_counts=True)
	max12 = nlargest(2, counts)
	if len(max12) > 1:
		return (np.abs(max12[0]) / np.abs(max12[1])) <= ratio
	else:
		return False


def uniqueCut(value, thr):
	if thr is None or thr == 0:
		return None
	return len(np.unique(value)) / len(value) >= thr

def varCut(x, thr):
	if thr is None:
		return None
	return np.var(x)>thr

def nearZeroVar(x, ratio, thr, var_thr):
	conds = [uniqueCut(x, thr), freqCut(x, ratio), varCut(x, var_thr)]
	return any(conds)

