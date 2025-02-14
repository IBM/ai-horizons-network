import collections
import itertools
import json
import logging
import os
import pickle
import random

import numpy as np
from sklearn.model_selection import train_test_split

import config
from utils.utils import JsonlReader

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
np.random.seed(config.SEED)
random.seed(config.SEED)


def get_groups_texts_from_umls_vocab(relation_text_to_groups, cui_to_entity_texts, fname_reltext_all_combos,
                                     load_existing=True):
    # Load rel groups file, if it exists
    if os.path.isfile(fname_reltext_all_combos) and load_existing:
        logger.info('Found existing relation text combination file -- loading relations.')
        with open(fname_reltext_all_combos, 'rb') as f:
            return pickle.load(f)
    else:
        logger.info("Not loading relation text combination file. Generating new set:")

    # Get all related CUI groups into set:
    groups = set()
    for relation_text in relation_text_to_groups:
        groups.update(relation_text_to_groups[relation_text])

    # Collect all combinations of related entities
    logger.info("Collecting all possible textual combinations of CUI groups ...")
    groups_texts = set()
    l = len(groups)

    for idx, (cui_src, cui_tgt) in enumerate(groups):
        if idx % 100000 == 0 and idx != 0:
            logger.info("Parsed {} groups of {}".format(idx, l))
        cui_src_texts = cui_to_entity_texts[cui_src]
        cui_tgt_texts = cui_to_entity_texts[cui_tgt]
        for cui_src_text_i in cui_src_texts:
            temp = list(zip([cui_src_text_i] * len(cui_tgt_texts), cui_tgt_texts))
            temp = ["\t".join(i) for i in temp]
            groups_texts.update(temp)

    # NOTE: this consumes a LOT of memory (~18 GB)! (clearing up memory takes around half an hour)
    logger.info("Collected {} unique tuples of (src_entity_text, tgt_entity_text) type.".format(len(groups_texts)))

    # Save rel groups:
    with open(fname_reltext_all_combos, 'wb') as f:
        logger.info('Saving relation text combination file.')
        pickle.dump(groups_texts, f)

    return groups_texts


def align_groups_to_sentences(groups_texts, jsonl_fname, output_fname):
    jr = JsonlReader(jsonl_fname)
    wf = open(output_fname, "w", encoding="utf-8", errors="ignore")

    logger.info("Aligning texts (sentences) to groups ...")
    pos_groups = set()
    neg_groups = set()

    for idx, jdata in enumerate(jr):
        if idx % 1000000 == 0 and idx != 0:
            logger.info("Processed {} tagged sentences".format(idx))

        # Permutations of size for matched entities in a sentence
        matched_perms = set(itertools.permutations(jdata['matches'].keys(), 2))

        # Left-hand-side (lhs) <==> right-hand-side (rhs)
        lhs2rhs = collections.defaultdict(list)
        rhs2lhs = collections.defaultdict(list)

        for group in matched_perms:
            src, tgt = group
            lhs2rhs[src].append(tgt)
            rhs2lhs[tgt].append(src)

        # Since `groups_texts` contain all possible groups that can exist
        # in the UMLS KG, for some relation, the intersection of this set
        # with matched permuted groups efficiently yields groups which
        # **do exist in KG for some relation and have matching sentences**.
        matched_perms = {"\t".join(m) for m in matched_perms}
        common = groups_texts.intersection(matched_perms)

        # We use sentence level noise, i.e., for the given sentence the
        # common groups represent positive groups, while the negative
        # samples can be generated as follows (like open-world assumption):
        #
        # For a +ve group, with prob. 1/2, remove the left (src) or right
        # (tgt) entity and replace with N entities such that the negative
        # group (e_orig, e_replaced) [for rhs] / (e_replaced, e_orig) [for lhs]
        # **must not be in KG for any relation**. This technique can possibly be
        # seen as creating hard negatives for same text evidence.
        output = {"p": set(), "n": set()}

        for group in common:
            pos_groups.add(group)
            src, tgt = group.split("\t")
            output["p"].add(group)
            # Choose left or right side to corrupt
            lhs_or_rhs = random.choice([0, 1])

            if lhs_or_rhs == 0:
                for corrupt_tgt in lhs2rhs[src]:
                    negative_group = "{}\t{}".format(src, corrupt_tgt)
                    if negative_group not in common:
                        output["n"].add(negative_group)
            else:
                for corrupt_src in rhs2lhs[tgt]:
                    negative_group = "{}\t{}".format(corrupt_src, tgt)
                    if negative_group not in common:
                        output["n"].add(negative_group)

        if output["p"] and output["n"]:
            no = list(output["n"])
            random.shuffle(no)
            # Keep number of negative groups at most as positives
            no = no[:len(output["p"])]
            output["n"] = no
            output["p"] = list(output["p"])
            neg_groups.update(no)
            jdata["groups"] = output
            wf.write(json.dumps(jdata) + "\n")

    # There will be lot of negative groups, so we will remove them next!
    logger.info("Collected {} positive and {} negative groups.".format(len(pos_groups), len(neg_groups)))

    return pos_groups, neg_groups


