# ----------------------------------------------------------------------------
# Copyright (c) 2019, AIHN-UCSD development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


from time import time
from numpy import random
import tarfile
from .TADA_data import Data
import os
import numpy as np
import unittest
import biom
import dendropy

def make_tarfile(output_filename, source_dir):
	with tarfile.open(output_filename, "w:gz") as tar:
		tar.add(source_dir, arcname=os.path.basename(source_dir))


class SampleGenerator(Data, unittest.TestCase):

	def __init__(self, seed_num=0, logger=None, generate_strategy="augmentation", tmp_dir=None,
				 xgen=5, n_beta=1, n_binom=5, var_method='br_penalized', stat_method='binom', prior_weight=0.0,
				 coef=200, exponent = 1/2, pseudo=1e-6, pseudo_cnt=5, normalized=False):

		Data.__init__(self, seed_num, logger, generate_strategy, tmp_dir, xgen, n_beta, n_binom,
				 var_method, stat_method, prior_weight, coef, exponent, pseudo, pseudo_cnt, normalized)

		np.random.seed(seed_num)
		self.logger_ins.info("The seed number inside the sample generatory fixed to", seed_num)
		print("The temp directory is", self.dirpath)


	def fit_transform(self, table, y, tree: dendropy.Tree):
		'''
		:param table: input biom table
		:param y: input labels
		:param tree:  input tree file path in newick format (dendropy.Tree)
		:return:
		'''
		self._set_data(table, y, tree)

		t0 = time()
		self._comput_average_distances()
		self.logger_ins.info("computing the average tip-to-tip distances took", time() - t0, "seconds")
		self.__traverse_tree()
		augm_biom, augm_labels = self.get_augm_data()
		orig_biom, orig_labels = self.get_orig_data()
		return orig_biom, orig_labels,  augm_biom, augm_labels

	def __load_counts_on_tree_class(self, class_id):
		samples = self.clusters[class_id]
		self.logger_ins.info(samples)
		smp_idxs = np.asarray([self.sample_dct[sample] for sample in samples])

		t0 = time()
		for nd in self.tree.postorder_node_iter():
			if nd.is_leaf():
				seq = nd.taxon.label
				if seq in self.obs_dct:
					seq_idx = self.obs_dct[seq]

					if hasattr(nd, 'freq_class'):
						nd.freq_class[class_id] = self.table[seq_idx, smp_idxs].reshape((-1, 1))
					else:
						nd.freq_class = dict()
						nd.freq_class[class_id] = self.table[seq_idx, smp_idxs].reshape((-1, 1))
				else:
					if hasattr(nd, 'freq_class'):
						nd.freq_class[class_id] = np.zeros((len(smp_idxs), 1))
					else:
						nd.freq_class = dict()
						nd.freq_class[class_id] = np.zeros((len(smp_idxs), 1))
			else:
				child_nodes = nd.child_nodes()
				if hasattr(nd, 'freq_class'):
					nd.freq_class[class_id] = child_nodes[0].freq_class[class_id] + child_nodes[1].freq_class[class_id]
					nd.mu[class_id] = np.mean(child_nodes[0].freq_class[class_id])
					nd.S[class_id] = np.mean(np.power(child_nodes[0].freq_class[class_id], 2))
					nd.n1[class_id] = np.mean(nd.freq_class[class_id])
					nd.n2[class_id] = np.mean(np.power(nd.freq_class[class_id], 2))
					nd.p[class_id] = nd.mu[class_id] / nd.n1[class_id]
					nd.probs[class_id] = child_nodes[0].freq_class[class_id] / nd.freq_class[class_id]
				else:
					nd.freq_class = dict()
					nd.mu = dict()
					nd.S = dict()
					nd.n1 = dict()
					nd.n2 = dict()
					nd.p = dict()
					nd.probs = dict()
					nd.freq_class[class_id] = child_nodes[0].freq_class[class_id] + child_nodes[1].freq_class[class_id]
					nd.mu[class_id] = np.mean(child_nodes[0].freq_class[class_id])
					nd.S[class_id] = np.mean(np.power(child_nodes[0].freq_class[class_id], 2))
					nd.n1[class_id] = np.mean(nd.freq_class[class_id])
					nd.n2[class_id] = np.mean(np.power(nd.freq_class[class_id], 2))
					nd.p[class_id] = nd.mu[class_id] / nd.n1[class_id]
					nd.probs[class_id] = child_nodes[0].freq_class[class_id] / nd.freq_class[class_id]

		self.logger_ins.info("traversing the tree for class", class_id, "Finished in", time() - t0, "seconds")
		return

	def __load_counts_on_tree_individual(self, sample_ids, class_id):
		samples = sample_ids
		smp_idxs = np.asarray([self.sample_dct[sample] for sample in samples])
		tree = self.tree
		for nd in tree.postorder_node_iter():
			'''
			features_edge_pr: num samples x num features 
			self.edge_map: keys: edge_num values: index of them (for features), note that edge_num is fixed across different runs
			rev_placement_supports: keys: edge_num, values: list of tuples (sequence (not species name), likelihood, pendent_edge_length, index (0 means maximum likelihood postion))
			'''
			if nd.is_leaf():
				seq = nd.taxon.label
				if seq in self.obs_dct:
					seq_idx = self.obs_dct[seq]

					nd.freq = self.table[seq_idx, smp_idxs]
					nd.prior = np.sum(nd.freq_class[class_id])
				else:
					nd.freq = 0
					nd.prior = np.sum(nd.freq_class[class_id])

			else:
				child_nodes = nd.child_nodes()
				nd.freq = child_nodes[0].freq + child_nodes[1].freq
				nd.prior = np.sum(nd.freq_class[class_id])
				if nd.prior - child_nodes[0].prior < nd.freq - child_nodes[0].freq:
					self.logger_ins.info("The length of the class_id", class_id, "is", len(self.clusters[class_id]),
										 "And the size of the freq_class is", nd.freq_class[class_id].shape)
					self.logger_ins.info("The class id is", class_id, "smp_idxs:", smp_idxs, "sample_ids", sample_ids)
					self.logger_ins.info("The label is", nd.label, "The prior of the node is", nd.prior,
										 "The freq  for node is", nd.freq, "Child0 label:",
										 child_nodes[0].label, "prior child 0:", child_nodes[0].prior, "freq child 0:",
										 child_nodes[0].freq, sample_ids, self.table[:, smp_idxs])
					exit()

		return tree

	def __get_method_of_moments_estimates(self, n1, n2, S, mu, p):
		if self.stat_method != 'beta':
			alpha_mom = (n2 * mu - n1 * S) / ((S / mu - 1) * np.power(n1, 2) + mu * (n1 - n2))
			beta_mom = (S / mu * n1 - n2) * (mu - n1) / ((S / mu - 1) * np.power(n1, 2) + mu * (n1 - n2))
		# if alpha_mom < 0 or beta_mom < 0:
		# self.logger_ins.info("WARNING: The alpha and beta estimates from method of moments are negative!", "n1:",
		# 				n1, "n2:", n2, "S:", S, "mu:", mu, "alpha_mom:", alpha_mom, "beta_mom:", beta_mom)
		else:
			alpha_mom, beta_mom = self.__infer_alpha_and_beta_beta_distribution(p)

		return alpha_mom, beta_mom

	def __infer_alpha_and_beta_beta_distribution(self, p):
		mu = np.mean(p)
		std = np.var(p)

		if std == 0:
			alpha_mom = -1
			beta_mom = -1
		else:
			M = mu * (1 - mu)
			alpha_mom = mu * (M / std - 1)
			beta_mom = (1 - mu) * (M / std - 1)

		return alpha_mom, beta_mom

	def __infer_alpha_and_beta(self, frc0, prc0, nd, class_id):
		if self.var_method == 'br_penalized' and self.stat_method != "binom":
			p = np.mean(frc0 * (1 - self.prior_weight) + prc0 * self.prior_weight)
			a = p * np.power(nd.avg + self.pseudo, self.exponent) * self.coef
			b = (1 - p) * np.power(nd.avg + self.pseudo, self.exponent) * self.coef
		elif self.stat_method == "binom":
			a = -1
			b = -1
		else:
			a, b = self.__get_method_of_moments_estimates(nd.n1[class_id], nd.n2[class_id], nd.S[class_id],
														nd.mu[class_id], nd.probs[class_id])
		return a, b

	def __gen_beta(self, a, b, n, Pr):
		if a == 0 and b > 0:
			x = np.zeros((n, 1))
		elif b == 0 and a > 0:
			x = np.ones((n, 1))
		elif a > 0 and b > 0:
			x = random.beta(a, b, size=n)
		else:
			p = [Pr]
			x = np.asarray(p * n)
		return x.ravel()

	def __gen_binomial(self, p, nd, n_binom):
		gen_x = list()
		n = nd.f
		for i in range(len(n)):
			i_p = i // n_binom
			if n[i] > 0 and p[i_p] > 0:
				gen_x.append(np.random.binomial(n[i], p[i_p], size=1))
			else:
				gen_x.append([0] * 1)
		return np.asarray(gen_x).ravel()

	def __set_children_features(self, nd, child_l, child_r, Pr, n_binom):
		if self.stat_method == "beta_binom" or self.stat_method == "binom":
			gen_x = self.__gen_binomial(Pr, nd, n_binom)
			child_l.f = gen_x
			child_r.f = nd.f - gen_x
		elif self.stat_method == "beta":
			child_l.f = Pr * nd.f
			child_r.f = (1 - Pr) * nd.f


	def __gen_augmented_sample(self, tree, n_binom, n_beta, class_id):
		t1 = time()
		if n_binom == 0:
			return
		n_generate = n_binom * n_beta
		to_be_generated = np.zeros((n_generate, len(self.obs_dct)))
		for nd in tree.preorder_node_iter():
			if nd == tree.seed_node:
				nd.f = np.asarray(
					[int(np.mean(nd.freq))] * n_binom * n_beta).ravel() if self.stat_method != "beta" else np.ones(
					(n_binom * n_beta,))

			if nd.is_leaf():
				seq = nd.taxon.label
				if seq in self.obs_dct:
					seq_idx = self.obs_dct[seq]
					to_be_generated[:, seq_idx] = np.asarray(nd.f).ravel()
			else:
				child_nodes = nd.child_nodes()
				frc0 = child_nodes[0].freq / (child_nodes[0].freq + child_nodes[1].freq) if child_nodes[0].freq + \
																							child_nodes[
																								1].freq > 0 else 0
				prc0 = child_nodes[0].prior / (child_nodes[0].prior + child_nodes[1].prior) if child_nodes[0].prior + \
																							   child_nodes[
																								   1].prior > 0 else 0

				pr_l = frc0 * (1 - self.prior_weight) + prc0 * self.prior_weight if (
						self.var_method == 'br_penalized') else nd.p[class_id]

				a, b = self.__infer_alpha_and_beta(frc0, prc0, nd, class_id)
				# self.logger_ins.info("label", nd.label, "a:", a, "b:", b, "nd.freq:", nd.freq, "child[0].freq:",
				# 					 child_nodes[0].freq, "frc0", frc0, "prc0", prc0, "pr_l:", pr_l, "nd.prior",
				# 					 nd.prior, "child_nodes[0].prior", child_nodes[0].prior)


				x = self.__gen_beta(a, b, n_beta, pr_l)
				self.__set_children_features(nd, child_nodes[0], child_nodes[1], x, n_binom)

		# self.logger_ins.info(to_be_generated.sum(1))
		self.logger_ins.info("Time to add new samples", time() - t1, len(to_be_generated))
		self.augmented_data.append(to_be_generated)

	def __load_and_generate(self, samples, label, n_augmentation, n_beta):

		t0 = time()

		tree = self.__load_counts_on_tree_individual(samples, label)
		self.logger_ins.info("It took", time() - t0, "seconds to load counts on tree for this individual")
		t1 = time()
		self.__gen_augmented_sample(tree, n_augmentation, n_beta, label)

		self.samples_generated += [samples[0]] * n_augmentation * n_beta
		self.labels_generated += [label] * n_augmentation * n_beta
		self.logger_ins.info("Time to add info of this sample", time() - t1)
		self.logger_ins.info("Generating", n_augmentation * n_beta, "samples for sample", samples, "finished in",
							 time() - t0, "seconds")
		return

	def __traverse_tree(self):
		'''
		Traverse the tree and computes features for each sample
		:return:
		'''
		for class_id in self.clusters.keys():
			self.__load_counts_on_tree_class(class_id)
		self.samples_generated = list()
		self.labels_generated = list()
		n_binom = self.n_binom
		n_beta = self.n_beta
		if self.generate_strategy == "augmentation" and self.var_method == "br_penalized":
			for i, _ in enumerate(self.samples):
				self.__load_and_generate([self.samples[i]], self.labels[i], n_binom, n_beta)

		elif self.generate_strategy == "augmentation" and self.var_method != "br_penalized":
			for cls in self.clusters:
				samples = self.clusters[cls]
				for _, sample in enumerate(samples):
					self.__load_and_generate([sample], cls, n_binom, n_beta)

		elif self.generate_strategy == 'balancing' and self.var_method == "br_penalized":
			for cls in self.clusters:
				samples = self.clusters[cls]
				if self.n_samples_to_select[cls] > 0:
					for sample in np.random.choice(samples, size=self.n_samples_to_select[cls], replace=True):
						self.__load_and_generate([sample], cls, n_binom, n_beta)
					sample = np.random.choice(samples, 1)[0]
					if self.n_binom_extra[cls] > 0:
						self.__load_and_generate([sample], cls, self.n_binom_extra[cls], 1)
		else:
			for cls in self.clusters:
				samples = self.clusters[cls].squeeze()
				if self.n_samples_to_select[cls] > 0:
					for sample in np.random.choice(samples, size=self.n_samples_to_select[cls], replace=True):
						self.__load_and_generate([sample], cls, n_binom, n_beta)
					sample = np.random.choice(samples, 1)[0]
					if self.n_binom_extra[cls] > 0:
						self.__load_and_generate([sample], cls, self.n_binom_extra[cls], 1)

		self.augmented_data = np.row_stack(self.augmented_data)

		return




	def __get_agum_data(self):
		samples = np.asarray(np.asarray(self.samples_generated).ravel())
		data = np.asarray(self.augmented_data)
		if self.normalized:
			data /= np.sum(data, axis=1, keepdims=True)
		return data, samples

	def __get_orig_data(self, feature):
		data = np.asarray(feature)
		data -= self.pseudo_cnt
		if self.normalized:
			data /= np.sum(data, axis=1, keepdims=True)
		return data


	def get_augm_data(self):
		data, samples = self.__get_agum_data()
		data = np.asarray(data.transpose())
		labels = self.__get_labels(samples, self.meta)
		samples = np.asarray([str(x) + "." + str(i) for i, x in enumerate(np.asarray(samples).ravel())])

		self.logger_ins.info("The size of features to be written on file_path is", data.shape)
		self.logger_ins.info("The number of samples is", len(samples))
		self.logger_ins.info("The length of features is", len(self.obs))

		t = biom.Table(data = data, observation_ids = self.sequences, sample_ids = np.asarray(samples).ravel())
		return t, labels

	def get_orig_data(self):
		data = self.__get_orig_data(self.table)
		self.logger_ins.info("The size of features to be written on file_path is", data.shape)
		self.logger_ins.info("The length of features is", len(self.obs))
		self.logger_ins.info("The number of samples is", len(self.samples))

		labels = self.__get_labels(self.samples, self.meta)
		t = biom.Table(data = data, observation_ids = self.sequences, sample_ids = self.samples)
		return t, labels

	def __get_labels(self, samples, meta):
		class_map = dict()
		for index, row in meta.iterrows():
			class_map[index] = row['label']

		labels = list()
		for sample in np.asarray(samples).squeeze():
			labels.append(class_map[sample])
		return labels



