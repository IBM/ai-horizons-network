# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import dendropy
import unittest
import pandas as pd
import tempfile
import numpy as np
from time import time
import os
from .logger import *

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

if 'TMPDIR' in os.environ:
	tmpdir = os.environ['TMPDIR']
else:
	tmpdir = tempfile.gettempdir()

def isNotEmpty(s):
	return bool(s and s.strip())



class Data():
	def __init__(self, seed_num, logger, generate_strategy, tmp_dir, xgen, n_beta, n_binom,
				 var_method, stat_method, prior_weight, coef, exponent, pseudo, pseudo_cnt, normalized):

		if tmp_dir is None:
			tmp_dir = tempfile.mkdtemp(dir=tmpdir)
		self.tmp_dir = tmp_dir
		if logger is not None:
			self.logger_ins = logger
		else:
			self.log_fp = tempfile.mktemp(dir=tmp_dir, prefix='logfile.log')
			log = LOG(self.log_fp)
			self.logger_ins = log.get_logger('generator')

		self.logger_ins.info("The seed number is set to", seed_num)
		np.random.seed(seed_num)

		self.logger_ins.info("The generate_strategy is", generate_strategy)
		self.logger_ins.info("The xgen is", xgen)
		self.logger_ins.info("The n_beta is", n_beta)
		self.logger_ins.info("The n_binom is", n_binom)
		self.logger_ins.info("The var_method is", var_method)
		self.logger_ins.info("The stat_method is", stat_method)
		self.logger_ins.info("The prior_weight is", prior_weight)
		self.logger_ins.info("The coef is", coef)
		self.logger_ins.info("The exponent is", exponent)
		self.logger_ins.info("The pseudo is", pseudo)
		self.logger_ins.info("The pseudo_cnt is", pseudo_cnt)
		self.logger_ins.info("The normalized is", normalized)

		if generate_strategy is not None:
			# generate_strategy: generation strategy, it could be "augmentation" meaning we are just augmenting data
			# without trying to balance out labels. Alternatively, "balancing" meaning we are balancing out labels

			self.generate_strategy = generate_strategy
		# stat_method: defines the generative procedure. options are "binom" , "beta_binom", "beta". We don't
		# recommend using beta. The default is binom

		self.stat_method = stat_method
		# prior_weight: defines the weight for per class parameter estimation. Default is 0 meaning we only use per individual parameter estimations
		self.prior_weight = prior_weight
		# coef: The penalty in the tree based variance formula. Default is 200. Larger numbers cause less variance
		self.coef = coef
		# exponent: The exponent in the tree based variance formula. Default is 1/2. Meaning

		self.exponent = exponent
		self.pseudo = pseudo
		self.xgen = xgen
		self.n_beta = n_beta
		self.n_binom = n_binom
		self.pseudo_cnt = pseudo_cnt
		# var_method: options are "br_penalized": priors are estimated based on the tree, or
		# "class": priors are estimated based on method of moments (cluster wise).
		self.var_method = var_method
		# normalized: If normalize biom table at the end or not. Default is False
		self.normalized = normalized
		if tmp_dir is not None:
			self.dirpath = tmp_dir
		else:
			self.dirpath = tempfile.mkdtemp(dir=tmpdir)

		self.logger_ins.info("Temporary directory path is", self.dirpath )




		if self.generate_strategy == "augmentation":
			self.most_freq_class = None
			self.freq_classes = None

	def _set_data(self, table, y, tree):
		t0 = time()
		self._load_tree(tree)
		self.logger_ins.info("loading the tree took", time() - t0, "seconds")
		t0 = time()
		self._set_table(table)
		self.logger_ins.info("biom table loaded in", time() - t0, "seconds")
		self.logger_ins.info("Number of sOTUs is ", len(self.obs))
		self.logger_ins.info("Number of samples is ", len(self.samples))

		t0 = time()
		self._set_labels(y)
		self.logger_ins.info("Meta data loaded in", time() - t0, "seconds")
		self._set_num_to_select()
		self._add_pseudo()
		self._init_gen()

	def _add_pseudo(self):
		'''
		adds pseudo count to each feature for the training data to avoid zero count
		self.pseudo_cnt should be an integer, where we divide it between all features.
		'''
		self.pseudo_cnt /= self.num_leaves
		self.table += self.pseudo_cnt


	def _set_num_to_select(self):
		'''
		This function sets the number of samples to be drawn for each class
		self.n_samples_to_select: key: class label, values: number of samples to be selected from each class

		:return:
		'''
		# If self.most_freq_class is None or self.freq_classes is None, then we are just augmenting, no need to
		# set up n_samples_to_select
		if self.generate_strategy == 'augmentation':
			self.n_binom_extra = {'all': 0}
		else:
			self.n_binom_extra = dict()
			self.n_samples_to_select = dict()
			for c in self.freq_classes:
				# n_all: after augmentation, all classes should have n_all + self.most_freq_class number of samples
				n_all = self.most_freq_class * (self.xgen)

				# check if our logic was correct
				if n_all + self.most_freq_class - self.freq_classes[c] < 0:
					print("The n_all is negative!", n_all + self.most_freq_class - self.freq_classes[c], c, n_all,
						  self.most_freq_class, self.freq_classes[c])
					exit()
				# number of samples to generate equals n_total_samples_to_gen
				n_total_samples_to_gen = np.max(n_all + self.most_freq_class - self.freq_classes[c], 0)

				# per each sample we generate self.n_binom*self.n_beta samples. Thus, the number of samples to select is

				self.n_samples_to_select[c] = np.max(
					(n_total_samples_to_gen) // (self.n_binom * self.n_beta), 0)

				# per each sample we generate self.n_binom*self.n_beta samples. If
				# n_total_samples_to_gen % (self.n_binom * self.n_beta) != 0, then we need some extra augmentation

				self.n_binom_extra[c] = max(
					n_total_samples_to_gen - self.n_samples_to_select[c] * self.n_binom  * self.n_beta, 0)

				self.logger_ins.info("class", c, "Generating", self.n_samples_to_select[c], "samples", "with",
									 "n_binom:", self.n_binom, "and n_beta:", self.n_beta, "and n_binom_extra",
									 self.n_binom_extra[c])

	def _set_labels(self, labels):
		'''
		:param labels: labels
		creates a data frame from the labels using self.__set_meta_clusters(labels)
		Then finds the most frequent class, an store the frequency in self.most_freq_class
		Finally sets clusters, a dictionary with keys: class labels, values: sample IDs
		:return:
		'''
		self.meta, self.labels, self.classes, counts = self._set_meta_clusters(labels)
		self.freq_classes = dict()
		max_cnt = 0
		for i, cls in enumerate(self.classes):
			self.freq_classes[cls] = counts[i]
			if self.freq_classes[cls] > max_cnt:
				max_cnt = self.freq_classes[cls]
		self.most_freq_class = max_cnt
		self.samples = np.asarray(self.samples)
		self._set_clusters()





	def _set_meta_clusters(self, labels):
		'''
		:param labels: phenotype labels
		creates a data frame from the labels, and fills the missing labels with a label "-1" by default.
		:return: data frame (meta), labels, classes: set of labels, counts: number of samples corresponding to each class
		'''
		labels = np.asarray(labels).ravel()
		meta = pd.DataFrame(index =  self.samples, columns = ['label'], data = labels)
		meta['label'] = meta['label'].fillna(-1)
		labels = meta['label']
		classes, counts = np.unique(labels, return_counts=True)
		self.logger_ins.info("possible class labels are", classes)
		for i in range(len(classes)):
			self.logger_ins.info("The number of samples from the class", classes[i], "in the is", counts[i])

		return meta, labels, classes, counts


	def _set_clusters(self):
		'''
		:sets the self.clusters. keys: class labels, values: sample ids
		'''
		self.clusters = dict()
		for cls in self.classes:
			if pd.isnull(cls):
				self.clusters['NaN'] = self.samples[self.meta['label'].isnull()]
				self.logger_ins.info("The number of samples with label", 'NaN', "is", len(self.clusters['NaN']))

			else:
				self.clusters[cls] = self.samples[self.labels == cls]
				self.logger_ins.info("The number of samples with label", cls, "is", len(self.clusters[cls]))

	def _init_gen(self):
		'''
		initiates the self.augmented_data: stores genrated data, rows: samples, columns: features.
		self.orig_samples: original data + pseudo count
		'''
		self.augmented_data = list()
		self.orig_samples = self.table.transpose()

	def _set_table(self, table):
		'''
		loads the biom table, removes unseen observation, and normalizes it, and saves the observations and samples
		:return:
		'''

		self.logger_ins.info("size of table before filtering", table.shape)
		self.table = table
		self.samples = table.ids('sample')
		self.obs = set(self.table.ids('observation'))
		self.sequences = self.table.ids('observation')
		self._sample_obs_dct()
		self.table = self.table.matrix_data.todense()
		return



	def _sample_obs_dct(self):
		'''
		 To keep track of index of samples and sequences in the biom table, we create two dictionaries
		 self.obs_dct: key: sequences, values: index
		 self.sample_dct: key: sample, values: index
		:return:
		'''
		sequences = self.table.ids('observation')
		samples = self.table.ids('sample')
		self.obs_dct = dict()
		for i, seq in enumerate(sequences):
			self.obs_dct[seq] = i

		self.sample_dct = dict()
		for i, sample in enumerate(samples):
			self.sample_dct[sample] = i
		return


	def _load_tree(self, tree: dendropy.Tree):
		'''
		:param tree: Phylogeny in Newick Fromat (dendropy.Tree)
		'''
		self.tree = tree

		self.tree.resolve_polytomies()
		c = 0
		for nd in self.tree.postorder_node_iter():
			if nd == self.tree.seed_node and nd.label is None:
				nd.label = "root"
			if nd.is_leaf():
				nd.label = nd.taxon.label
			else:
				nd.label = "internal_node_" + str(c)
			c += 1

		self.num_leaves = len(self.tree.leaf_nodes())

		return

	def _comput_average_distances(self):
		'''
		:param tree: The phylogeny
		:return: Computes the average tip to tip distances bellow for each clade of the tree in one traverse of the trees
		'''
		for nd in self.tree.postorder_node_iter():
			if nd.is_leaf():
				nd.num = 1
				nd.avg = 0.0
				nd.sum_dist = 0.0
				nd.num_pairs = 1
			else:
				child_nodes = nd.child_nodes()
				nd.num_pairs = child_nodes[0].num * child_nodes[1].num
				total_dist = child_nodes[1].sum_dist * child_nodes[0].num + child_nodes[0].sum_dist * child_nodes[
					1].num + \
							 (child_nodes[1].edge.length + child_nodes[0].edge.length) * (nd.num_pairs)
				nd.avg = total_dist / (nd.num_pairs)

				nd.sum_dist = child_nodes[0].sum_dist + child_nodes[1].sum_dist + \
							  child_nodes[0].edge.length * child_nodes[0].num + \
							  child_nodes[1].edge.length * child_nodes[1].num

				nd.num = child_nodes[0].num + child_nodes[1].num
		return

if __name__ == '__main__':
	unittest.main()