def pruned_triples(cui_to_entity_texts, relation_text_to_groups, pos_groups, neg_groups, min_rel_group=10,
                   max_rel_group=1500):
    logger.info("Mapping CUI groups to relations ...")
    group_to_relation_texts = collections.defaultdict(list)

    for idx, (relation_text, groups) in enumerate(relation_text_to_groups.items()):
        for group in groups:
            group_to_relation_texts[group].append(relation_text)  # can have multiple rel texts per group

    logger.info("Mapping relations to groups texts ...")
    relation_text_to_groups_texts = collections.defaultdict(set)

    for idx, (group, relation_texts) in enumerate(group_to_relation_texts.items()):
        if idx % 1000000 == 0 and idx != 0:
            logger.info("Mapped from {} groups".format(idx))

        cui_src, cui_tgt = group
        local_groups = set()
        cui_src_texts = cui_to_entity_texts[cui_src]
        cui_tgt_texts = cui_to_entity_texts[cui_tgt]

        for l1i in cui_src_texts:
            local_groups.update(list(zip([l1i] * len(cui_tgt_texts), cui_tgt_texts)))

        for lg in local_groups:
            if "\t".join(lg) in pos_groups:
                for relation_text in relation_texts:
                    relation_text_to_groups_texts[relation_text].add("\t".join(lg))

    logger.info("No. of relations before pruning: {}".format(len(relation_text_to_groups_texts)))

    # Prune relations based on the group size
    relations_to_del = list()
    for relation_text, groups_texts in relation_text_to_groups_texts.items():
        if (len(groups_texts) < min_rel_group) or (len(groups_texts) > max_rel_group):
            relations_to_del.append(relation_text)

    logger.info("Relations not matching the criterion of min, max group sizes of {} and {}.".format(min_rel_group,
                                                                                                    max_rel_group))
    # Delete relations not meeting min and max counts
    for r in relations_to_del:
        del relation_text_to_groups_texts[r]
    logger.info("Relations deleted: {}".format(relations_to_del))
    logger.info("No. of relations after pruning: {}".format(len(relation_text_to_groups_texts)))

    # Update positive groups
    new_pos_groups = set()
    entities = set()
    for relation_text, groups_texts in relation_text_to_groups_texts.items():
        for group_text in groups_texts:
            new_pos_groups.add(group_text)
            entities.update(group_text.split("\t"))

    logger.info("Updated no. of positive groups after pruning: {}".format(len(new_pos_groups)))
    logger.info("No. of unique entities: {}".format(len(entities)))

    # Update negative groups

    # 1) We apply the constraint that the negative groups must have positive
    # triples entities only
    new_neg_groups = set()

    for negative_group in neg_groups:
        src, tgt = negative_group.split("\t")
        if (src in entities) and (tgt in entities):
            new_neg_groups.add(negative_group)

    logger.info("[1] Updated no. of negative groups after pruning groups that are not in positive entities: {}".format(
        len(new_neg_groups)))

    # 2) Negative examples are used for NA / Other relation, which is just another class.
    # To avoid training too much on NA relation, we make a simple choice randomly taking
    # the same number of groups as largest group size positive class.
    max_pos_group_size = max([len(v) for v in relation_text_to_groups_texts.values()])
    new_neg_groups = list(new_neg_groups)
    random.shuffle(new_neg_groups)

    # Using 70% of positive groups to form negative groups
    new_neg_groups = new_neg_groups[:int(max_pos_group_size * 0.7)]
    logger.info(
        'Len of new_pos_groups: {}, Len of max_pos_group_size: {}'.format(len(new_pos_groups), max_pos_group_size))
    logger.info(
        "Number of negative groups after taking 70 percent more than positive groups: {}".format(len(new_neg_groups)))

    relation_text_to_groups_texts["NA"] = new_neg_groups

    # Collect triples now
    triples = set()
    for r, groups in relation_text_to_groups_texts.items():
        for group in groups:
            src, tgt = group.split("\t")
            triples.add((src, r, tgt))
    triples = list(triples)

    logger.info(" *** No. of triples (including NA) *** : {}".format(len(triples)))

    return triples


