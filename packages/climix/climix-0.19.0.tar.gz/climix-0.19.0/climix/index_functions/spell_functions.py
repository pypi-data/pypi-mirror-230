from cf_units import Unit
import dask.array as da
import numpy as np

from .spell_kernels import make_first_spell_kernels, make_spell_length_kernels
from .support import normalize_axis, IndexFunction, ThresholdMixin, ReducerMixin


class FirstSpell(ThresholdMixin, IndexFunction):
    def __init__(self, threshold, condition, duration, dead_period):
        super().__init__(threshold, condition, units=Unit("days"))
        self.duration = duration
        self.dead_period = dead_period
        self.kernels = make_first_spell_kernels(duration.points[0])

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        raise NotImplementedError

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        data = da.moveaxis(data, axis, -1)
        offset = self.dead_period.points[0]
        data = data[..., offset:]
        first_spell_data = da.reduction(
            data,
            self.chunk,
            self.aggregate,
            keepdims=True,
            output_size=4,
            axis=-1,
            dtype=int,
            concatenate=False,
            meta=np.array((), dtype=int),
        )
        res = first_spell_data[..., 2].copy()
        res = da.where(res >= 0, res - offset, res)
        res = da.ma.masked_array(da.ma.getdata(res), mask)
        return res.astype("float32")

    def chunk(self, raw_data, axis, keepdims, computing_meta=False):
        if computing_meta:
            return np.array((), dtype=int)

        data = self.condition(raw_data, self.threshold.points)
        data = np.ma.filled(data, fill_value=False)
        chunk_res = self.kernels.chunk(data)
        return chunk_res

    def aggregate(self, x_chunk, axis, keepdims):
        if not isinstance(x_chunk, list):
            return x_chunk
        res = self.kernels.aggregate(np.array(x_chunk))
        return res


class SpellLength(ThresholdMixin, ReducerMixin, IndexFunction):
    def __init__(self, threshold, condition, statistic, fuse_periods=False):
        super().__init__(threshold, condition, statistic, units=Unit("days"))
        self.spanning_spells = True
        self.kernels = make_spell_length_kernels(self.scalar_reducer)
        self.fuse_periods = fuse_periods

    def pre_aggregate_shape(self, *args, **kwargs):
        return (4,)

    def call_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = np.ma.getmaskarray(data).any(axis=axis)
        res = np.apply_along_axis(self, axis=axis, arr=data)
        res = np.ma.masked_array(np.ma.getdata(res), mask)
        return res.astype("float32")

    def lazy_func(self, data, axis, **kwargs):
        axis = normalize_axis(axis, data.ndim)
        mask = da.ma.getmaskarray(data).any(axis=axis)
        data = da.moveaxis(data, axis, -1)
        res = da.reduction(
            data,
            self.chunk,
            self.aggregate,
            keepdims=True,
            output_size=4,
            axis=-1,
            dtype=int,
            concatenate=False,
            meta=np.array((), dtype=int),
        )
        res = da.ma.masked_array(
            da.ma.getdata(res), np.broadcast_to(mask[..., np.newaxis], res.shape)
        )
        return res.astype("float32")

    def chunk(self, raw_data, axis, keepdims, computing_meta=False):
        if computing_meta:
            return np.array((), dtype=int)

        data = self.condition(raw_data, self.threshold.points)
        data = np.ma.filled(data, fill_value=False)
        chunk_res = self.kernels.chunk(data)
        return chunk_res

    def aggregate(self, x_chunk, axis, keepdims):
        if not isinstance(x_chunk, list):
            return x_chunk
        res = self.kernels.aggregate(np.array(x_chunk))
        return res

    def post_process(self, cube, data, coords, period, **kwargs):
        def fuse(this, previous_tail):
            own_mask = da.ma.getmaskarray(this[..., 0])
            own_length = this[..., 0]
            own_head = this[..., 1]
            internal = this[..., 2]
            own_tail = this[..., 3]
            head = da.where(own_head, previous_tail + own_head, 0.0)
            tail = da.where(own_length == own_head, previous_tail + own_tail, own_tail)
            stack = da.stack([head, internal, tail], axis=-1)
            spell_length = da.ma.masked_array(
                self.lazy_reducer(stack, axis=-1), own_mask
            )
            return spell_length, tail

        if self.fuse_periods and len(data) > 1:
            stack = []
            this = data[0]
            slice_shape = this.shape[:-1]
            previous_tail = da.ma.masked_array(
                da.zeros(slice_shape, dtype=np.float32),
                da.ma.getmaskarray(data[0, ..., 3]),
            )

            for next_chunk in data[1:]:
                spell_length, previous_tail = fuse(this, previous_tail)
                stack.append(spell_length)
                this = next_chunk

            stack.append(fuse(next_chunk, previous_tail)[0])
            res_data = da.stack(stack, axis=0)
        else:
            res_data = self.lazy_reducer(data[..., 1:], axis=-1)
        return cube, res_data
