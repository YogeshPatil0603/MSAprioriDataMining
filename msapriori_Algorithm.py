'''
MS-Apriori algorithm implementation with constraints for Must-Have items and Cannot-be-together items.
Author : Rohan Tadphale (UIN: 657662650) and Yogesh Patil (UIN: 668632704)
'''

import sys
import operator

mis_data = {}  # MIS data will be stored in dictionary.
input_data = []  # input data will be stored in a list.
constraint = []  # constraints such as must-have and no-together will be stored in a list.


# scan data and record the support count of an itemset in the data.
def support_seq(seq, data):
	n = 0
	for i in data:
		for j in seq:
			if j not in i:
				break
		else:
			n = n + 1
	return n

# count the support of one item in the data.
def support_count(item, data):
	n = 0
	for i in data:
		if item in i:
			n = n + 1
	return n


# check whether an itemset contains any must-having item.
def isMust_have(must_h, itemset):
	for i in must_h:
		if i in itemset:
			return True
	return False


# sort all items in a set according to each item's MIS value.
def sort_items(data, mis):
	seq = {}
	for i in mis.keys():
		for j in data:
			if i in j:
				seq[i] = mis[i]
	sorted_items = sorted(seq.items(), key=operator.itemgetter(1))
	return sorted_items  # sorted items are stored in a list and each item is built as (item, MIS(item)).


# First scan the data and store all items whose support count is bigger than the MIS value of the first item whose support count >= MIS value in an ordered itemset.
def init_pass(sort, data):
	n = len(data)
	L = []
	for i in sort:  # i is tuple.
		if support_count(i[0], data) >= (n * mis_data[i[0]]):
			# find the first item in sorted items whose support count is not smaller than its mis value. And store it in L as the first one.
			L.append(i[0])
			p = sort.index(i)
			sort_after = sort[p + 1:len(sort)]
			for j in sort_after:  # insert all item after the first one in order whose support count is bigger than mis value of the first one.
				if support_count(j[0], data) >= (n * mis_data[L[0]]):
					L.append(j[0])
			return L


# level2-candidate-gen function: It takes an argument L and returns a superset of the set of all frequent 2-itemsets.
def candidate_gen_level2(L, sdc):
	n = len(input_data)
	C2 = []
	for l in L:
		if support_count(l, input_data) >= (mis_data[l] * n):
			L0 = []
			p = L.index(l)
			L0 = L[p + 1:len(L)]
			for h in L0:
				if support_count(h, input_data) >= (mis_data[l] * n) and abs(
						support_count(h, input_data) - support_count(l, input_data)) <= (n * sdc):
					c = []
					c = [l, h]
					# if isMust_have(must_h,c):
					# if not is_together(c,no_together):
					C2.append(c)
	return C2


# Frequent 1-itemsets F1 are obtained from L.
def F_1(L, must_have):
	F1 = []
	n = len(input_data)
	for l in L:
		if support_count(l, input_data) >= (mis_data[l] * n):
			if l in must_have:
				F1.append([l])
	return F1


# find all subsets from an itemsets. Each subset is shorter than the itemsets by one item.
def subsets(itemset):
	subset = []
	for i in itemset:
		j = []
		p = itemset.index(i)
		j = itemset[:p] + itemset[p + 1:]
		subset.append(j)
	return subset


# MScandidate-gen function:
def MScandidate_gen(F, sdc):
	C = []
	n = len(input_data)
	# join step:
	for i in F:
		for j in F:
			if i[0:-1] == j[0:-1] and i[-1] < j[-1] and abs(
					support_count(i[-1], input_data) - support_count(j[-1], input_data)) <= (n * sdc):
				c = []
				c = i[:]
				c.append(j[-1])
				C.append(c)
	# prune step:
	for k in C:
		p = C.index(k)
		subset = []
		subset = subsets(k)
		for j in subset:
			if k[0] in j or mis_data[k[0]] == mis_data[k[1]]:
				if j not in F:
					del C[p]
					break
	return C