def filter_triples_with_evidence(triples, max_bag_size=32):
    group_to_relation_texts = collections.defaultdict(set)

    for ei, rj, ek in triples:
        group = "{}\t{}".format(ei, ek)
        group_to_relation_texts[group].add(rj)

    jr = JsonlReader(config.groups_linked_sents_file)

    group_to_data = collections.defaultdict(list)
    candid_groups = set(group_to_relation_texts.keys())

    for idx, jdata in enumerate(jr):
        if idx % 1000000 == 0 and idx != 0:
            logger.info("Processed {} lines for linking to triples".format(idx))
        common = candid_groups.intersection(jdata["groups"]["p"] + jdata["groups"]["n"])

        if not common:
            continue

        for group in common:
            src, tgt = group.split("\t")
            src_span = jdata["matches"][src]
            tgt_span = jdata["matches"][tgt]
            sent = jdata["sent"]
            sent = sent.replace("$", "")
            sent = sent.replace("^", "")

            # src entity mentioned before tgt entity
            if src_span[1] < tgt_span[0]:
                sent = sent[:src_span[0]] + "$" + src + "$" + sent[src_span[1]:tgt_span[0]] + "^" + tgt + "^" + sent[
                                                                                                                tgt_span[
                                                                                                                    1]:]
                rel_dir = 1

            # tgt entity mentioned before src entity
            elif src_span[0] > tgt_span[1]:
                sent = sent[:tgt_span[0]] + "^" + tgt + "^" + sent[tgt_span[1]:src_span[0]] + "$" + src + "$" + sent[
                                                                                                                src_span[
                                                                                                                    1]:]
                rel_dir = -1

            # Should not happen, but to be on safe side
            else:
                continue

            if group not in group_to_data:
                group_to_data[group] = collections.defaultdict(list)

            group_to_data[group][rel_dir].append(sent)

    # Adjust bag sizes
    new_group_to_data = dict()
    for group in list(group_to_data.keys()):
        src, tgt = group.split("\t")
        bag = list()
        for rel_dir in group_to_data[group]:
            bag.extend(group_to_data[group][rel_dir])
        if len(bag) > max_bag_size:
            bag = random.sample(bag, max_bag_size)
        else:
            idxs = list(np.random.choice(list(range(len(bag))), max_bag_size - len(bag)))
            bag = bag + [bag[i] for i in idxs]
        new_group_to_data["\t".join([src, tgt, "0"])] = {
            "relations": group_to_relation_texts[group],
            "bag": bag
        }
    group_to_data = new_group_to_data

    filtered_triples = set()
    for group in group_to_data:
        src, tgt, _ = group.split("\t")
        for relation in group_to_data[group]["relations"]:
            filtered_triples.add((src, relation, tgt))

    return filtered_triples, group_to_data


def remove_overlapping_sents(train_lines, dev_lines, test_lines):
    dev_test_sentences = set()
    for line in dev_lines:
        dev_test_sentences.update({s.replace("$", "").replace("^", "") for s in line["sentences"]})
    for line in test_lines:
        dev_test_sentences.update({s.replace("$", "").replace("^", "") for s in line["sentences"]})

    new_train_lines = list()

    for line in train_lines:
        new_sents = list()
        for sent in line["sentences"]:
            temp_sent = sent.replace("$", "").replace("^", "")
            if temp_sent not in dev_test_sentences:
                new_sents.append(sent)
        if not new_sents:
            continue
        bag = new_sents
        if len(bag) > config.bag_size:
            bag = random.sample(bag, config.bag_size)
        else:
            idxs = list(np.random.choice(list(range(len(bag))), config.bag_size - len(bag)))
            bag = bag + [bag[i] for i in idxs]
        line["sentences"] = bag
        new_train_lines.append(line)

    new_triples = set()

    for line in new_train_lines:
        src, tgt = line["group"]
        relation = line["relation"]
        new_triples.add((src, relation, tgt))

    return new_train_lines, new_triples


def create_data_split(triples):
    triples = list(triples)
    inds = list(range(len(triples)))
    y = [relation for _, relation, _ in triples]
    # train_dev test split
    train_dev_inds, test_inds = train_test_split(inds, stratify=y, test_size=0.2, random_state=config.SEED)
    y = [y[i] for i in train_dev_inds]
    train_inds, dev_inds = train_test_split(train_dev_inds, stratify=y, test_size=0.1, random_state=config.SEED)

    train_triples = [triples[i] for i in train_inds]
    dev_triples = [triples[i] for i in dev_inds]
    test_triples = [triples[i] for i in test_inds]

    logger.info(" *** Train triples : {} *** ".format(len(train_triples)))
    logger.info(" *** Dev triples : {} *** ".format(len(dev_triples)))
    logger.info(" *** Test triples : {} *** ".format(len(test_triples)))

    return train_triples, dev_triples, test_triples


