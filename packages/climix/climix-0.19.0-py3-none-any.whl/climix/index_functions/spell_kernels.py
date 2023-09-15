from collections import namedtuple

import numpy as np
from numba import jit

Kernels = namedtuple(
    "Kernels", ["chunk", "aggregate", "combine", "post_process"], defaults=[None, None]
)


def make_first_spell_kernels(minimum_length):
    # The gufunc support in numba is lacking right now.
    # Once numba supports NEP-20 style signatures for
    # gufunc, we can use @guvectorize to vectorize this
    # function, allowing for more general applicability
    # in terms of dimensions and hopefully better performance,
    # perhaps taking advantage of GPUs. The template is
    # @guvectorize([float32, int64], '(n)->(4)')
    # def chunk_column(column, res):
    @jit(nopython=True)
    def chunk_column(column):
        """Calculate first spell information for a single timeseries.

        Parameters
        ----------
        column : np.array
            1d array containing the timeseries

        Returns
        -------
        np.array
            4 vector containing the first spell information, namely:
            - length of timeseries
            - length of spell at beginning
            - position of first spell in the timeseries
            - length of spell at the end
        """
        res = np.empty((4,), dtype=np.int64)
        n = column.shape[0]
        where = np.flatnonzero
        x = column[1:] != column[:-1]
        starts = where(x) + 1
        no_runs = len(starts)
        # the length of the chunk is n
        res[0] = n
        # assume no internal spell
        res[2] = -1
        # if no change occurs, then...
        if no_runs == 0:
            # ...either the spell covers the entire chunk, or...
            if column[0]:
                res[1] = n
                if n >= minimum_length:
                    res[2] = 0
                res[3] = n
            # ...there is no spell in this chunk
            else:
                res[1] = 0
                res[3] = 0
        else:
            # there is a spell from the beginning to the first change
            # if the first value is part of a spell
            res[1] = starts[0] if column[0] else 0
            # there is a spell from the last change to the end if
            # the last value is part of a spell
            res[3] = n - starts[-1] if column[starts[-1]] else 0
            # if there is a sufficiently long spell at the beginning, we're done
            if res[1] >= minimum_length:
                res[2] = 0
                return res
            # if there is a sufficiently long spell at the end,
            # we don't need to look at more chunks in the aggregation
            if res[3] >= minimum_length:
                res[2] = starts[-1]
            # if there are at least two changes (range(1) = [0])
            for k in range(no_runs - 1):
                # if the value at the corresponding change is part
                # of a spell then this spell stretches to the next
                # change and is an internal spell
                if column[starts[k]]:
                    length = starts[k + 1] - starts[k]
                    if length >= minimum_length:
                        res[2] = starts[k]
                        return res
        return res

    @jit(nopython=True)
    def chunk(thresholded_data):
        res = np.empty(thresholded_data.shape[:-1] + (4,), dtype=np.int64)
        for ind in np.ndindex(*thresholded_data.shape[:-1]):
            res[ind] = chunk_column(thresholded_data[ind])
        return res

    @jit(nopython=True)
    def aggregate(x_chunk):
        # start with the first chunk and merge all others subsequently
        res = x_chunk[0].copy()
        # mark where this chunk is completely covered by a spell
        this_full = np.asarray(res[..., 0] == res[..., 1])
        for k in range(1, x_chunk.shape[0]):
            next_chunk = x_chunk[k]
            for ind in np.ndindex(res.shape[:-1]):
                ind_length = ind + (0,)
                ind_head = ind + (1,)
                ind_internal = ind + (2,)
                ind_tail = ind + (3,)
                # the next chunk is completely covered by a spell
                next_full = next_chunk[ind_length] == next_chunk[ind_head]
                # if both are completely covered the merged chunk
                # is completely covered too
                if this_full[ind] and next_full:
                    res[ind_head] += next_chunk[ind_head]
                    res[ind_tail] += next_chunk[ind_tail]
                    if res[ind_head] >= minimum_length:
                        res[ind_internal] = 0
                # if the old chunk is completely covered, but the new one
                # isn't, then
                elif this_full[ind]:
                    # the head is the old head + the new head,
                    res[ind_head] += next_chunk[ind_head]
                    # the internal spell is the new internal spell,
                    if res[ind_head] >= minimum_length:
                        res[ind_internal] = 0
                    else:
                        res[ind_internal] = res[ind_length] + next_chunk[ind_internal]
                    # the tail is the new tail,
                    res[ind_tail] = next_chunk[ind_tail]
                    # and the resulting chunk is no longer fully covered
                    this_full[ind] = False
                # if the old chunk is not fully covered, but the new one is
                elif next_full:
                    old_tail = res[ind_tail]
                    # the tail is the old tail + the new head
                    res[ind_tail] += next_chunk[ind_head]
                    if res[ind_tail] >= minimum_length and res[ind_internal] == -1:
                        res[ind_internal] = res[ind_length] - old_tail
                # if neither are fully covered
                else:
                    # the head stays the same,
                    # the internal spell is the winner between
                    # the old internal spell, the new internal spell,
                    # and the internal spell resulting from merging
                    # old tail and new head,
                    if res[ind_internal] == -1:
                        length = res[ind_tail] + next_chunk[ind_head]
                        if length >= minimum_length:
                            res[ind_internal] = res[ind_length] - res[ind_tail]
                        elif next_chunk[ind_internal] != -1:
                            res[ind_internal] = (
                                res[ind_length] + next_chunk[ind_internal]
                            )
                    # and the tail is the new tail
                    res[ind_tail] = next_chunk[ind_tail]
                # the length of the combined chunks is the sum of the
                # lengths of the individual chunks
                res[ind_length] += next_chunk[ind_length]
        return res

    return Kernels(chunk, aggregate)


