# -*- coding: utf-8 -*-


import unittest

import jax.numpy as jnp
from brainpylib import coo_atomic_prod

import brainpy as bp
import brainpy.math as bm

bp.math.set_platform('cpu')


class TestAtomicProd(unittest.TestCase):
  def test_heter_values1(self):
    bp.math.random.seed(12345)
    size = 200
    post_ids = jnp.arange(size, dtype=jnp.uint32)
    pre_ids = jnp.arange(size, dtype=jnp.uint32)
    sps = bp.math.asarray(bp.math.random.randint(0, 2, size),
                          dtype=bp.math.float_)
    a = coo_atomic_prod(sps.value, post_ids, size, pre_ids)
    print(a)
    self.assertTrue(jnp.array_equal(a, sps.value))

  def test_homo_value1(self):
    size = 200
    value = 2.
    post_ids = jnp.arange(size, dtype=jnp.uint32)
    a = coo_atomic_prod(value, post_ids, size)
    print(a)
    self.assertTrue(jnp.all(a == value))

  def test_homo_fixedpro(self):
    size = 10
    value = 2.
    conn = bp.conn.FixedProb(prob=1, seed=123)
    conn(pre_size=size, post_size=size)
    post_ids = conn.require('post_ids')
    a = coo_atomic_prod(value, bm.as_jax(post_ids), size)
    print(a)

  def test_heter_fixedpro(self):
    size = 10
    value = jnp.ones(size) * 2.
    conn = bp.conn.FixedProb(prob=1, seed=123)
    conn(pre_size=size, post_size=size)
    pre_ids, post_ids = conn.require('pre_ids', 'post_ids')
    a = coo_atomic_prod(value, bm.as_jax(post_ids), size, bm.as_jax(pre_ids))
    print(a)
