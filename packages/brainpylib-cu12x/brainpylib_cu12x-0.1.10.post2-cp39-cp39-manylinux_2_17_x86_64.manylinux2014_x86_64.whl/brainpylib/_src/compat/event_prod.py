# -*- coding: utf-8 -*-

__all__ = [
  'csr_event_prod',
]

from functools import partial

import jax.numpy as jnp
import numpy as np
from jax import core
from jax.interpreters import xla
from jax.lib import xla_client
from brainpylib._src.errors import GPUOperatorNotFound
from brainpylib._src.tools import transform_brainpy_array

try:
  from brainpylib import gpu_ops
except ImportError:
  gpu_ops = None

x_shape = xla_client.Shape.array_shape
x_ops = xla_client.ops

csr_event_prod_p1 = core.Primitive("csr_event_prod")


def csr_event_prod(events, pre2post, post_num, values):
  events = transform_brainpy_array(events)
  post_num = transform_brainpy_array(post_num)
  values = transform_brainpy_array(values)
  indices, indptr = pre2post
  indices = transform_brainpy_array(indices)
  indptr = transform_brainpy_array(indptr)
  # events
  if events.dtype != jnp.bool_:
    raise ValueError(f'"events" must be a vector of bool, while we got {events.dtype}')

  # connections
  if len(events) + 1 != len(indptr):
    raise ValueError(f'The length of "events" must be equal to "len(pre2post[1]) - 1", '
                     f'while we get: {len(events)} + 1 != {len(indptr)}')
  if indices.dtype != indptr.dtype:
    raise ValueError(f"The dtype of pre2post[0] must be equal to that of pre2post[1], "
                     f"while we got {(indices.dtype, indptr.dtype)}")
  if not jnp.issubdtype(indices.dtype, jnp.integer):
    raise ValueError(f'The dtype of pre2post must be a subtype of integer, while we got {indices.dtype}')

  # output value
  if np.ndim(values) == 0:
    values = jnp.asarray([values])
  if values.dtype not in [jnp.float32, jnp.float64]:
    raise ValueError(f'The dtype of "values" must be float32 or float64, while we got {values.dtype}.')
  if values.size not in [1, indices.size]:
    raise ValueError(f'The size of "values" must be 1 (a scalar) or len(pre2post[0]) (a vector), '
                     f'while we got {values.size} != 1 != {indices.size}')
  # bind operator
  return csr_event_prod_p1.bind(events, indices, indptr, values, post_num=post_num)


def _event_prod_abstract(events, indices, indptr, values, *, post_num):
  return core.ShapedArray(dtype=values.dtype, shape=(post_num,))


csr_event_prod_p1.def_abstract_eval(_event_prod_abstract)
csr_event_prod_p1.def_impl(partial(xla.apply_primitive, csr_event_prod_p1))


def _event_prod_translation(c, events, indices, indptr, values, *, post_num, platform="cpu"):
  # The pre/post shape
  pre_size = np.array(c.get_shape(events).dimensions()[0], dtype=np.uint32)
  _pre_shape = x_shape(np.dtype(np.uint32), (), ())
  _post_shape = x_shape(np.dtype(np.uint32), (), ())

  # The indices shape
  indices_shape = c.get_shape(indices)
  Itype = indices_shape.element_type()
  assert np.issubdtype(Itype, np.integer)

  # The value shape
  values_shape = c.get_shape(values)
  Ftype = values_shape.element_type()
  assert Ftype in [np.float32, np.float64]
  values_dim = values_shape.dimensions()

  # We dispatch a different call depending on the dtype
  f_type = b'_f32' if Ftype == np.float32 else b'_f64'
  i_type = b'_i32' if Itype in [np.uint32, np.int32, jnp.uint32, jnp.int32] else b'_i64'

  # And then the following is what changes between the GPU and CPU
  if platform == "cpu":
    v_type = b'_csr_event_prod_homo' if values_dim[0] == 1 else b'_csr_event_prod_heter'
    return x_ops.CustomCallWithLayout(
      c, platform.encode() + v_type + f_type + i_type,
      operands=(x_ops.ConstantLiteral(c, pre_size),
                x_ops.ConstantLiteral(c, post_num),
                events,
                indices,
                indptr,
                values),
      operand_shapes_with_layout=(_pre_shape,
                                  _post_shape,
                                  c.get_shape(events),
                                  c.get_shape(indices),
                                  c.get_shape(indptr),
                                  c.get_shape(values)),
      shape_with_layout=x_shape(np.dtype(Ftype), (post_num,), (0,)),
    )
  elif platform == 'gpu':
    if gpu_ops is None:
      raise GPUOperatorNotFound(csr_event_prod_p1.name)
    v_type = b'_csr_event_prod_homo' if values_dim[0] == 1 else b'_csr_event_prod_heter'
    opaque = gpu_ops.build_csr_event_prod_descriptor(pre_size, post_num)
    return x_ops.CustomCallWithLayout(
      c, platform.encode() + v_type + f_type + i_type,
      operands=(events,
                indices,
                indptr,
                values),
      operand_shapes_with_layout=(c.get_shape(events),
                                  c.get_shape(indices),
                                  c.get_shape(indptr),
                                  c.get_shape(values)),
      shape_with_layout=x_shape(np.dtype(Ftype), (post_num,), (0,)),
      opaque=opaque,
    )

  else:
    raise ValueError("Unsupported platform, we only support 'cpu' or 'gpu'")


xla.backend_specific_translations["cpu"][csr_event_prod_p1] = partial(_event_prod_translation, platform="cpu")
xla.backend_specific_translations["gpu"][csr_event_prod_p1] = partial(_event_prod_translation, platform="gpu")