def make_spell_length_kernels(reducer):
    # The gufunc support in numba is lacking right now.
    # Once numba supports NEP-20 style signatures for
    # gufunc, we can use @guvectorize to vectorize this
    # function, allowing for more general applicability
    # in terms of dimensions and hopefully better performance,
    # perhaps taking advantage of GPUs. The template is
    # @guvectorize([float32, int64], '(n)->(4)')
    # def chunk_column(column, res):
    @jit(nopython=True)
    def chunk_column(column):
        res = np.empty((4,), dtype=np.int64)
        n = column.shape[0]
        where = np.flatnonzero
        x = column[1:] != column[:-1]
        starts = where(x) + 1
        no_runs = len(starts)
        # the length of the chunk is n
        res[0] = n
        # assume no internal spell
        res[2] = 0
        # if no change occurs, then...
        if no_runs == 0:
            # ...either the spell covers the entire chunk, or...
            if column[0]:
                res[1] = n
                res[3] = n
            # ...there is no spell in this chunk
            else:
                res[1] = 0
                res[3] = 0
        else:
            # there is a spell from the beginning to the first change
            # if the first value is part of a spell
            res[1] = starts[0] if column[0] else 0
            # there is a spell from the last change to the end if
            # the last value is part of a spell
            res[3] = n - starts[-1] if column[starts[-1]] else 0
            # if there are at least two changes (range(1) = [0])
            for k in range(no_runs - 1):
                # if the value at the corresponding change is part
                # of a spell then this spell stretches to the next
                # change and is an internal spell
                if column[starts[k]]:
                    length = starts[k + 1] - starts[k]
                    res[2] = reducer(length, res[2])
        return res

    @jit(nopython=True)
    def chunk(thresholded_data):
        res = np.empty(thresholded_data.shape[:-1] + (4,), dtype=np.int64)
        for ind in np.ndindex(*thresholded_data.shape[:-1]):
            res[ind] = chunk_column(thresholded_data[ind])
        return res

    @jit(nopython=True)
    def aggregate(x_chunk):
        # start with the first chunk and merge all others subsequently
        res = x_chunk[0].copy()
        # mark where this chunk is completely covered by a spell
        this_full = np.asarray(res[..., 0] == res[..., 1])
        for k in range(1, x_chunk.shape[0]):
            next_chunk = x_chunk[k]
            for ind in np.ndindex(res.shape[:-1]):
                ind_length = ind + (0,)
                ind_head = ind + (1,)
                ind_internal = ind + (2,)
                ind_tail = ind + (3,)
                # the next chunk is completely covered by a spell
                next_full = next_chunk[ind_length] == next_chunk[ind_head]
                # the length of the combined chunks is the sum of the
                # lengths of the individual chunks
                res[ind_length] += next_chunk[ind_length]
                # if both are completely covered the merged chunk
                # is completely covered too
                if this_full[ind] and next_full:
                    res[ind_head] += next_chunk[ind_head]
                    res[ind_tail] += next_chunk[ind_tail]
                # if the old chunk is completely covered, but the new one
                # isn't, then
                elif this_full[ind]:
                    # the head is the old head + the new head,
                    res[ind_head] += next_chunk[ind_head]
                    # the internal spell is the new internal spell,
                    res[ind_internal] = next_chunk[ind_internal]
                    # the tail is the new tail,
                    res[ind_tail] = next_chunk[ind_tail]
                    # and the resulting chunk is no longer fully covered
                    this_full[ind] = False
                # if the old chunk is not fully covered, but the new one is
                elif next_full:
                    # the tail is the old tail + the new head
                    res[ind_tail] += next_chunk[ind_head]
                # if neither are fully covered
                else:
                    # the head stays the same,
                    # the internal spell is the winner between
                    # the old internal spell, the new internal spell,
                    # and the internal spell resulting from merging
                    # old tail and new head,
                    res[ind_internal] = reducer(
                        res[ind_internal],
                        res[ind_tail] + next_chunk[ind_head],
                        next_chunk[ind_internal],
                    )
                    # and the tail is the new tail
                    res[ind_tail] = next_chunk[ind_tail]
        return res

    return Kernels(chunk, aggregate)