# Frequent k-itemsets are obtained from C(k). Here k is not smaller than 2.
def F_k(C_k, mis, data, must_h, no_together):
	Freq_k = []
	n = len(data)
	for c in C_k:
		if isMust_have(must_h, c):  # check the candidate whether meets the constraints.
			n2 = len(no_together)
			i = 0
			while i < n2:
				if is_together(c, no_together[i]):
					break
				i += 1
			if i == n2:
				if support_seq(c, data) >= n * mis_data[c[0]]:
						Freq_k.append(c)

	return Freq_k


# check whether an itemset has any no-together itemset.
def is_together(itemset, no_together):
	n = 0
	bound = len(no_together)
	for i in no_together:
		if i in itemset:
			n = n + 1
		if n == bound:
			return True
	return False


# Format the output as per the given output format.
def display_op(freq_items, data):
	freq_items = freq_items[1:]
	for i in freq_items:
		n = freq_items.index(i) + 1
		print('Frequent %d-itemsets \n' % n)

		for j in i:
			j_output = '{' + str(j).strip('[]') + '}'
			print('\t%d : %s' % (support_seq(j, data), j_output))  # the support count of the itemsets.

			if len(j) > 1:
				j_tail = j[1:]
				j_tailcount = support_seq(j_tail, data)  # Tailcount
				print('Tailcount = %d' % j_tailcount)
		print('\n\tTotal number of frequent %d-itemsets = %d\n\n' % (n, len(i)))


def main():
	sort = []
	L = []
	C2 = []
	C_sets = []
	F_sets = []
	r1 = [] # to get multiple 'cannot be together's
	no_together_List = []

	# READ PARAM FILE
	with open(sys.argv[2]) as f:
		for line in f:
			line = line.rstrip()
			if "=" in line:
				key, value = line.split(" = ")
				if key[0:3] == 'MIS':
					key = key[4:-1]
				mis_data[key] = float(value)
			if ":" in line:
				a, b = line.split(": ")
				if a == 'cannot_be_together':
					b = b[1:-1]
					blist = b.split("}, {")
					i = 0
					while i < len(blist):
						r1 = blist[i].split(", ")
						no_together_List.append(r1)
						i += 1
					constraint.append(no_together_List)

				if a == 'must-have':
					b = b[:]
					b = b.split(" or ")
					constraint.append(b[:])

	#READ TXN FILE
	with open(sys.argv[1]) as f:
		for line in f:
			l = list(line)
			p1 = l.index("{")
			p2 = l.index("}")
			line = line[p1 + 1:p2]
			list0 = line.split(", ")  # each item in one sequence is stored in a list
			input_data.append(list0)

	no_together = constraint[0]
	must_h = constraint[1]

	sort = sort_items(input_data, mis_data)
	L = init_pass(sort, input_data)  # Make the first pass over T and produce the seeds L.
	F_sets.append(L)  # The seeds L is stored in the F_sets at first.
	F_sets.append(F_1(L, must_h))  # the 1-itemsets F_1 is inserted in the F_sets.
	# f_sets[0] is L. c_k starts with c2.
	for i in range(2, 100, 1):
		# Algorithm creates an empty list of f_sets before stopping execution. This step checks if there is an empty list appended to f_sets.
		# if there is then it will delete the last list. also we need to delete the last c_k set as it will be empty s well.
		if not F_sets[i - 1]:
			del F_sets[-1]
			if len(C_sets) >= 1:
				del C_sets[-1]
			break
		else:  # when F_k-1 is not empty
			if i <= 2:  # To generate 2-itemsets candidates.
				C2 = candidate_gen_level2(L, mis_data['SDC'])
				C_sets.append(C2)
			else:
				# To generate k-itemets(k>2) candidates.
				C_sets.append(MScandidate_gen(F_sets[i - 1], mis_data['SDC']))

			F_sets.append(F_k(C_sets[i - 2], mis_data, input_data, must_h,
							  no_together))  # F_sets is the set of all Frequent itemsets.

	display_op(F_sets, input_data)  # Print all Freq. itemsets.


if __name__ == "__main__":
	main()