def split_lines(triples, group_to_data):
    groups = set()
    for ei, _, ek in triples:
        groups.add("{}\t{}".format(ei, ek))
    lines = list()
    for group in groups:
        src, tgt = group.split("\t")
        G = ["\t".join([src, tgt, "0"]), ]
        for g in G:
            if g not in group_to_data:
                continue
            data = group_to_data[g]
            _, _, rel_dir = g.split("\t")
            rel_dir = int(rel_dir)
            for relation in data["relations"]:
                lines.append({
                    "group": (src, tgt),
                    "relation": relation,
                    "sentences": data["bag"],
                    "e1": data.get("e1", None), "e2": data.get("e2", None),
                    "reldir": rel_dir
                })
    return lines


def report_data_stats(lines, triples):
    stats = dict(
        num_of_groups=len(lines),
        num_of_sents=sum(len(line["sentences"]) for line in lines),
        num_of_triples=len(triples)
    )
    for k, v in stats.items():
        logger.info(" *** {} : {} *** ".format(k, v))


def write_final_jsonl_file(lines, output_fname):
    with open(output_fname, "w") as wf:
        for idx, line in enumerate(lines):
            wf.write(json.dumps(line) + "\n")


if __name__ == "__main__":
    # 0. Load UMLS vocab object
    logger.info("Loading UMLS vocab object `{}` ...".format(config.umls_cui_to_txts))
    with open(config.umls_cui_to_txts, "rb") as ctt, open(config.umls_reltxt_to_groups, "rb") as rttg:
        cui_to_entity_texts = pickle.load(ctt)
        relation_text_to_groups = pickle.load(rttg)
        ctt.close(), rttg.close()

    # 1. Collect all possible group texts from their CUIs
    groups_texts = get_groups_texts_from_umls_vocab(relation_text_to_groups, cui_to_entity_texts,
                                                    config.reltext_all_combos)

    # 2. Search for text alignment of groups (this can take up to 80~90 mins)
    pos_groups, neg_groups = align_groups_to_sentences(groups_texts, config.medline_linked_sents_file,
                                                       config.groups_linked_sents_file)

    # 3. From collected groups and pruning relations criteria, get final triples
    triples = pruned_triples(cui_to_entity_texts, relation_text_to_groups, pos_groups, neg_groups, config.min_rel_group,
                             config.max_rel_group)

    # 4. Collect evidences and filter triples based on sizes of collected bags
    triples, group_to_data = filter_triples_with_evidence(triples, config.bag_size)
    logger.info(" *** No. of triples (after filtering) *** : {}".format(len(triples)))

    E, R = set(), set()

    with open(config.triples_file_all, "w") as wf:
        for ei, rj, ek in triples:
            E.update([ei, ek])
            R.add(rj)
            line = "{}\t{}\t{}".format(ei, rj, ek)
            wf.write(line + '\n')

    with open(config.entities_file, "w") as wf:
        for e in E:
            wf.write("{}\n".format(e))

    with open(config.relations_file, "w") as wf:
        for r in R:
            wf.write("{}\n".format(r))

    logger.info(" *** No. of entities *** : {}".format(len(E)))
    logger.info(" *** No. of relations *** : {}".format(len(R)))

    # 5. Split into train, dev and test at triple level to keep zero triples overlap
    train_triples, dev_triples, test_triples = create_data_split(triples)
    train_lines = split_lines(train_triples, group_to_data)
    dev_lines = split_lines(dev_triples, group_to_data)
    test_lines = split_lines(test_triples, group_to_data)

    # Remove any overlapping test and dev sentences from training
    logger.info("Train stats before removing overlapping sentences ...")
    report_data_stats(train_lines, train_triples)
    train_lines, train_triples = remove_overlapping_sents(train_lines, dev_lines, test_lines)

    # Write triples file and final combined file
    logger.info("Train stats after removing dev + test overlapping sentences ...")
    triples_splits = [
        (config.complete_train, config.triples_file_train, train_triples, train_lines, "TRAIN"),
        (config.complete_dev, config.triples_file_dev, dev_triples, dev_lines, "DEV"),
        (config.complete_test, config.triples_file_test, test_triples, test_lines, "TEST")
    ]
    for complete_file, trip_file, trips, lines, split_name in triples_splits:
        print(split_name)
        report_data_stats(lines, trips)
        with open(trip_file, "w") as wf:
            for ei, rj, ek in trips:
                wf.write("{}\t{}\t{}\n".format(ei, rj, ek))

        # 6. Write train, dev, test files with sentence, group and relation
        logger.info("Creating training file at `{}` ...".format(complete_file))
        write_final_jsonl_file(lines, complete_file)
