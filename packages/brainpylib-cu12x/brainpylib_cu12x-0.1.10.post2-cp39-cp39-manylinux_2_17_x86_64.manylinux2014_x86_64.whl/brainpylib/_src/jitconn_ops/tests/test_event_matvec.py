# -*- coding: utf-8 -*-

import brainpy.math as bm
import jax
import jax.numpy as jnp
from absl.testing import parameterized

import brainpylib as bl

shapes = [(100, 200),
          (10, 1000),
          (2, 1000),
          (1000, 10),
          (1000, 2)]


class Test_event_matvec_prob_conn(parameterized.TestCase):
  def __init__(self, *args, platform='cpu', **kwargs):
    super(Test_event_matvec_prob_conn, self).__init__(*args, **kwargs)
    bm.set_platform(platform)
    print()

  @parameterized.named_parameters(
    dict(testcase_name=f'_test_homo: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, '
                       f'homo_data = {homo_data}, '
                       f'bool_event = {bool_event}, '
                       f'x64={x64}',
         shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         homo_data=homo_data,
         bool_event=bool_event, seed=1234, x64=x64)
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1, 0.5]
    for homo_data in [-1., ]
    for bool_event in [True, False]
  )
  def test_homo(self, shape, transpose, outdim_parallel, prob, homo_data, bool_event=True, seed=None, x64=False):
    print(f'_test_homo: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, '
          f'homo_data = {homo_data}, '
          f'bool_event = {bool_event}, '
          f'x64={x64}')

    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = bm.as_jax(rng.random(shape[0] if transpose else shape[1])) < 0.1
    if not bool_event:
      events = events.astype(float)

    r1 = bl.jitconn_ops.event_matvec_prob_conn_homo_weight(events,
                                                           homo_data,
                                                           conn_prob=prob,
                                                           shape=shape,
                                                           seed=seed,
                                                           outdim_parallel=outdim_parallel,
                                                           transpose=transpose)

    r2 = bl.jitconn_ops.event_matvec_prob_conn_homo_weight(events,
                                                           homo_data,
                                                           conn_prob=prob,
                                                           shape=shape,
                                                           seed=seed,
                                                           outdim_parallel=outdim_parallel,
                                                           transpose=transpose)
    self.assertTrue(jnp.allclose(r1, r2))

    r3 = bl.jitconn_ops.event_matvec_prob_conn_homo_weight(events,
                                                           homo_data,
                                                           conn_prob=prob,
                                                           shape=(shape[1], shape[0]),
                                                           seed=seed,
                                                           outdim_parallel=outdim_parallel,
                                                           transpose=not transpose)
    self.assertTrue(jnp.allclose(r1, r3))

    # indices, indptr = bp.conn.FixedProb(prob)(*shape).require('pre2post')
    # indices = bm.as_jax(indices)
    # indptr = bm.as_jax(indptr)
    # r3 = event_ops.event_csr_matvec(homo_data, indices, indptr, events,
    #                                 shape=shape, transpose=transpose)
    # print('Homo difference: ', bm.abs(r1 - r3).sum() / r1.size)

    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(testcase_name=f'_test_homo_vmap: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, '
                       f'bool_event = {bool_event}, x64={x64}',
         shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         x64=x64,
         bool_event=bool_event,
         seed=1234)
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1, 0.5]
    for bool_event in [True, False]

  )
  def test_homo_vmap(self, shape, transpose, outdim_parallel, prob, bool_event=True, seed=None, x64=False):
    print(f'_test_homo_vmap: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, '
          f'bool_event = {bool_event}, '
          f'x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random((10, shape[0] if transpose else shape[1])) < 0.1
    events = bm.as_jax(events)
    if not bool_event:
      events = events.astype(float)
    weights = bm.as_jax(rng.random(10))

    f1 = jax.vmap(
      lambda event, data: bl.jitconn_ops.event_matvec_prob_conn_homo_weight(
        event, data, conn_prob=prob, shape=shape, seed=seed,
        transpose=transpose, outdim_parallel=outdim_parallel
      )
    )
    r1 = f1(events, weights)
    r2 = f1(events, weights)
    self.assertTrue(jnp.allclose(r1, r2))
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(testcase_name=f'_test_homo_grad: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, x64={x64}',
         shape=shape, transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob, seed=1234,
         x64=x64)
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1, 0.5]
  )
  def test_homo_grad(self, shape, transpose, outdim_parallel, prob, seed=None, x64=False):
    print(f'_test_homo_grad: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random(shape[0] if transpose else shape[1]) < 0.5
    events = bm.as_jax(events)
    events = events.astype(float)

    f1 = jax.grad(
      lambda event, data: bl.jitconn_ops.event_matvec_prob_conn_homo_weight(
        event, data, conn_prob=prob, shape=shape, seed=seed,
        outdim_parallel=outdim_parallel, transpose=transpose
      ).sum(),
      argnums=0
    )
    r1 = f1(events, 1.)

    f2 = jax.grad(
      lambda event, data: bl.jitconn_ops.event_matvec_prob_conn_homo_weight(
        event, data, conn_prob=prob, shape=shape, seed=seed,
        transpose=transpose, outdim_parallel=outdim_parallel
      ).sum(),
      argnums=1
    )
    r2 = f2(events, 1.)

    f3 = jax.grad(
      lambda event, data: bl.jitconn_ops.event_matvec_prob_conn_homo_weight(
        event, data, conn_prob=prob, shape=shape, seed=seed,
        outdim_parallel=outdim_parallel, transpose=transpose
      ).sum(),
      argnums=(0, 1)
    )
    r3 = f3(events, 1.)

    self.assertTrue(jnp.allclose(r1, r3[0]))
    self.assertTrue(jnp.allclose(r2, r3[1]))
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(testcase_name=f'test_uniform: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, '
                       f'w_low = {w_low}, '
                       f'w_high = {w_high}, '
                       f'bool_event = {bool_event}, '
                       f'x64={x64}',
         shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         w_low=w_low,
         w_high=w_high,
         bool_event=bool_event,
         seed=1234,
         x64=x64
         )
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1, 0.4]
    for w_low, w_high in [(-1., 0.), (0., 1.), (-1., 1.)]
    for bool_event in [True, False]
  )
  def test_uniform(self, shape, transpose, outdim_parallel, prob, w_low, w_high,
                   bool_event=True, seed=None, x64=False):
    print(f'_test_uniform: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, '
          f'w_low = {w_low}, '
          f'w_high = {w_high}, '
          f'x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random(shape[0] if transpose else shape[1]) < 0.1
    events = bm.as_jax(events)
    if not bool_event:
      events = events.astype(float)

    r1 = bl.jitconn_ops.event_matvec_prob_conn_uniform_weight(events,
                                                              w_low=w_low,
                                                              w_high=w_high,
                                                              conn_prob=prob,
                                                              shape=shape,
                                                              seed=seed,
                                                              outdim_parallel=outdim_parallel,
                                                              transpose=transpose)

    r2 = bl.jitconn_ops.event_matvec_prob_conn_uniform_weight(events,
                                                              w_low=w_low,
                                                              w_high=w_high,
                                                              conn_prob=prob,
                                                              shape=shape,
                                                              seed=seed,
                                                              outdim_parallel=outdim_parallel,
                                                              transpose=transpose)
    self.assertTrue(jnp.allclose(r1, r2))

    r3 = bl.jitconn_ops.event_matvec_prob_conn_uniform_weight(events,
                                                              w_low=w_low,
                                                              w_high=w_high,
                                                              conn_prob=prob,
                                                              shape=(shape[1], shape[0]),
                                                              seed=seed,
                                                              outdim_parallel=outdim_parallel,
                                                              transpose=not transpose)
    self.assertTrue(jnp.allclose(r1, r3))
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(shape=shape, transpose=transpose,
         outdim_parallel=outdim_parallel, prob=prob,
         bool_event=bool_event,
         x64=x64,
         seed=1234,
         testcase_name=f'_test_uniform_vmap: '
                       f'shape={shape}, '
                       f'transpose={transpose}, '
                       f'bool_event={bool_event}, '
                       f'outdim_parallel={outdim_parallel}, '
                       f'prob={prob}, '
                       f'x64={x64}')
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1]
    for bool_event in [True, False]
  )
  def test_uniform_vmap(self, shape, transpose, outdim_parallel, prob,
                        bool_event=True, seed=None, x64=False):
    print(f'_test_uniform_vmap: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random((10, shape[0] if transpose else shape[1])) < 0.1
    events = bm.as_jax(events)
    if not bool_event:
      events = events.astype(float)

    f1 = jax.vmap(
      lambda e: bl.jitconn_ops.event_matvec_prob_conn_uniform_weight(e,
                                                                     w_low=0.,
                                                                     w_high=1.,
                                                                     conn_prob=prob,
                                                                     shape=shape,
                                                                     seed=seed,
                                                                     outdim_parallel=outdim_parallel,
                                                                     transpose=transpose)
    )

    r1 = f1(events)
    r2 = f1(events)
    self.assertTrue(jnp.allclose(r1, r2))
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         seed=1234,
         testcase_name=f'_test_uniform_grad: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, x64={x64}')
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1]
  )
  def test_uniform_grad(self, shape, transpose, outdim_parallel, prob, seed=None, x64=False):
    print(f'_test_uniform_grad: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random(shape[0] if transpose else shape[1]) < 0.1
    events = bm.as_jax(events)
    events = events.astype(float)

    f1 = jax.grad(
      lambda e: bl.jitconn_ops.event_matvec_prob_conn_uniform_weight(
        e,
        w_low=0.,
        w_high=1.,
        conn_prob=prob,
        shape=shape,
        seed=seed,
        outdim_parallel=outdim_parallel,
        transpose=transpose).sum()
    )

    r1 = f1(events)
    # print(r1)
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         w_mu=w_mu,
         w_sigma=w_sigma,
         bool_event=bool_event,
         x64=x64,
         seed=1234,
         testcase_name=f'_test_normal: '
                       f'shape={shape}, '
                       f'transpose={transpose}, '
                       f'outdim_parallel={outdim_parallel}, '
                       f'prob={prob}, '
                       f'w_mu={w_mu}, '
                       f'w_sigma={w_sigma}, '
                       f'bool_event={bool_event}, '
                       f'x64={x64}')
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1, ]
    for w_mu, w_sigma in [(-1., 1.), (0., 0.1), (0., 0.5)]
    for bool_event in [True, False]
  )
  def test_normal(self, shape, transpose, outdim_parallel, prob, w_mu, w_sigma,
                  bool_event=True, seed=None, x64=False):
    print(f'_test_normal: shape = {shape}, '
          f'transpose = {transpose}, outdim_parallel = {outdim_parallel}, prob={prob}, '
          f'w_mu = {w_mu}, w_sigma = {w_sigma}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random(shape[0] if transpose else shape[1]) < 0.1
    events = bm.as_jax(events)
    if not bool_event:
      events = events.astype(float)

    r1 = bl.jitconn_ops.event_matvec_prob_conn_normal_weight(events,
                                                             w_mu=w_mu,
                                                             w_sigma=w_sigma,
                                                             conn_prob=prob,
                                                             shape=shape,
                                                             seed=seed,
                                                             outdim_parallel=outdim_parallel,
                                                             transpose=transpose)

    r2 = bl.jitconn_ops.event_matvec_prob_conn_normal_weight(events,
                                                             w_mu=w_mu,
                                                             w_sigma=w_sigma,
                                                             conn_prob=prob,
                                                             shape=shape,
                                                             seed=seed,
                                                             outdim_parallel=outdim_parallel,
                                                             transpose=transpose)
    self.assertTrue(jnp.allclose(r1, r2))

    r3 = bl.jitconn_ops.event_matvec_prob_conn_normal_weight(events,
                                                             w_mu=w_mu,
                                                             w_sigma=w_sigma,
                                                             conn_prob=prob,
                                                             shape=(shape[1], shape[0]),
                                                             seed=seed,
                                                             outdim_parallel=outdim_parallel,
                                                             transpose=not transpose)
    self.assertTrue(jnp.allclose(r1, r3))

    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         bool_event=bool_event,
         x64=x64,
         seed=1234,
         testcase_name=f'_test_normal_vmap: '
                      f'shape={shape}, '
                      f'transpose={transpose}, '
                      f'outdim_parallel={outdim_parallel}, '
                      f'prob={prob}, '
                      f'bool_event={bool_event}, '
                       f'x64={x64}')
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1]
    for bool_event in [True, False]
  )
  def test_normal_vmap(self, shape, transpose, outdim_parallel, prob,
                       bool_event=True, seed=None, x64=False):
    print(f'_test_normal_vmap: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random((10, shape[0] if transpose else shape[1])) < 0.1
    events = bm.as_jax(events)
    if not bool_event:
      events = events.astype(float)

    f1 = jax.vmap(lambda e: bl.jitconn_ops.event_matvec_prob_conn_normal_weight(e,
                                                                                w_mu=0.,
                                                                                w_sigma=1.,
                                                                                conn_prob=prob,
                                                                                shape=shape,
                                                                                seed=seed,
                                                                                outdim_parallel=outdim_parallel,
                                                                                transpose=transpose))
    r1 = f1(events)
    r2 = f1(events)
    self.assertTrue(jnp.allclose(r1, r2))
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()

  @parameterized.named_parameters(
    dict(shape=shape,
         transpose=transpose,
         outdim_parallel=outdim_parallel,
         prob=prob,
         x64=x64,
         seed=1234,
         testcase_name=f'_test_normal_grad: '
                       f'shape = {shape}, '
                       f'transpose = {transpose}, '
                       f'outdim_parallel = {outdim_parallel}, '
                       f'prob={prob}, x64={x64}')
    for transpose in [True, False]
    for x64 in [True, False]
    for outdim_parallel in [True, False]
    for shape in shapes
    for prob in [0.01, 0.1]
  )
  def test_normal_grad(self, shape, transpose, outdim_parallel, prob, seed=None, x64=False):
    print(f'_test_normal_grad: '
          f'shape = {shape}, '
          f'transpose = {transpose}, '
          f'outdim_parallel = {outdim_parallel}, '
          f'prob={prob}, x64={x64}')
    if x64:
      bm.enable_x64()
    rng = bm.random.RandomState()
    events = rng.random(shape[0] if transpose else shape[1]) < 0.1
    events = bm.as_jax(events)
    events = events.astype(float)

    f1 = jax.grad(
      lambda e: bl.jitconn_ops.event_matvec_prob_conn_normal_weight(
        e,
        w_mu=0.,
        w_sigma=1.,
        conn_prob=prob,
        shape=shape,
        seed=seed,
        outdim_parallel=outdim_parallel,
        transpose=transpose).sum()
    )
    r1 = f1(events)
    # print(r1)
    if x64:
      bm.disable_x64()
    bm.clear_buffer_memory()
